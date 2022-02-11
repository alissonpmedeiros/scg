
# SCG approach description
This repository describes the technology stack setup used by SCG.

---
## Operating system:
1.  Ubuntu server 20 is used for both mininet and onos VMs

---

## ONOS SDN controller setup

ONOS sdn controller is used to provide the mobility connectivity automation for SCG. 

1. tutorial: ```https://wiki.onosproject.org/display/ONOS/Installing+and+running+ONOS``` 
    - ```sudo adduser sdn --system --group```
    - ```sudo apt install openjdk-11-jdk  curl```
    - ```sudo su ```
      ```cat >> /etc/environment <<EOL ```
      ```JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 ```
      ```JRE_HOME=/usr/lib/jvm/java-11-openjdk-amd64/jre ```
      ```EOL ```
    - ```cd /opt ```
    - PS: use the version 2.7. ``` wget -c https://repo1.maven.org/maven2/org/onosproject/onos-releases/2.7.0/onos-2.7.0.tar.gz```
    - ```sudo tar xzf onos-$ONOS_VERSION.tar.gz ```
    - ```sudo mv onos-$ONOS_VERSION onos ```
    - ```/opt/onos/bin/onos-service start ```

2. Addition steps: Running ONOS as a service
    - ```sudo cp /opt/onos/init/onos.initd /etc/init.d/onos ```
 

3. Onos SSH:
    - In case you need to ssh onos: ```ssh -p 8101 onos@ONOS-VM-IP```


4. Install ONOS apps. To do so, go to **http://ONOS-VM-IP:8181/onos/ui/login.html** and access *Applications* and install the following apps:

    - OpenFlow Base Provider
    - OpenFlow Provider Suite
    - OpenFlow Agent
    - Control Message Stats Provider
    - Reactive Forwarding
    - Proxy ARP/NDP
    - LLDP
    - OVSDB host Provider
    - Openflow overlay
    - Mobility
    - Onos legacy GUI if the GUI2 is crashing 


---

## Mininet WiFi setup

Mininet Wifi is used to provide a mobility scenario for VR applications

The script **mininet_network.py** constains the mininet code to provide the network, including base stations, VR HMD users in mobility, latency between nodes, and bandwidth restrictions. The script also connects to ONOS. 

To run the script use *python3*: ```sudo python3 ~/mininet_network.py```

1. Mininet wifi instalation:

    - packages:
        ```sudo apt-get install network-manager```
        ```sudo service stop network-manager```
        ```sudo apt install linux-generic-hwe-20.04```
        ```linux-modules-5.4.0-1030-kvm_5.4.0-1030.31_amd64.deb``` 
        ```linux-image-5.4.0-1030-kvm_5.4.0-1030.31_amd64.deb``` 

    - reboot the OS after installing the packages for wmedium.
    - ```git clone https://github.com/intrig-unicamp/mininet-wifi.git```
    - ```cd mininet-wifi```
    - ```sudo util/install.sh -Wlnfv```

---

## SCG setup

1. Computing resources (gpu and cpu) for MEC servers and VR services are automatically generated based on the number of base stations and users configured at *mininet_network.py*. 
The data will be stored at **~/mec/mecs.txt** and **~/user/users.txt**. To start the system, runs the following script:

2. To start the system, runs the following script:
    - ``` python3 main.py ``` 


3. Every time the script **main.py** runs, we have to delete the *users.txt* file because the VR users will have different MAC addresses. 
---
