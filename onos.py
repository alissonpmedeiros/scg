#!/usr/bin/python3

import requests
from requests.exceptions import HTTPError
import pprint




class OnosController:
    def __init__(self):
        self.server_IP = '130.92.70.174'
        self.OF_port = '8181'
        self.user = 'onos'
        self.password = 'rocks' 


    def request(self, resource: str):
        URL = 'http://' + self.server_IP + ':' + self.OF_port + '/onos/v1/' + resource 
        try: 
            response = requests.get(URL, auth=(self.user, self.password), verify=False)
            return response.json()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')


    def get_hosts(self):
        resource = 'hosts'
        hosts = self.request(resource)
        return hosts


    def get_host(self, host_IP: str):
        hosts = self.get_hosts()
        for host in hosts['hosts']:
            '''
            usage -> host['key']
            during this loop, the following keys are available for each host:
            id, mac, vlan, innerVlan, outerTpid, configured, suspended,
            ipAddresses[0], locations[0]['elementId'] 
            '''
            if host['ipAddresses'][0] == host_IP:
                print(host)
                return host

        print('Host with ip ' + host_IP + ' not found')
        return None

    def get_devices(self):
        # this function returns a list of devices, where each one of them is a dict object
        resource = 'devices'
        devices = self.request(resource)
        devices_list = []

        for device in devices['devices']:
            '''
            usage -> device['key']
            during this loop, the following keys are available for each device:
            id, chassisId, annotations['datapathDescription']. 
            annotations['datapathDescription'] contains the device name from mininet  
            '''
            device_id = device['id']
            device_name = device['annotations']['datapathDescription']
            new_device = {'id': device_id, 'name': device_name}
            devices_list.append(new_device)
        
        return devices_list


    def get_device(self, device_id: str):
        devices = self.get_devices()
        for device in devices:
            if device['id'] == device_id:
                print(device)
                return device
        return None    


    def get_links(self):
        # this function returns a list of links, where each one of them is a dict object
        resource = 'links'
        links = self.request(resource)
        links_list = []

        for link in links['links']:
            '''
            usage -> link['key']
            during this loop, the following keys are available for each link:
            src['port'], src['device'], dst['port'], dst['device'], state, type. 
            Furthermore, scr = source and dst = destination
            '''
            scr_port = link['src']['port']
            scr_device = link['src']['device']
            dst_port = link['dst']['port']
            dst_device = link['dst']['device']

            new_link = {'scr': {'port': scr_port, 'device': scr_device}, 
                        'dst': {'port': dst_port, 'device': dst_device}}

            links_list.append(new_link)

        return links_list


    def get_link(self, node_id: str):
        links = self.get_links()
        device_links = []
        for link in links:
            if link['scr']['device'] == node_id:
                device_links.append(link)
        
        return device_links


    def get_flows(self):
        resource = 'flows'
        flows = self.request(resource)
        return flows


    def get_intents(self):
        resource = 'intents'
        intents = self.request(resource)
        return intents


    def get_topology(self):
        # this function builds the topology of the network, containing devices and links
        devices = self.get_devices()
        topology = []
        for device in devices: 
            device_id = device['id']
            device_links = self.get_link(device_id)
            device['links'] = device_links
            topology.append(device)
        
        return topology
            




if __name__ == '__main__':
    controller = OnosController()
    x = controller.get_topology()
    pprint.pprint(x)