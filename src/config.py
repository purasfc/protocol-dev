from enum import StrEnum, auto
import typing
import logging
import yaml

from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger("config")

class DeviceType(StrEnum):
    THORLABS_K10CR1M = "thorlabs_k10cr1m"
    THORLABS_OSW1310E = "thorlabs_osw1310e"
    THORLABS_KBD101 = "thorlabs_kbd101"
    OZOPTICS_650M = "ozoptics_650m"
    MULTIHARP_160 = "multiharp_160"


class SwitchConfig(StrEnum):
    BAR = auto()
    CROSS = auto()


class DeviceConfig(BaseModel):
    """this class will be handed to pnpq"""
    serial_number: str | None = Field(default=None)
    serial_port: str | None = Field(default=None)
    net_address: str | None = Field(default=None)
    net_port: str | None = Field(default=None)
    name: str
    device_type: DeviceType
    calibration_offset: float = Field(default=0.0)
    stub: bool = Field(default=False)
    
    
class Config(BaseModel):
    node_name: str
    node_address: str
    grpc_server_address: str = Field(default="[::]:50051")
    participants: dict[str, str] = Field(default=None)
    devices: list[DeviceConfig]


def load_config(input_file: typing.TextIO) -> Config:
    data = yaml.safe_load(input_file)
    logger.info(f"Loaded data: {data}")
    if not data:
        raise ValueError("Loaded data is empty or invalid")

    return Config(**data)
