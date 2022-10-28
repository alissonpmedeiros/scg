#!/usr/bin/python3

""" mininet modules """
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from envbash import load_envbash
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd, ITSLink
from mn_wifi.wmediumdConnector import interference
from mininet.node import Controller, RemoteController, OVSSwitch

""" other modules """
import sys, os, time
import threading, signal, sys, json, random, os

""" controller modules """
from .. controllers import config_controller


""" VARIABLES """
# network variables
NET = Mininet_wifi(switch=OVSSwitch, waitConnected=True)

# configuration variables
CONFIG = config_controller.ConfigController.get_config()
load_envbash('{}{}'.format(CONFIG['ONOS']['FILE_DIR'], CONFIG['ONOS']['FILE']))

# HMDs and Base station simulation parameters
BS_SET = []
HMDS_SET = []
HMDS = CONFIG['NETWORK']['HMDS']
NET_GRAPH_DIMENSION = CONFIG['NETWORK']['NET_GRAPH_DIMENSION']


#generates a random mac whenever this lambda function is called
random_mac = lambda : ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])

def remove_config_files():
    """ removes configuration files """
    
    data_dir = CONFIG['SYSTEM']['DATA_DIR']
    mec_file = CONFIG['SYSTEM']['MEC_FILE']
    bs_file = CONFIG['SYSTEM']['BS_FILE']
    user_file = CONFIG['SYSTEM']['HMDS_FILE']
    
    if os.path.exists('{}{}'.format(data_dir, mec_file)):
        print(f'*** Removing file at {mec_file} ***')
        os.remove('{}{}'.format(data_dir, mec_file))
    
    if os.path.exists('{}{}'.format(data_dir, bs_file)):
        print(f'*** Removing file at {bs_file} ***')
        os.remove('{}{}'.format(data_dir, bs_file))
    
    if os.path.exists('{}{}'.format(data_dir, user_file)):
        print(f'*** Removing file at {user_file} ***')
        os.remove('{}{}'.format(data_dir, user_file))    
    


def signal_handler(sig, frame):
    """ detects Ctrl+C action"""

    print('\n\nYou pressed Ctrl+C!\n\n')
    info("*** Stopping network\n")
    NET.stop()
    info("*** Cleaning mininet-wifi env.\n")
    time.sleep(2)
    cmd = 'sudo mn -c'
    os.system(cmd)
    sys.exit(0)

def remove_link(data, id, edge_value):
    """ removes a link from an edge link """
    
    for node in data:
        if node['id'] == edge_value:
            index = node['edges'].index(id)
            del node['edges'][index]
            break
      
def load_topology():
    """ loads network topology from network configuration file """
    '''
    network_config = DecoderController.decode_net_config_file()
    return network_config
    '''
    network_file_name = CONFIG['NETWORK']['NETWORK_FILE']
    network_file_dir =  CONFIG['NETWORK']['NETWORK_FILE_DIR']
    
    with open('{}{}'.format(network_file_dir, network_file_name)) as json_file:
        data = json.load(json_file)
        #remove_duplicated_links(data)
        return data 

def set_hmd_range_color(hmd_set: dict):
    for hmd in hmd_set:
         hmd.set_circle_color('r')  # for red color


def add_hmds():
    info("*** Adding HMDs nodes\n")
    network_adress = 0
    host_adress = 1
    
    for i in range(1, HMDS+1):    
        hmd_id = 'HMD{}'.format(i)
        hmd_ip = '10.0.{}.{}/16'.format(network_adress, host_adress)
        hmd_mac = random_mac()
        hmd_range = 100 # antenna gain in meters
        hmd_min_velicity = CONFIG['NETWORK']['HMD_MIN_VELOCITY']
        hmd_max_velocity = CONFIG['NETWORK']['HMD_MAX_VELOCITY']
        
        bs = NET.addStation(
            hmd_id, 
            mac=hmd_mac, 
            ip=hmd_ip, 
            active_scan=1, 
            range=hmd_range, 
            max_y=NET_GRAPH_DIMENSION, 
            max_x=NET_GRAPH_DIMENSION, 
            min_v=hmd_min_velicity,
            max_v=hmd_max_velocity
        )
        
        HMDS_SET.append(bs)    

        host_adress += 1

        if host_adress == 256:
            network_adress += 1
            host_adress = 0

        print('HMD: {}'.format(i))
    
