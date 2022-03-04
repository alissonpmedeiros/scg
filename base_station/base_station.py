from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import random


@dataclass_json
@dataclass
class BaseStation:
    id: str
    name: str
    mec_id: str
    links: dict
    wireless_latency: float = field(init=False)
    
    def __post_init__(self):
        self.wireless_latency = round(random.uniform(0.1, 0.3), 2) 