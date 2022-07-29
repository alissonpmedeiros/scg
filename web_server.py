import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.vr import VrHMD 

""" controller modules """
from controllers import vr_controller as vr
from controllers import json_controller as jsonc
from controllers import config_controller as config

""" other modules """
import json, asyncio
from flask import Flask, abort, request
from typing import List

app = Flask(__name__)


CONFIG = config.ConfigController.get_config()
 

MIGRATION_ALGORITHMS = CONFIG['MIGRATION']['ALGORITHMS']
data_dir = CONFIG['SYSTEM']['DATA_DIR']
users_file = CONFIG['SYSTEM']['USERS_FILE']
vr_users = jsonc.DecoderController.decoding_to_dict(data_dir=data_dir, file_name=users_file)
requests_count = 0


def changing_workloads(vr_users: List['VrHMD']):
    """changing service quotas for vr services"""
    print('*** GENERATING WORKLOADS ***')
    for user in vr_users:
            for service in user.services_set:
                vr.VrController.change_quota(service)
    
async def check_requests():
    """async function to control the number of requests untill response to all requests"""
    while requests_count % MIGRATION_ALGORITHMS >= 1:
        await asyncio.sleep(0.00001)
    return 

trusted_ips = ('127.0.0.1', '192.168.116.14')

@app.before_request
def limit_remote_addr():
    if request.remote_addr not in trusted_ips:
        abort(404)  # Not Found

@app.route('/')
async def index():
    changing_workloads(vr_users)    
    global requests_count
    requests_count +=1
    await check_requests()
    if requests_count == MIGRATION_ALGORITHMS:
        requests_count = 0
    return json.dumps({'users': vr_users}), 200, {'ContentType':'application/json'} 


if __name__ == '__main__':
    app.run(host="0.0.0.0")
  