""" other modules """
import random
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class BaseStation:
    """represents a base station"""
    
    name: str
    mec_id: str
    links: dict
    wireless_latency: float = field(default_factory=float, init=True)
    
    def __post_init__(self):
        self.wireless_latency = round(random.uniform(0.1, 0.3), 2) 
    
   