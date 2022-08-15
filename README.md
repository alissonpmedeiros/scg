
# SCG approach description
This repository describes the technology stack setup used by SCG.

---
## Operating system:
1.  Ubuntu server 20 is used for both *mininet* and *ONOS* VMs

2. VMs requirements
    - RAM: 50GB
    - VCPUs: 32
    - Storage: 40G
---

## ONOS SDN controller setup

ONOS sdn controller is used to provide the mobility connectivity automation for SCG. 

1. tutorial: ```https://wiki.onosproject.org/display/ONOS/Installing+and+running+ONOS``` 
    - ```sudo adduser sdn --system --group```
    - ```sudo apt install openjdk-11-jdk  curl```
    - ```sudo su ```
    - ```cat >> /etc/environment <<EOL ```
    - ```JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 ```
    - ```JRE_HOME=/usr/lib/jvm/java-11-openjdk-amd64/jre ```
    - ```EOL ```
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

5. Describe the configuration file!

6. ONOS service should be cleaned whenever a new topology is loaded on Mininet-wifi:  
    - ```sudo /opt/onos27/bin/onos-service clean```

---

## Mininet WiFi setup

Mininet Wifi is used to provide a mobility scenario for VR applications

The script **mininet_network.py** constains the mininet code to provide the network, including base stations, VR HMDs in mobility, latency between nodes, and bandwidth restrictions. The script also connects to ONOS. 

At root directory that contains scg directory, run the mininet script: ```sudo python3 -m scg.network.mininet_network```

1. Mininet wifi instalation:

    - packages:
        * ```sudo apt-get install network-manager```
        * ```sudo service stop network-manager```
        * ```sudo apt install linux-generic-hwe-20.04```
        * ```linux-modules-5.4.0-1030-kvm_5.4.0-1030.31_amd64.deb``` 
        * ```linux-image-5.4.0-1030-kvm_5.4.0-1030.31_amd64.deb``` 

    - reboot the OS after installing the packages for wmedium.
        * ```git clone https://github.com/intrig-unicamp/mininet-wifi.git```
        * ```cd mininet-wifi```
        * ```sudo util/install.sh -Wlnfv```
    
    - Setup Xauthority
        * Make sure ~/.Xauthority owned by you: ```ls -l ~/.Xauthority```
        * ```chown user:group ~/.Xauthority```
        * ```chmod 0600 ~/.Xauthority```
        * ```export XAUTHORITY=$HOME/.Xauthority```
    
    - Setup display
        * ```export DISPLAY="127.0.0.1:10.0"``` or ```export DISPLAY=:0.0```
        * For mac osx install XQuartz and use -Y to ssh, export the display, and export XAUTHORITY 

    - X11 SSHD (server) Forwarding
        * set X11Forwarding yes at ```/etc/ssh/sshd_config```

    - X11 client Forwarding
        * set X11Forwarding yes at ```/etc/ssh/ssh_config ```

    - Stop network manager service
        * ```sudo service network-manager stop```

---

## Web server setup
1. The web server provides an *async function* to control the number of requests in order to respond to all requests at the same time. 
    - Example: there are 5 migration algorithms, then we have to run ``` python3 ~/scg/main.py {migration_algorithm}``` 5 times, especifying each migration algorithm acronym. 
    - The web server will only respond after receiving 5 requets.
    - The number of algorithms is specified at ```~/scg/web_server.py```
    - Each algorithm will request the data from the web server. 
    - After each iteration of script ```/scg/main.py```, the algorithms that finish their processing tasks first have to wait until all other algorithms finish their tasks. 
    - This action ensures that all algorithms will have the same workload in each iteration.
---

## TENET setup

1. Computing resources (GPUs and CPUs) for MEC servers and VR services are automatically generated based on the number of base stations and hmds configured at **mininet_network.py**. The data will be stored at **~/config/mecs.json**, **~/config/base_stations.json** and **~/config/hmds.json**. 
    - Wait until all services are recognized by the SDN controller
    - To do so, check **http://ONOS-VM-IP:8181/onos/ui/#/host**

2. Every time the script **mininet_network.py** runs, we have to delete the *hmds.json* file because VR HMDs will have different MAC addresses. 

3. To start the system, runs the following scripts:
    - ```python3 ~/scg/network/mininet_network.py```
    - ```python3 ~/scg/web_server.py```
    - ```python3 ~/scg/main.py {migration_algorithm}``` 


---