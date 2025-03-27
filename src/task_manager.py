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
        asyncio.create_task(self.monitor_schedule())

    async def monitor_schedule(self) -> None:
        """定期的にスケジュールを確認し、タスクを実行"""
        while self.running:
            now = time.time()
            if self.global_schedule and self.global_schedule[0].time_start <= now:
                task = self.global_schedule.popleft()
                await self.run_task(task)
            await asyncio.sleep(0.5)

    async def run_task(self, task: Task) -> None:
        """タスクを実行"""
        logger.info(f"Executing task: {task.id}, Nodes: {task.pair}, Timeout: {task.timeout} seconds")
        
        for op in task.device_operations:
            grpc_addr = self.config.participants.get(op.node, "localhost:50051")
            logger.info(f"Sending request to node: {op.node}, gRPC address: {grpc_addr}")

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
                logger.error(f"Error executing operation for node {op.node}: {e}")
                op.success = False
        
        all_success = all(op.success for op in task.device_operations)

        logger.info(f"Task {task.id} completed with status: {all_success}")

    async def schedule_task(self, task: Task) -> None:
        """タスクをスケジュールし、完了を待つ"""
        self.global_schedule.append(task)
        logger.info(f"Task scheduled: {task}")
        logger.info(f"global schedule: {self.global_schedule}")
        
