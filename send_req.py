import logging
import random
from argparse import ArgumentParser
import grpc
import asyncio
from src.protocol_pb2_grpc import L2ServiceStub
from src.protocol_pb2 import LinkEstablishRequest

logging.basicConfig(level=logging.INFO)  # ここでログレベルを設定
logger = logging.getLogger("send_req")

async def send_req(
    initiator: str,
    responder: str
) -> str:
    host: str = "localhost"
    port: str = "50051"
    channel = grpc.aio.insecure_channel(f"{host}:{port}")
    stub = L2ServiceStub(channel)
    
    logger.info(f"initiator: {initiator}, responder: {responder}")
    
    try:
        response = await stub.LinkEstablish(
            LinkEstablishRequest(
                link_initiator_address=initiator,
                link_responder_address=responder
            )
        )
        print(response)
    except Exception as e:
        logger.error(f"Error requesting link establishment: {e}")

if __name__ == "__main__":
    parser = ArgumentParser("CLI client to send request for testbed_node")
    parser.add_argument("initiator", type=str, help="initiator address")
    parser.add_argument("responder", type=str, help="responder address")
    args = parser.parse_args()

    asyncio.run(send_req(initiator=args.initiator, responder=args.responder))