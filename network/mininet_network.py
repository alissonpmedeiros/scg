#!/usr/bin/python

'Example for Handover'

import sys, os, time

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd, ITSLink
from mn_wifi.wmediumdConnector import interference
from mininet.node import Controller, RemoteController, OVSSwitch
import threading, signal, sys, json, pickle
from pprint import pprint as pprint


net = Mininet_wifi(switch=OVSSwitch, waitConnected=True)

vr_users = 5
vr_users_set = []
plot_dimensions = 240

def signal_handler(sig, frame):
    print('\n\nYou pressed Ctrl+C!\n\n')
    info("*** Stopping network\n")
    net.stop()
    info("*** Cleaning mininet-wifi env.\n")
    time.sleep(2)
    cmd = 'sudo mn -c'
    os.system(cmd)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def load_topology():
    files_directory =  '/home/ubuntu/scg/network/'
    file_name = 'network_graph.json'
    with open('{}{}'.format(files_directory, file_name)) as json_file:
        data = json.load(json_file)
        #pprint(data)
        return data 

def topology(args):
    info("*** Creating network\n")

    info("*** Creating nodes\n")
    for i in range(0, vr_users):

        sta_args = dict()
        if '-s' in args:
            sta_args['position'] = '{},{},0'.format(plot_dimensions/2, plot_dimensions/2)

        sta = net.addStation('HMD{}'.format(i), mac='00:00:00:00:00:0{}'.format(i), active_scan=1, **sta_args)

        vr_users_set.append(sta)    
        print('user: {}'.format(i+1))

    aps_set = []
    bs_cont = 0
    info("*** Adding base stations nodes\n")
    for i in range(30, plot_dimensions, 60):
        for j in range(20, plot_dimensions+40, 40):
            bs_cont+= 1
            ap = net.addAccessPoint('BS{}'.format(bs_cont), ssid='ssid-ap{}'.format(bs_cont), channel='1', position='{},{},0'.format(j, i))
            aps_set.append(ap)
            print('bs: {}'.format(bs_cont))

    

    info("*** Starting ONOS controller\n")
    c1 = net.addController('c1', controller=RemoteController,ip='172.17.0.2',port=6653,protocols="OpenFlow13")

    net.setPropagationModel(model="logDistance", exp=5)

    info("*** Configuring wifi nodes\n")

    net.configureWifiNodes()

    info("*** Creating links\n")
    '''
    for i in range(1, len(aps_set)):
        net.addLink(aps_set[i-1], aps_set[i])
    '''
    data = load_topology()    
    for i in range(1, len(aps_set)):
        id = data[i-1].get('id')
        edges = data[i-1].get('edges')
        for edge in edges:
            net.addLink(aps_set[i-1], aps_set[edge])

    net.setMobilityModel(time=0, model='RandomDirection',
                         max_x=plot_dimensions, max_y=plot_dimensions, seed=20, AC='ssf', min_v=1, max_v=1)

    
    
    info("*** Starting network\n")
    net.build()
    c1.start()
    for ap in aps_set:
        ap.start([c1])


    info("*** Running CLI\n")
    CLI_THREAD = threading.Thread(target=lambda: CLI(net))
    CLI_THREAD.daemon = True

    
    
    """ runs the ping.sh script for each node ping all other nodes  """
    while True:
        for user in vr_users_set:
            time.sleep(0.01)
            #print(user.cmd( 'nohup ./scg/ping.sh {} &'.format(vr_users)))
            #print(user.cmd( './scg/ping.sh {} &'.format(vr_users)))
            p1 = user.popen( '/home/ubuntu/scg/network/ping.sh {} &'.format(vr_users))
            print(p1)
            p1.terminate()

  
    #CLI(net)
    
    



if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
    