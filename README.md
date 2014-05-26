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

5. Use Vagrant to bring up the Saturnring VM, you should see a lot of bootup activity happening on the VM (takes a while) 
vagrant up saturnring

6. If all went well, you should be able to navigate to
   http://192.168.61.20/admin from a web brower on the host machine 

6. Log into the Saturnring VM
vagrant ssh saturnring

7. 

To run

Use screen, set the python environment as specified in the requirements file using pip and virtualenv

Screen 1
python manage.py runserver 0.0.0.0:8000

Screen 2
python manage.py rqworker default

Screen 3
crontab -e and then insert
* * * * * curl -X GET http://saturnring.store.altus.bblabs:8000/api/stateupdate/
Later you may do a tail -f saturn.log to see the log

On the browser:
http://<satunring.store.altus.bblabs>:8000/admin

On the iSCSI client (for example):
curl -X GET http://saturnring.store.altus.bblabs:8000/api/provisioner/ -d "clienthost=bbmserver62&sizeinGB=1.0&serviceName=b8mworkers" -u bbmserviceowner:password

Provisioning a new saturn server
Copy the SSH key
ssh-copy-id -i ./config/saturnserver.pub local@newhost.bb.com
Add the host to via the admin interface of Saturnring
Then kick the vgscanner
curl -X GET http://saturnring.store.altus.bblabs/saturnring/api/vgscan/ -d 'saturnserver=newhost.bb.com'

Directory Structure

The ssddj directory contains the Django project, which includes the portal and the API 

The deployment directory contains a vagrant VM setup (tested in Virtualbox); since the Vagrant setup starts with a vanilla Ubuntu VM and then applies scripts to the VMs to modify them into Saturnring VMs, the same scripts can be used to setup Saturnring on other virtual or bare-metal platforms

The doc directory contains some more documentation and images

The misc directory contains some scripts/supporting open-source software and their licenses if applicable

