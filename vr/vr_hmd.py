import uuid, random
from typing import List
from vr.vr_service import VrService
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class VrHMD:
    """ represents a VR HMD instance """
    ip: str
    mac_address: str
    previous_location: str 
    current_location:  str 
    cpu: int = 0
    gpu: int = 0
    id: str = field(init=False)
    computing_latency: int = field(init=False)
    services_set: List[VrService] = field(default_factory=list, init=False)
    services_ids: List[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.id = str(uuid.uuid4())
        self.computing_latency = round(random.uniform(2, 6), 2)
