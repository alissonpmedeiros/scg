#!/usr/bin/python

from app import app
import threading
import pprint



from mininet.log import info, output, error
from mininet.term import makeTerms, runX11
from mininet.util import ( quietRun, dumpNodeConnections,
                           dumpPorts )




class MininetRestAPI:

    def __init__(self, net):
        self.mn_net = net
        #self.server_api = threading.Thread(target=lambda: app.run(host='0.0.0.0', port='5000', debug=False))
        #self.server_api.daemon = True
        

    def start_server(self):
        #self.server_api.start()
        nodes = self.get_hosts()
        for node in nodes:
            print(node)
            #print(node.cmd('iw dev ' + str(node) + '-wlan0 link'))
            print(node.cmd('iw dev ' + str(node) + '-wlan0 link'))
        #pass

    def stop_server(self):
        #self.server_api.join(timeout=1)
        pass

    
    def get_nodes(self):
        nodes = self.mn_net.get_mn_wifi_nodes()

    def get_node_position(self, node):
        nodes = self.mn_net.get_mn_wifi_nodes()
        for node in nodes:
            print(node.position)

    def get_mobility_params(self):
        nodes = self.mn_net.get_mobility_params()
        print(type(nodes))
        pprint.pprint(nodes)
    
    def get_hosts(self):
        nodes = self.mn_net.hosts + self.mn_net.stations + self.mn_net.sensors + self.mn_net.modems
        return nodes