def add_base_stations(topology_data):
    info("*** Adding base stations nodes\n")
    for node in topology_data:
        bs_id = 'BS' + str(node['id'])
        bs_ssid = 'ssid-bs' + str(node['id'])
        bs_x_position = str(node['position'][0] * NET_GRAPH_DIMENSION) 
        bs_y_position = str(node['position'][1] * NET_GRAPH_DIMENSION)
        bs_position = '{},{},0'.format(bs_x_position, bs_y_position)
        bs_channel = CONFIG['NETWORK']['BS_CHANNEL']
        bs_mode = CONFIG['NETWORK']['BS_MODE']
        bs_range = CONFIG['NETWORK']['BS_RANGE']
        bs_tx_power = CONFIG['NETWORK']['BS_TX_POWER']
        
        bs = NET.addAccessPoint(
            bs_id, ssid=bs_ssid, 
            channel=bs_channel, 
            mode=bs_mode, 
            txpower=bs_tx_power, 
            range=bs_range, 
            position=bs_position
        )
        
        BS_SET.append(bs)
    
def create_bs_links(topology_data):    
    info("*** Creating links\n")
    for node in topology_data:
        print(node.get('id'))
        #print('\n')
        node_id = node['id']
        for edge in node['edges']:
            NET.addLink(BS_SET[node_id], BS_SET[edge])
            #print(f'LINK: {BS_SET[node_id]} -> {BS_SET[edge]}')
        #a = input('')
        
def get_sdn_controller():
    info("*** Starting ONOS controller\n")
    controller_ip = str(os.environ[CONFIG['ONOS']['IP']])
    controller_port = CONFIG['SDN']['PORT']
    controller_protocols = CONFIG['SDN']['PROTOCOLS']
    controller = NET.addController(
        'c1', 
        controller=RemoteController,
        ip=controller_ip, 
        port=controller_port,
        protocols = controller_protocols
    )
    return controller
    
def config_ovs_switches(controller):
    i = 0
    for bs in BS_SET:
        bs.start([controller])
        """ forcing ovs switches to use OpenFlow 13 """
        os.system('ovs-vsctl set bridge BS{} protocols=OpenFlow13'.format(i))
        i+=1

def ping_nodes():
    """ runs the ping.sh script for each node ping all other nodes  """
    while True:
        for user in HMDS_SET:
            #print(user.cmd( 'nohup ./scg/ping.sh {} &'.format(vr_users)))
            #print(user.cmd( './scg/ping.sh {} &'.format(vr_users)))
            p1 = user.popen( '/home/ubuntu/scg/network/ping.sh {} &'.format(HMDS))
            p1.terminate()

def topology(args):
    """ builds the network topology """
    info("*** Creating network\n")
    topology_data = load_topology() 
    
    add_hmds()
    add_base_stations(topology_data)
    sdn_controller = get_sdn_controller()

    info("*** Configuring propagation model\n")
    NET.setPropagationModel(model="logDistance", exp=5)

    info("*** Configuring wifi nodes\n")
    NET.configureWifiNodes()

    create_bs_links(topology_data)
            
    info("*** Configuring mobility model\n")
    NET.setMobilityModel(time=0, model='RandomDirection', seed=20, AC='ssf')

    #info("""*** Starting the graph interface\n""")
    #NET.plotGraph(max_x=NET_GRAPH_DIMENSION, max_y=NET_GRAPH_DIMENSION) 
    
    info("*** Starting network\n")
    NET.build()
    sdn_controller.start()
    
    config_ovs_switches(sdn_controller)

    info("*** Running CLI\n")
    CLI_THREAD = threading.Thread(target=lambda: CLI(NET))
    CLI_THREAD.daemon = True
    
    set_hmd_range_color(HMDS_SET)
    ping_nodes()

    #CLI(net)
    
#initializing signal handler function
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    remove_config_files()
    setLogLevel('info')
    topology(sys.argv)
    
