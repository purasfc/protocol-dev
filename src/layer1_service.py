import random
import asyncio
import grpc
from protocol_pb2 import ExecuteDeviceOperationResponse
from protocol_pb2_grpc import L2ServiceServicer, add_L2ServiceServicer_to_server
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("layer1")

class Layer1Service(L2ServiceServicer):
    async def ExecuteDeviceOperation(self, request, context) -> ExecuteDeviceOperationResponse:
        logger.info(f"request setting: {request.device_setting}")
        logger.info("Executing Device Operation")

        # ランダムな処理時間を非同期で待機
        task_execution_time = random.randint(1, 5)
        logger.info(f"it will take {task_execution_time} seconds")
        await asyncio.sleep(task_execution_time)

        logger.info("execution has done")
        return ExecuteDeviceOperationResponse(
            accept="Operation has done",
            success=True
        )
