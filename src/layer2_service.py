import asyncio
from protocol_pb2 import (
    LinkEstablishResponse,
    LinkEstablishRequest,
    ExecuteDeviceOperationRequest,
    ExecuteDeviceOperationResponse)
import time
import grpc
from protocol_pb2_grpc import L2ServiceServicer, L1NotificationStub
from scheduler import (
    Task,
    OperationTask,
)
from collections import deque
from typing import Deque
import logging
import uuid
import sys
from random import random

from config import Config


# ✅ 明示的にログ設定を適用
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    stream=sys.stdout,
    force=True
)

logger = logging.getLogger("layer2")

# ✅ grpc のロギングも有効化
grpc_logger = logging.getLogger('grpc')
grpc_logger.setLevel(logging.DEBUG)

class Layer2Service(L2ServiceServicer):
    config: Config
    def __init__(self, config: Config):
        self.config = config
        self.global_schedule: Deque[Task] = deque()  
        self.node_schedules: dict[str, Deque[OperationTask]] = {
            "nodeA": deque(),
            "nodeB": deque(),
            "nodeC": deque(),
            "switch": deque()
        }
        self.running = True
        asyncio.create_task(self.monitor_schedule())
    
    async def monitor_schedule(self)-> None:
        while self.running:
            now = time.time()
            while self.global_schedule and self.global_schedule[0].time_start <= now:
                task = self.global_schedule.popleft()
                await self.run_task(task)
            await asyncio.sleep(0.5)
    
    async def run_task(self, task: Task) -> None:
        logger.info(f"Executing task: {task.id}, Nodes: {task.pair}, it takes: {task.timeout} second")
        await asyncio.sleep(task.timeout)
        for op in task.device_operations:
            grpc_addr = self.config.participants[op.node]
            logger.info(f"node: {op.node}, grpc_address:{grpc_addr}")
            channel = grpc.insecure_channel(grpc_addr)
            grpc.channel_ready_future(channel).result(timeout=1)
            stub = L1NotificationStub(channel)
            
            response = stub.ExecuteDeviceOperation(
                ExecuteDeviceOperationRequest(
                    device_setting="test setting"
                )
            )
            op.success = True
        logger.info(f"Task {task.id} completed successfully.")
    
    async def LinkEstablish(self, request, context) -> LinkEstablishResponse:
        return await self.schedule(request, context)
    
    async def schedule(self, request: LinkEstablishRequest, context) -> LinkEstablishResponse:
        
        initiator = request.link_initiator_address.strip().replace(',', '')
        responder = request.link_responder_address.strip().replace(',', '')
        
        logger.info(f"Existing node_schedules keys: {list(self.node_schedules.keys())}")
        logger.info(f"Received initiator: '{initiator}', responder: '{responder}'")

        if initiator not in self.node_schedules:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid initiator: {initiator}")
            return LinkEstablishResponse(
                link_initiator_address=initiator,
                link_responder_address=responder,
                accept=False,
                message="Invalid initiator"
            )

        initiator_schedule = self.node_schedules[initiator]
        responder_schedule = self.node_schedules[responder]

        start_time = max(
            initiator_schedule[-1].end_time if initiator_schedule else 0,
            responder_schedule[-1].end_time if responder_schedule else 0
        ) if initiator_schedule and responder_schedule else time.time()
        
        task_id = str(uuid.uuid4())

        initiator_operation_task = OperationTask(
            id=task_id,
            node=responder,
            start_time=start_time,
            end_time=start_time + 3,
            success=False
        )

        responder_operation_task = OperationTask(
            id=task_id,
            node=initiator,
            start_time=start_time,
            end_time=start_time + 3,
            success=False
        )

        initiator_schedule.append(initiator_operation_task)
        responder_schedule.append(responder_operation_task)

        task = Task(
            id=task_id,
            time_start=start_time,
            timeout=int(random(1,10)),
            pair=[initiator, responder],
            device_operations=[initiator_operation_task, responder_operation_task]
        )

        self.global_schedule.append(task)

        logger.info(f"Task scheduled: {task}")
        logger.info(f"Global queue: {list(self.global_schedule)}")
        logger.info(f"Node schedules: {dict(self.node_schedules)}")
        
        await self.run_task(task)
        success = all(op.success for op in task.device_operations)

        return LinkEstablishResponse(
            link_initiator_address=initiator,
            link_responder_address=responder,
            accept=success,
            message="Link Established" if success else "Task Execution failed"
        )
