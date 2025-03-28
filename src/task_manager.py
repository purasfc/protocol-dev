import random
import asyncio
import time
import grpc
import uuid
import logging
from collections import deque
from typing import Deque
import grpc.aio
from protocol_pb2 import LinkEstablishRequest, LinkEstablishResponse, ExecuteDeviceOperationRequest
from protocol_pb2_grpc import L1NotificationStub
from task import Task, OperationTask
from config import Config

logger = logging.getLogger("layer2")

class Layer2TaskManager:
    def __init__(self, config: Config):
        self.config = config
        self.global_schedule: Deque[Task] = deque()
        self.running = True
        self.task_events: dict[str,asyncio.Event] = {}
        self.task_results: dict[str, LinkEstablishResponse] = {}
        asyncio.create_task(self.monitor_schedule())

    async def monitor_schedule(self) -> None:
        """定期的にスケジュールを確認し、タスクを実行"""
        while self.running:
            now = time.time()
            if self.global_schedule and self.global_schedule[0].time_start <= now:
                task = self.global_schedule.popleft()
                await self.run_task(task)
            await asyncio.sleep(0.5)

    async def run_task(self, task: Task) -> LinkEstablishResponse:
        """タスクを実行"""
        logger.info(f"Executing task: {task.id}, Nodes: {task.pair}, Timeout: {task.timeout} seconds")
        
        async def execute_operation(op):
            
            grpc_addr = self.config.participants.get(op.target_node, "localhost:50051")
            logger.info(f"Sending request to node: {op.target_node}, gRPC address: {grpc_addr}")

            try:
                channel = grpc.aio.insecure_channel(grpc_addr)
            
                stub = L1NotificationStub(channel)

                response = await stub.ExecuteDeviceOperation(
                    ExecuteDeviceOperationRequest(
                        device_setting="test setting"
                    )
                )
                op.success = response.success  
            except Exception as e:
                logger.error(f"Error executing operation for node {op.target_node}: {e}")
                op.success = False
        
        await asyncio.gather(*(execute_operation(op) for op in task.device_operations))
        
        all_success = all(op.success for op in task.device_operations)

        logger.info(f"Task {task.id} completed with status: {all_success}")
        
        
        initiator = task.pair[0]
        responder = task.pair[1]
        
        start_time = time.time()
        
        
        logger.info(f"Response values - task_id: {task.id}, initiator: {initiator}, responder: {responder}")

        while time.time() - start_time < task.timeout:
            # すべてのタスクのsuccessがTrueかどうかをチェック
            if all(op.success for op in task.device_operations):
                success = True
                response = LinkEstablishResponse(
                    task_id=task.id,
                    link_initiator_address=initiator,
                    link_responder_address=responder,
                    accept=success,
                    message="Link Established"
                )
                break
            await asyncio.sleep(0.5)  # 0.5秒ごとにチェック
            
        else:    
            success = False
            response = LinkEstablishResponse(
                task_id=task.id,
                link_initiator_address=initiator,
                link_responder_address=responder,
                accept=success,
                message="execution timed out or device operation did not succeed"
            )
        
        self.task_results[task.id] = response
        
        if task.id in self.task_events:
            self.task_events[task.id].set()

    async def schedule_task(self, task: Task) -> None:
        """タスクをスケジュールし、完了を待つ"""
        
        self.global_schedule.append(task)
        self.task_events[task.id] = asyncio.Event()
        
        logger.info(f"Task scheduled: {task}")
        logger.info(f"global schedule: {self.global_schedule}")
        
        await self.task_events[task.id].wait()
        
        response = self.task_results.pop(task.id)
        
        if response is None:
            return LinkEstablishResponse(
                task_id=task.id,
                link_initiator_address=task.pair[0],
                link_responder_address=task.pair[1],
                accept=False,
                message="Task result missing"
            )
        
        return response
        
        
