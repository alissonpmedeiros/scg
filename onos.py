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

    @classmethod
    def request(self, resource: str) -> dict:
        """ provides an http request to onos server API """
        
        URL = 'http://' + self.server_IP + ':' + self.OF_port + '/onos/v1/' + resource 
        time.sleep(0.001)        
        try: 
            response = requests.get(URL, auth=(self.user, self.password), verify=False)
            result = DefaultMunch.fromDict(response.json())
            return result
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

    @staticmethod
    def get_hosts() -> dict:
        """ get the list of mininet hosts, including stations and hosts """
        
        resource = 'hosts'
        hosts = OnosController.request(resource)
        return hosts

    @staticmethod
    def get_host(host_IP: str) -> list:
        """ get a specific host info based on its IP""" 
        """
        usage -> host['key']
        during this loop, the following keys are available for each host:
        id, mac, vlan, innerVlan, outerTpid, configured, suspended,
        ipAddresses[0], locations[0]['elementId'] 
        """
        
        hosts = OnosController.get_hosts()
        for host in hosts.hosts:
            if host.ipAddresses[0] == host_IP:
                return host


    @staticmethod
    def get_devices() -> list:
        """ returns a list of devices, which includes mininet switches and access points """
        
        resource = 'devices'
        devices = OnosController.request(resource)
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

    @staticmethod
    def get_device(device_id: str) -> list:
        """ get a specific device info based on its ID""" 

        devices = OnosController.get_devices()
        print(type(devices))
        return [device for device in devices if device.id == device_id]
        
    @staticmethod
    def get_links() -> list:
        """ returns a list of links, including the source and destination devices and the used ports """

        resource = 'links'
        links = OnosController.request(resource)
        links_list = []
        for link in links.links:
            """
            usage -> link['key']
            during this loop, the following keys are available for each link:
            src['port'], src['device'], dst['port'], dst['device'], state, type. 
            Furthermore, src = source and dst = destination
            """

            src_port = link['src']['port']
            src_device = link['src']['device']
            dst_port = link['dst']['port']
            dst_device = link['dst']['device']

            new_link = {'src': {'port': src_port, 'device': src_device}, 
                        'dst': {'port': dst_port, 'device': dst_device}}
            
            new_link_dict = DefaultMunch.fromDict(new_link)

            links_list.append(new_link_dict)

        return links_list

    @staticmethod
    def get_link(device_id: str) -> list:
        """ get the associated (destination) links to a specific device""" 

        links = OnosController.get_links()
        return [link for link in links if link.src.device == device_id]

    @staticmethod
    def get_flows() -> dict:
        """ returns the list of flows deployed on the devices"""

        resource = 'flows'
        flows = OnosController.request(resource)
        return flows

    @staticmethod
    def get_intents() -> dict:
        """ returns the list of intents, which are used to manage the network resources (bandwidth, flows)"""

        resource = 'intents'
        intents = OnosController.request(resource)
        return intents

    @staticmethod
    def get_topology() -> list:
        """" builds the topology of the network, containing devices and links """

        devices = OnosController.get_devices()
        topology = []
        for device in devices: 
            device_id = device['id']
            device_links = OnosController.get_link(device_id)
            device['links'] = device_links
            topology.append(device)
        
        return topology

    @classmethod            
    def delete_hosts(self) -> None:
        """ deletes all hosts """
        hosts = OnosController.get_hosts()  
        for host in hosts['hosts']:
            URL = 'http://' + self.server_IP + ':' + self.OF_port + '/onos/v1/hosts/{}'.format(host.id)
            try: 
                requests.delete(URL, auth=(self.user, self.password), verify=False)
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')

            time.sleep(0.0001)
    
    @classmethod            
    def delete_devices(self) -> None:
        """ deletes all devices """
        devices = OnosController.get_devices()  
        for device in devices:
            URL = 'http://' + self.server_IP + ':' + self.OF_port + '/onos/v1/devices/{}'.format(device.id)
            try: 
                requests.delete(URL, auth=(self.user, self.password), verify=False)
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')

            time.sleep(0.0001)

if __name__=='__main__':
    
    '''
    devices = OnosController.get_devices()
    hosts = OnosController.get_hosts()
    #pprint.pprint(hosts)
    for host in hosts['hosts']:
        pprint.pprint(host)
        a = input()
    '''
    OnosController.delete_devices()
    OnosController.delete_hosts()