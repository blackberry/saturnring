Introduction

Saturnring enables efficient sharing of block storage. For example, a solid state device or QoS-guaranteed block storage like AWS provisioned IOPs can be shared by multiple VMs using Saturnring. The key motivations for doing this could be
1) The IO capabilities of high performance block storage offered by cloud providers (e.g. SSDs attached to VMs) often exceed the requirements of that one VM. 
2) Another bottleneck like CPU load or memory prevents full IO utilization of the block storage. Therefore the excess IO capabilities (high number of IOs/sec, throughput, low latency) of SSDs can be exported to other VMs. This is usually  much cheaper than buying SSD storage for each of the VMs seperately.
3) Saturnring can be used to create highly available block storage and remove single points of failure (that single SSD block device attached to a single VM). For example Saturnring can offer two block devices from two different VMs to a third client VM, and the client can use software RAID 1 (like md or mirror LVM) to create a highly available block device from the two block devices. This setup also doubles the read IO capability.
 
A use case for Saturnring might be an application that uses a relational database (e.g. Postgres or MariaDB) and a persistent messaging queue syeste (e.g. RabbitMQ) that are deployed on VMs in the cloud. Both class of applications benefit from high-performing SSD storage, but may not individually require the full capabilities of 2 independent SSDs. Another use case may be an SSD storage array for a private cloud by using Saturnring to provision and manage multiple bare-metal x86 boxes containing SSDs or PCIe solid-state storage cards. Saturnring aggregates block storage resources and enables architects to move block storage capabilities to where they are required in the application. 

Saturnring relies on recent versions of Linux LVM (Logical volume manager) to divide up block device(s) into logical volumes that are exported via an iSCSI server (currently, SCST) as iSCSI targets. Clients of this storage - iSCSI initiators - create iSCSI sessions to to the targets in order to use the corresponding LVs as block storage devices. Saturn provides mechanisms for orchestrating multiple multiple block devices. This is useful for example, when provisioning from multiple VMs with SSDs to several other "client VMs". Saturn can also provision targets that belong to anti-affinity groups; targets belonging to the same AAG will be placed on different target block devices if possible. This is useful in controlling failure domains for applications like Cassandra or active-active replicated storage back-ends for relational databases. Tests indicate that the memory and CPU requirement of SCST is low, therefore it may be installed alongside other applications on the same host. Moreover, Saturnring does not require control of the full block device, it instead provisions storage off a volume group that may be created over a part of the block device. 

Unlike clustered data storage systems (e.g. GPFS, Gluster, CEPH etc.) Saturnring makes no effort of replicating data on the back-end. There are no multiple copies being created on write. Instead Saturnring defers high-availability and data protection to the application (e.g. NoSQL database replication or software RAID 1 across 2 target LVs on the initiator). Saturnring manages one or more iSCSI servers. Saturnring focus is on preserving low latency, highIOPs and high throughput properties of SSDs or other "fast" storage over the cloud network. For this it relies on the well vetted Linux iSCSI implementation SCST (other iSCSI implmentations can be substituted with moderate effort). Its chief value add is manageability and RESTFul block storage sharing and provisioning, all amenable to cloud applications.

Architecture

Saturnring provides the following components:

1. A web portal and API which 
a)allows the storage administrator to manage users and their iSCSI targets
b) A HTTP RESTful-API call to provision iSCSI targets. The API is very
sparse by design - there is only one API method that provisions block storage.
This prevents fat finger issues.
c) Facilities like user quotas, ingesting multiple iSCSI target servers into a Saturnring cluster, deleting storage, thin provisioning, and basic monitoring support etc. are available via the Saturnring portal
2. A Vagrant setup where all of the above is setup; this example should give enough guidance to  install Saturnring in AWS or other suitable public or private cloud provider.

Fig 1. shows how Saturnring works. Clients can use the RESTful provisioner call to create iSCSI targets on saturn servers' LVM volume groups. The portal allows administrators to track the overall storage in the Saturnring cluster (up to the logical volume level). It also provides user views to track Saturn storage for individual users. The web portal is a modified Django admin interface. By hacking the default Django interface rather than creating custom views, the core functionlity (managing iSCSI block devices) has been the key development focus. 


