import typing
import logging
import yaml

from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger("config")

    
class Config(BaseModel):
    node_name: str
    node_address: str
    grpc_server_address: str = Field(default="[::]:50051")
    participants: dict[str, str] = Field(default=None)
    


def load_config(input_file: typing.TextIO) -> Config:
    data = yaml.safe_load(input_file)
    logger.info(f"Loaded data: {data}")
    if not data:
        raise ValueError("Loaded data is empty or invalid")

    return Config(**data)
