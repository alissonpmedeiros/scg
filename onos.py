#!/usr/bin/python3
import requests
from requests.exceptions import HTTPError
from dataclasses import dataclass
from munch import Munch, DefaultMunch
import pprint, time


@dataclass(frozen=True)
class OnosController:
    """ SDN controller representation for ONOS """
    
    server_IP: str = '130.92.70.174'
    OF_port: str = '8181'
    user: str = 'onos'
    password: str = 'rocks' 


    def request(self, resource: str) -> dict:
        """ provides an http request to onos server API """
        
        URL = 'http://' + self.server_IP + ':' + self.OF_port + '/onos/v1/' + resource 
        try: 
            response = requests.get(URL, auth=(self.user, self.password), verify=False)
            result = DefaultMunch.fromDict(response.json())
            return result
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')


    def get_hosts(self) -> dict:
        """ get the list of mininet hosts, including stations and hosts """
        
        resource = 'hosts'
        hosts = self.request(resource)
        return hosts


    def get_host(self, host_IP: str) -> list:
        """ get a specific host info based on its IP""" 
        """
        usage -> host['key']
        during this loop, the following keys are available for each host:
        id, mac, vlan, innerVlan, outerTpid, configured, suspended,
        ipAddresses[0], locations[0]['elementId'] 
        """
        
        hosts = self.get_hosts()
        return [host for host in hosts.hosts if host.ipAddresses[0] == host_IP]
        



    def get_devices(self) -> list:
        """ returns a list of devices, which includes mininet switches and access points """
        
        resource = 'devices'
        devices = self.request(resource)
        devices_list = []

        for device in devices.devices:
            """
            usage -> device['key']
            during this loop, the following keys are available for each device:
            id, chassisId, annotations['datapathDescription']. 
            annotations['datapathDescription'] contains the device name from mininet  
            """

            device_id = device.id
            device_name = device.annotations.datapathDescription
            new_device = Munch ({'id': device_id, 'name': device_name})
            devices_list.append(new_device)
        
        return devices_list


    def get_device(self, device_id: str) -> list:
        """ get a specific device info based on its ID""" 

        devices = self.get_devices()
        print(type(devices))
        return [device for device in devices if device.id == device_id]
        

    def get_links(self) -> list:
        """ returns a list of links, including the source and destination devices and the used ports """

        resource = 'links'
        links = self.request(resource)
        links_list = []
        for link in links.links:
            """
            usage -> link['key']
            during this loop, the following keys are available for each link:
            src['port'], src['device'], dst['port'], dst['device'], state, type. 
            Furthermore, scr = source and dst = destination
            """

            scr_port = link['src']['port']
            scr_device = link['src']['device']
            dst_port = link['dst']['port']
            dst_device = link['dst']['device']

            new_link = {'scr': {'port': scr_port, 'device': scr_device}, 
                        'dst': {'port': dst_port, 'device': dst_device}}
            
            new_link_dict = DefaultMunch.fromDict(new_link)

            links_list.append(new_link_dict)

        return links_list


    def get_link(self, device_id: str) -> list:
        """ get the associated (destination) links to a specific device""" 

        links = self.get_links()
        return [link for link in links if link.scr.device == device_id]


    def get_flows(self) -> dict:
        """ returns the list of flows deployed on the devices"""

        resource = 'flows'
        flows = self.request(resource)
        return flows


    def get_intents(self) -> dict:
        """ returns the list of intents, which are used to manage the network resources (bandwidth, flows)"""

        resource = 'intents'
        intents = self.request(resource)
        return intents


    def get_topology(self) -> list:
        """" builds the topology of the network, containing devices and links """

        devices = self.get_devices()
        topology = []
        for device in devices: 
            device_id = device['id']
            device_links = self.get_link(device_id)
            device['links'] = device_links
            topology.append(device)
        
        return topology
            




'''

if __name__ == '__main__':
    controller = OnosController()
    #x = controller.get_device('of:1000000000000004')
    x = controller.get_link('of:1000000000000002')
    #x = controller.get_links()
    print("\n")
    pprint.pprint(x)
    for link in x:
        print(link.dst.device)
    
'''


if __name__ == '__main__':
    controller = OnosController()
    while True:
     x = controller.get_hosts() 
     pprint.pprint(x)
     time.sleep(1)