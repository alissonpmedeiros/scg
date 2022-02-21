import json, asyncio
from flask import Flask
from vr_controller import VrController
from encoder import JsonEncoder

app = Flask(__name__)
COUNT = 0

MIGRATION_ALGORITHMS = 1
VR_USERS = VrController.load_vr_users()

FILE_NAME='service_workloads.json'
FILE_DIRECTORY='/home/ubuntu/scg/workloads/'

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
        JsonEncoder.encoder(VR_USERS, FILE_DIRECTORY, FILE_NAME)
        COUNT = 0
    await check_requests()
    return json.dumps({'status': True}), 200, {'ContentType':'application/json'} 


if __name__ == '__main__':
    app.run(host="0.0.0.0")
    