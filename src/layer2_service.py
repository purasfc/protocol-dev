import asyncio
from protocol_pb2 import (
    LinkEstablishResponse,
    LinkEstablishRequest,
    ExecuteDeviceOperationRequest,
    ExecuteDeviceOperationResponse)
import time
import grpc
from protocol_pb2_grpc import L2ServiceServicer, L1NotificationStub
from task import (
    Task,
    OperationTask,
)
from task_manager import Layer2TaskManager
from collections import deque
from typing import Deque
import logging
import uuid
import random
import sys

from config import Config



logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    stream=sys.stdout,
    force=True
)

logger = logging.getLogger("layer2")


grpc_logger = logging.getLogger('grpc')
grpc_logger.setLevel(logging.DEBUG)

class Layer2Service(L2ServiceServicer):
    def __init__(self, config: Config):
        self.task_manager = Layer2TaskManager(config)
        self.node_schedules: dict[str, Deque[OperationTask]] = {
            "nodeA": deque(),
            "nodeB": deque(),
            "nodeC": deque(),
            "bsa": deque()
        }

    async def LinkEstablish(self, request, context) -> LinkEstablishResponse:
        """タスクをスケジュールし、完了を待つ"""
        return await self.schedule(request, context)

    async def schedule(self, request: LinkEstablishRequest, context) -> LinkEstablishResponse:
        """タスクを `Layer2TaskManager` に渡して、完了するまで待つ"""
        initiator = request.link_initiator_address.strip().replace(',', '')
        responder = request.link_responder_address.strip().replace(',', '')

        start_time = time.time()
        task_id = str(uuid.uuid4())
        
        if initiator not in self.node_schedules:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid initiator: {initiator}")
            return LinkEstablishResponse(
                task_id=task_id,
                link_initiator_address=initiator,
                link_responder_address=responder,
                accept=False,
                message="Invalid initiator"
            )

        initiator_operation_task = OperationTask(
            id=task_id,
            target_node=responder,
            start_time=start_time,
            end_time=start_time + 3,
            success=False
        )

        responder_operation_task = OperationTask(
            id=task_id,
            target_node=initiator,
            start_time=start_time,
            end_time=start_time + 3,
            success=False
        )
        
        
        task = Task(
            id=task_id,
            time_start=start_time,
            # randomly set timeout
            timeout=random.randint(9, 12),
            pair=[initiator, responder],
            device_operations=[initiator_operation_task, responder_operation_task]
        )

        response =  await self.task_manager.schedule_task(task)
        
        return response
        