Getting Started
Saturnring is built out of multiple components - the iSCSI server(s), the Django-driven Saturnring portal and API and Apache webserver with modwsgi extensions, the backend database (sqlite or other Django-compatible relational DB) and a redis-server and job workers for running periodic tasks. A Vagrant file and shell provisioner scripts are included to automatically setup these components for illustration. The Vagrant file setups up Virtualbox VMs that take on the roles of the Saturnring server, 2 iSCSI servers, and an iSCSI client. Vagrant brings up vanilla Ubuntu 14.04 images, and the shell provisioner scripts do the work of adapting the vanilla VMs into these different roles. These bash scripts are an easy segway to setting up Saturnring in any other virtual or bare-metal environment, or for creating custom images.

Assuming you have an unhindered Internet connection and a computer capable of running at least 2 VMs (256M RAM per VM, 1 vCPU per VM, 20GiB disk)
1. Install Virtualbox
http://www.virtualbox.org

2. Install vagrant 
http://docs.vagrantup.com/v2/installation/

3. On the Virtualbox host machine (your PC) Clone into <GITHUB DIRECTORY> in local directory <DIRROOT>
mkdir -p ~/DIRROOT
cd ~/DIRROOT
git clone <GITHUB URL> 

4. Navigate to <DIRROOT>/deployments/vagrant
cd ~/DIRROOT/deployments/vagrant

STAGE 1: Getting Bringing up Saturnring portal/API server

5. Use Vagrant to bring up the Saturnring VM, you should see a lot of bootup activity happening on the VM (takes a while) 
vagrant up saturnring

6. If all went well, you should be able to navigate to
   http://192.168.61.20/admin from a web brower on the host machine 

7. Log into the Saturnring VM
vagrant ssh saturnring

8. Activate the Saturnring Python environment
cd saturnring
source saturnenv/bin/activate

9. Create a Storage admin superuser  
cd /home/vagrant/saturnring/ssddj
python manage.py createsuperuser
(follow the prompts to setup a superuser)

10. Exit to the host and confirm that you can log into the Saturnring
   portal using the superuser credentials in the web browser.

STAGE 2: Bringing up the iSCSI server(s)

11. Navigate to <DIRROOT>/deployments/vagrant
cd ~/DIRROOT/deployments/vagrant

12. Bring up  an iSCSI VM defined in Vagrantfile 
vagrant up iscsiserver1

13. Log into the saturnring VM and copy SSH keys for Saturning to
    access the iSCSI server
vagrant ssh saturnring
cd ~/saturnring/ssddj/config
ssh-copy-id -i saturnkey vagrant@192.168.61.21

14. Log into the saturnring portal as admin superuser and add the new  iscsi server. For this simple example, Dnsname=Ipaddress=Storageip1=Storageip2=192.168.61.21. Failure to save indicates a problem in the configuration steps (11-13). Saturnring will not allow a Storagehost being saved before all the config is right. This is probably a good thing.

15. From the VM host or one of the above 2 fired up VMs, Make a "initial scan" request to the Saturnring server so that it ingests the storage made available by iscsiserver1 at IP address 192.168.61.21 (Networking is defined in the Vagrantfile) 
curl -s -X http://192.168.61.20/api/vgscan -d "saturnserver=192.168.61.21" 
Confirm in the portal (under VGs) that there is a new volume group

16. Repeat steps 11-15 for iscsiserver2 if you want (it is useful to have 2 iscsiservers if you want to try the anti-affinity provisioning)

STAGE 3: Testing via a client VM



Directory Structure

The ssddj directory contains the Django project, which includes the portal and the API 

The deployment directory contains a vagrant VM setup (tested in Virtualbox); since the Vagrant setup starts with a vanilla Ubuntu VM and then applies scripts to the VMs to modify them into Saturnring VMs, the same scripts can be used to setup Saturnring on other virtual or bare-metal platforms

The doc directory contains some more documentation and images

The misc directory contains some scripts/supporting open-source software and their licenses if applicable

LICENSE

#Copyright 2014 Blackberry Limited
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#implied.
#See the License for the specific language governing permissions and
#limitations under the License.
