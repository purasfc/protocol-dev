import asyncio
from protocol_pb2 import ExecuteDeviceOperationResponse
import time
import grpc
from protocol_pb2_grpc import L2ServiceServicer
from scheduler import (
    Task,
    OperationTask,
)
from collections import deque
from typing import Deque
import logging
import uuid
import sys
from config import Config

logging.basicConfig(level=logging.INFO)  # ここでログレベルを設定
logger = logging.getLogger("layer1")

class Layer1Service(L2ServiceServicer):
    def ExecuteDeviceOperation(self, request, context) -> ExecuteDeviceOperationResponse:
        logger.info("Executing Device Operation")
        return ExecuteDeviceOperationResponse(
            accept="Operation has done"
        )
        