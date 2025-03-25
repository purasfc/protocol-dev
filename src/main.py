import asyncio
import logging
import os
import signal
from argparse import ArgumentParser
import daemon
import grpc
from daemon import pidfile
import typing
from enum import StrEnum, auto
from pydantic import BaseModel, Field
import logging
import sys
from concurrent import futures
import time

from protocol_pb2_grpc import add_L2ServiceServicer_to_server, add_L1NotificationServicer_to_server
from layer2_service import Layer2Service
from layer1_service import Layer1Service

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from config import Config, load_config



logging.basicConfig(level=logging.INFO)  # ここでログレベルを設定
logger = logging.getLogger("main")

async def serve(
     config: Config
):
    server = grpc.aio.server()
    if config.node_name == "central_manager":
        # only central manager need L2service
        add_L2ServiceServicer_to_server(Layer2Service(config=config), server)
        add_L1NotificationServicer_to_server(Layer1Service(), server)
    else:
        
        add_L1NotificationServicer_to_server(Layer1Service(), server)
    server_address = config.grpc_server_address
    server.add_insecure_port(server_address)
    await server.start()
    print(f"Server started on port {server_address}...")
    await server.wait_for_termination()
    

def run(): 
    parser = ArgumentParser(
        "testbed_node program",
        usage="start testbed node server",
    )
    parser.add_argument("-c", "--config", type=open, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    
    asyncio.run(serve(config))

if __name__ == "__main__":
    run()
