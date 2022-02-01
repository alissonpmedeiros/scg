
# SCG approach description
This repository describes the technology stack setup used by SCG.

---

## ONOS SDN controller setup

ONOS sdn controller is used to provide the mobility connectivity automation for SCG. 

1. tutorial: ```https://wiki.onosproject.org/display/ONOS/Installing+and+running+ONOS``` 

2. install ONOS openflow apps. To do so, go to http://130.92.70.173:8181/onos/ui/login.html and access *Applications* and install the following apps:

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

The script **mininet_network.py** constains the mininet code to provide the network, including base stations, VR HMD users in mobility, latency between nodes, and bandwidth restrictions. The script also connects to ONOS. 

To run the script use *python2*: ```sudo python2 ~/mininet_network.py```

---

## SCG setup

1. Computing resources (gpu and cpu) for MEC servers and VR services are automatically generated based on the number of base stations and users configured at *mininet_network.py*. 
The data will be stored at **~/mec/mecs.txt** and **~/user/users.txt**. To start the system, runs the following script:

    ``` python3 architecture.py ```. 


2. 
---
