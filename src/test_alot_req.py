import logging
import random
import grpc
import asyncio
from protocol_pb2_grpc import L2ServiceStub
from protocol_pb2 import LinkEstablishRequest

logging.basicConfig(level=logging.INFO)  # ここでログレベルを設定
logger = logging.getLogger("send_req")

# ランダムに選択するノードのリスト
NODES = ["nodeA", "nodeB", "nodeC"]

async def send_req(initiator: str, responder: str) -> None:
    """非同期でリクエストを送信する関数"""
    host: str = "localhost"
    port: str = "50051"
    channel = grpc.insecure_channel(f"{host}:{port}")
    grpc.channel_ready_future(channel).result(timeout=1)
    stub = L2ServiceStub(channel)
    
    try:
        response = await asyncio.to_thread(
            stub.LinkEstablish,
            LinkEstablishRequest(
                link_initiator_address=initiator,
                link_responder_address=responder
            )
        )
        logger.info(f"Received response: {response}")
    except grpc.RpcError as e:
        logger.error(f"RPC failed: {e}")

async def send_multiple_requests(request_count: int) -> None:
    """指定された回数だけ非同期でランダムなリクエストを送信する"""
    tasks = []
    for _ in range(request_count):
        initiator = random.choice(NODES)
        responder = random.choice([node for node in NODES if node != initiator])  # 同じノードを選ばない
        logger.info(f"Scheduling request with initiator: {initiator} and responder: {responder}")
        tasks.append(send_req(initiator, responder))
    
    # タスクを非同期で実行
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    request_count = 10  # 送信するリクエストの数
    asyncio.run(send_multiple_requests(request_count))
