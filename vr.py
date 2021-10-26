import uuid

class AppWorkload:
    def __init__(self):
        pass


class VrService:
    def __init__(self):
        pass

class VrApp:
    def __init__(self):
        self.id = uuid.uuid4()
        self.services=[]
    
    def add_service(self, service: VrService):
        pass


class HMD:
    def __init__(self):
        self.cpu = 0
        self.gpu = 0





