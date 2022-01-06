
# SCG approach description
This repository describes the technology stack setup used by SCG.

---

## ONOS SDN controller setup

ONOS sdn controller is used to provide the mobility connectivity automation for SCG. 

1. run: ```docker run -t -d -p 8181:8181 -p 8101:8101 -p 5005:5005 -p 830:830 --name onos onosproject/onos:2.7-latest``` 

2. install ONOS openflow apps. To do so, go to http://130.92.70.174:8181/onos/ui/login.html and access *Applications* and install the following apps:

    - OpenFlow Base Provider
    - OpenFlow Provider Suite
    - OpenFlow Agent
    - Control Message Stats Provider
    - Reactive Forwarding
    - Proxy ARP/NDP
    - LLDP
    - OVSDB host Provider
    - Openflow overlay


---

## Mininet WiFi setup

Mininet Wifi is used to provide a mobility scenario for VR applications

The script **network.py** constains the mininet code to provide the network, including base stations, VR HMD users in mobility, latency between nodes, and bandwidth restrictions. The script also connects to ONOS. 

To run the script use *python2*: ```sudo python2 ~/network.py```

---

## SCG setup

1. To generate computing (gpu and cpu) resources for MEC servers and VR services call the method **init_servers()** from class **ScgController**. The data will be stored at **./mec/mecs.txt**:

    ``` python3 architecture.py ```. 


2. 
---
