import json, asyncio
from flask import Flask
from vr_controller import VrController

app = Flask(__name__)
COUNT = 0

MIGRATION_ALGORITHMS = 6
VR_USERS = VrController.load_vr_users()

def changing_workloads(vr_users: list):
    """changing service quotas for vr services"""
    print('generating workloads')
    for user in vr_users:
            for service in user.services_set:
                VrController.change_quota(service)
    
async def check_requests():
    """async function to control the number of requests untill response to all requests"""
    while COUNT % MIGRATION_ALGORITHMS >= 1:
        await asyncio.sleep(0.0001)
    return 


@app.route('/')
async def index():
    global COUNT
    COUNT +=1
    if COUNT == MIGRATION_ALGORITHMS:
        changing_workloads(VR_USERS)
        COUNT = 0
    await check_requests()
    return json.dumps({'users': VR_USERS}), 200, {'ContentType':'application/json'} 


if __name__ == '__main__':
    app.run()
    