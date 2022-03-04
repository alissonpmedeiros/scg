import json, asyncio
from flask import Flask
from typing import List
from vr.vr_hmd import VrHMD
from vr.vr_controller import VrController

app = Flask(__name__)
COUNT = 0

MIGRATION_ALGORITHMS = 6
VR_USERS = VrController.load_vr_users()


def changing_workloads(vr_users: List[VrHMD]):
    """changing service quotas for vr services"""
    print('*** GENERATING WORKLOADS ***')
    for user in vr_users:
            for service in user.services_set:
                VrController.change_quota(service)
    
async def check_requests():
    """async function to control the number of requests untill response to all requests"""
    while COUNT % MIGRATION_ALGORITHMS >= 1:
        await asyncio.sleep(0.00001)
    return 


@app.route('/')
async def index():
    changing_workloads(VR_USERS)    
    global COUNT
    COUNT +=1
    await check_requests()
    if COUNT == MIGRATION_ALGORITHMS:
        COUNT = 0
    return json.dumps({'users': VR_USERS}), 200, {'ContentType':'application/json'} 


if __name__ == '__main__':
    #app.run(host="0.0.0.0")
    app.run(host="0.0.0.0")
    