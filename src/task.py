from dataclasses import dataclass, asdict
import json

@dataclass
class OperationTask:
    id: int
    target_node: str
    start_time: int
    end_time: int
    success: bool = False
    
    
    def __repr__(self):
        return json.dumps(asdict(self), indent=2)

@dataclass
class Task:
    id: int
    time_start: int
    timeout: int
    pair: list[str]
    device_operations: list[OperationTask]
    
    def __repr__(self):
        return json.dumps(asdict(self), indent=2)
