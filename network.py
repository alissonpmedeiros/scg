#!/usr/bin/python

'Example for Handover'

import sys, os, time

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd, ITSLink
from mn_wifi.wmediumdConnector import interference
from mininet.node import Controller, RemoteController, OVSSwitch
from API import MininetRestAPI
import threading



def topology(args):
    info("*** Creating network\n")
    #net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)
    #net = Mininet_wifi(ac_method='ssf')
    net = Mininet_wifi(switch=OVSSwitch, waitConnected=True)
    

    info("*** Creating nodes\n")
    sta1_args, sta2_args = dict(), dict()
    if '-s' in args:
        sta1_args['position'], sta2_args['position'] = '20,30,0', '60,30,0'

    sta1 = net.addStation('sta1', mac='00:00:00:00:00:01', active_scan=1, **sta1_args)
    sta2 = net.addStation('sta2', mac='00:00:00:00:00:02', active_scan=1, **sta2_args)

    ap1 = net.addAccessPoint('ap1', ssid='ssid-ap1', channel='1', position='20,30,0')
    ap2 = net.addAccessPoint('ap2', ssid='ssid-ap2', channel='6', position='60,30,0')
    ap3 = net.addAccessPoint('ap3', ssid='ssid-ap3', channel='3', position='100,30,0')

    ap4 = net.addAccessPoint('ap4', ssid='ssid-ap4', channel='1', position='20,90,0')
    ap5 = net.addAccessPoint('ap5', ssid='ssid-ap5', channel='6', position='60,90,0')
    ap6 = net.addAccessPoint('ap6', ssid='ssid-ap6', channel='3', position='100,90,0')
    

    #c1 = net.addController('c1')
    info("\n\n**** Starting ONOS controller\n")
    c1 = net.addController('c1', controller=RemoteController,ip='172.17.0.2',port=6653,protocols="OpenFlow13")

    net.setPropagationModel(model="logDistance", exp=5)

    info("** Configuring wifi nodes\n")
    #cwd = os.getcwd()
    #print("Current working directory: {0}".format(cwd))

    net.configureWifiNodes()

    info("*** Creating links\n")
    net.addLink(ap1, ap2)
    net.addLink(ap2, ap3)
    net.addLink(ap3, ap4)
    net.addLink(ap4, ap5)
    net.addLink(ap5, ap6)
    #net.addLink(ap1, sta1)
    #net.addLink(ap2, sta2)

    if '-p' not in args:
        net.plotGraph(max_x=1000, max_y=1000)


    #net.setMobilityModel(time=0, model='RandomWayPoint', constantDistance=1, constantVelocity=1,
    #                     max_x=150, max_y=150, seed=20)
    
    net.setMobilityModel(time=0, model='RandomDirection',
                         max_x=120, max_y=120, seed=20, AC='llf')

    
    
    info("*** Starting network\n")
    net.build()
    c1.start()
    ap1.start([c1])
    ap2.start([c1])
    ap3.start([c1])
    ap4.start([c1])
    ap5.start([c1])
    ap6.start([c1])

    mininet_rest = MininetRestAPI(net)


    info("*** Running CLI\n")
    #CLI_THREAD = threading.Thread(target=lambda: CLI(net))
    #CLI_THREAD.daemon = True
    CLI(net)
    
    #print(sta1.cmd('iw dev ' + str('sta1') + '-wlan0 link'))

    #info("*** Starting flask server\n")
    #mininet_rest.start_server()
    
    #a = raw_input("type enter to close the program!")
    

    #info("*** Stopping flask server\n")
    #mininet_rest.stop_server()

    info("*** Stopping network\n")
    net.stop()

    info("*** Cleaning mininet-wifi env.\n")
    time.sleep(2)
    cmd = 'sudo mn -c'
    os.system(cmd)

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
    