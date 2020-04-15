# HFRD
Hyperledger Fabric Regression Driver

#This introduce is used for setup HFRD for IBP V2.0's test
# Done load HRFD project

git clone https://github.com/gbl1124/hfrd.git
# Make API & Docker image
## Make API:

path: /hfrd

make api-docker

## Update run path

path: /hfrd/setup/hfrd.sh
       rootdir=~/hfrd            This is the test result saved path.
       install=~/hfrd-gbl/hfrd   This is the path you get HFRD source from git.

# Build Docker image
## Image for Jenkins
path:  /hfrd/docker/jenkins-ansible
docker build -t hfrd/jenkins:ibpv2-latest .

## Image for bxbox
path: /hfrd/backend/jenkins
docker build -f  docker/bxbox_alpine -t bxbox_alpine .

## Image for ocp-dns-proxy
path: /hfrd/backend/jenkins
docker build -f  docker/ocp-dns-proxy.dockerfile  -t  ocp-dns-proxy .

# create a custom docker network
 If you already have network ibp_ocp.
        use command: docker network ls  to check if you already have.
        use command : docker network inspect ibp_ocp
        To make sure it used the following config
        If you want remove: used command: docker network rm  ibp_ocp
 Use the following command create custom docker networt:       

docker network create \
  --driver=bridge \
  --subnet=172.3.27.0/24 \
  --ip-range=172.3.27.0/26 \
  --gateway=172.3.27.1 \
  ibp_ocp

# Set up docker network
Copy your local network resolv.conf for docker

cp /etc/resolv.conf to /hfrd/backend/jenkins/docker

add nameserver 127.0.0.1 into /hfrd/backend/jenkins/docker/resolv.conf
Note: Please make sure it on the first line

If you need upddate the hostname or need a new hostname.
update server=/hostname/ip in the following file: 
/hfrd/backend/jenkins/docker/dnsmasq.conf

for example: server=/apps.ibp-perf-zvm.openshift.zpa.ibm.com/9.12.44.56

# Start up:

```
./hfrd.sh start <Your_server_IP_address> <path_to_hfrdconfig.xml> <true/false>
   
    For example: ./hfrd.sh start 192.168.56.32 ./hfrdconfig.xml false
```   
This process creates a directory named hfrd in your home directory. There will be many files and directories created in this directory while your hfrd is running. The files and directories in ~/hfrd directory should not be changed manually. The process will also show you couple of urls at the end of the process. You can use these url to access hfrd rest server and jenkins server. For the example above, you should have two urls like these:

```
   http://192.168.56.32:9090   (The api server)
   http://192.168.56.32:8080   (The jenkins server)
```

The flag at the end means if the jenkins server needs to be restarted. In production env, you may not want to restart your jenkins server since it may still be running some jobs. This is very important especially when you just stopped a running instance of hfrd.
################################################################
# Stop hfrd
Run the following command to stop all the hfrd containers
```
./hfrd.sh stop
```
