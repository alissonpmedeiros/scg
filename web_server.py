import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.vr import VrHMD 

""" controller modules """
from controllers import vr_controller 
from controllers import json_controller 
from controllers import config_controller 

""" other modules """
import json, asyncio
from flask import Flask, abort, request
from typing import Dict

app = Flask(__name__)


CONFIG = config_controller.ConfigController.get_config()
 

MIGRATION_ALGORITHMS = CONFIG['MIGRATION']['ALGORITHMS']
data_dir = CONFIG['SYSTEM']['DATA_DIR']
hmds_file = CONFIG['SYSTEM']['HMDS_FILE']
hmds_set = json_controller.DecoderController.decoding_to_dict(data_dir, hmds_file)
requests_count = 0


def changing_workloads(hmds_set: Dict[str,'VrHMD']):
    """changing service quotas for vr services"""
    
    print('*** GENERATING WORKLOADS ***')
    for hmd in hmds_set.values():
        for service in hmd.services_set:
            vr_controller.VrController.change_quota(service)
    
async def check_requests():
    """async function to control the number of requests untill response to all requests"""
    while requests_count % MIGRATION_ALGORITHMS >= 1:
        await asyncio.sleep(0.00001)
    return 

def convert_to_json(hmds_set: Dict[str,'VrHMD']):
    """converst the hmds_set to json"""
    
    data_set = {}
    for id, hmd in hmds_set.items():
        data_set[id] = hmd.to_json()
    return data_set

trusted_ips = ('127.0.0.1', '192.168.116.14')

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in trusted_ips:
        abort(404)  # Not Found

@app.route('/')
async def index():
    changing_workloads(hmds_set)    
    global requests_count
    requests_count +=1
    await check_requests()
    if requests_count == MIGRATION_ALGORITHMS:
        requests_count = 0
    
    data_set = convert_to_json(hmds_set)
    return json.dumps({'hmds_set': data_set}), 200, {'ContentType':'application/json'} 


if __name__ == '__main__':
    app.run(host="0.0.0.0")
  