## Synopsis

Saturnring enables sharing multiple block storage devices on multiple hosts via iSCSI. For example, SSD or QoS-guaranteed block storage like AWS provisioned IOPs can be shared by multiple VMs using Saturnring.

## Motivation

1. The IO capabilities of high performance block storage offered by cloud providers (e.g. SSDs attached to VMs) often exceed the requirements of that one VM. 
2. Non-IO bottlenecks like CPU load or memory prevent the optimal use of high performance IO devices like SSDs . The unused IO capabilities (high number of IOs/sec, throughput, low latency) of SSDs can be exported to other VMs. This is usually more economical than buying SSD storage for VMs seperately.
3. Saturnring can be used to create highly available block storage and remove single points of failure (single SSD block device attached to a VM). For example Saturnring can offer (parts of) two block devices from two different VMs to a third client VM, and the client can use software RAID 1 (like md or mirror LVM) to create a highly available block device. This setup also doubles the read IO capability.
 
A use case for Saturnring might be an application that uses a relational database (e.g. Postgres or MariaDB) and a persistent messaging queue system (e.g. RabbitMQ) in the cloud. Both class of applications benefit from high-performing SSD storage, but may not individually require the full capabilities of 2 independent SSDs. Another use case is building a multi-head  SSD storage array for a private cloud by using Saturnring to provision and manage multiple bare-metal x86 boxes containing SSDs or PCIe solid-state storage cards. Saturnring aggregates block storage resources and enables architects to move block storage capabilities to where they are required in the application. 

Saturnring relies on recent versions of Linux LVM (Logical volume manager) to divide up block device(s) into logical volumes that are exported via an iSCSI server (currently, SCST) as iSCSI targets. Clients of this storage - iSCSI initiators - create iSCSI sessions to to the targets in order to use the corresponding LVs as block storage devices. Saturn provides mechanisms for orchestrating multiple block devices. Saturn can also provision targets that belong to the same anti-affinity groups: targets belonging to the same AAG will be placed on different target block devices if possible. This is useful in controlling failure domains for applications like Cassandra or active-active replicated storage back-ends for relational databases. Saturnring does not require control of the full block device, it instead provisions storage off a volume group that may be created over a part of a block device. 

Unlike clustered data storage systems (e.g. GPFS, Gluster, CEPH etc.) Saturnring makes no effort of replicating data on the back-end. There are no multiple copies being created on write. Instead Saturnring defers high-availability and data protection to the application (e.g. NoSQL database replication or software RAID 1 across 2 target LVs on the initiator). Saturnring manages one or more iSCSI servers. Saturnring focus is on preserving low latency, highIOPs and high throughput properties of SSDs or other "fast" storage over the cloud network. For this it relies on the well vetted Linux iSCSI implementation SCST (other iSCSI implmentations can be substituted with moderate effort). Its chief value add is manageability and RESTFul block storage sharing and provisioning, all amenable to cloud applications.

## Architecture

Saturnring provides the following components:

1. A web portal and API which 
a)allows the storage administrator to manage users and their iSCSI targets
b) A HTTP RESTful-API call to provision iSCSI targets. To keep things simple the API is very sparse by design - there are only 3 API methods.
c) Facilities like user quotas, ingesting multiple iSCSI target servers into a Saturnring cluster, deleting storage, thin provisioning, and basic monitoring support etc. are available via the Saturnring portal
2. A Vagrant setup where all of the above is setup; this example should give enough guidance to  install Saturnring in AWS or other suitable public or private cloud provider.

Fig 1. shows how Saturnring may be setup to serve out block storage.
![Fig 1: high level architecture](http://gitlab.rim.net/ssd/saturnring/raw/localrun/doc/high-level-arch.png "High Level Architecture")
Clients can use the RESTful provisioner call to create iSCSI targets on saturn servers' LVM volume groups. The portal allows administrators to track the overall storage in the Saturnring cluster (up to the logical volume level). It also provides user views to track Saturn storage for individual users. The web portal is a modified Django admin interface. By hacking the default Django interface rather than creating custom views, the core functionlity (managing iSCSI block devices) has been the key development focus. 



## Installation and Getting Started
Saturnring is built out of multiple components - the iSCSI server(s), the Django-driven Saturnring portal and API and Apache webserver with modwsgi extensions, the backend database (sqlite or other Django-compatible relational DB) and a redis-server and job workers for running periodic tasks. A Vagrant file and shell provisioner scripts are included to automatically setup these components for illustration. Instead of supplying pre-baked and customized VM images for quick setup the idea is to provide scripts that can be adapted to instantiate Saturnring on any private or public cloud. The Vagrant file setups up Virtualbox VMs that take on the roles of the Saturnring server, 2 iSCSI servers, and an iSCSI client. Vagrant brings up vanilla Ubuntu 14.04 images, and the shell provisioner scripts do the work of adapting the vanilla VMs into these different roles. These bash scripts are an easy segway to setting up Saturnring in any other virtual or bare-metal environment, or for creating custom images to be used in the cloud.

An unhindered Internet connection and a computer capable of running at least 2 VMs (256M RAM per VM, 1 vCPU per VM, 20GiB disk) is assumed here. 'Host' refers to the PC running the VMs, the SSH login/password for all VMs is vagrant/vagrant, and the Vagrant file defines an internal network 192.168.61/24 and a bridged adaptor to let VMs access the Internet.
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
(192.168.61.20)

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
vagrant up iscsiserver1 (192.168.61.21)

13. Log into the saturnring VM and copy SSH keys for Saturning to
    access the iSCSI server
vagrant ssh saturnring
cd ~/saturnring/ssddj/config
ssh-copy-id -i saturnkey vagrant@192.168.61.21

14. Log into the saturnring portal as admin superuser and add the new  iscsi server. For this simple example, Dnsname=Ipaddress=Storageip1=Storageip2=192.168.61.21. Failure to save indicates a problem in the configuration steps (11-13). Saturnring will not allow a Storagehost being saved before all the config is right. This is probably a good thing.

15. From the VM host or one of the above 2 fired up VMs, Make a "initial scan" request to the Saturnring server so that it ingests the storage made available by iscsiserver1 at IP address 192.168.61.21 (Networking is defined in the Vagrantfile) 
curl -s -X http://192.168.61.20/api/vgscan -d "saturnserver=192.168.61.21" 
Confirm in the portal (under VGs) that there is a new volume group

16. Repeat steps 11-15 for iscsiserver2 (192.168.61.22) if you want (it is useful to have 2 iscsiservers if you want to try the anti-affinity provisioning)

STAGE 3: Testing via an iscsi client VM (192.168.21.23)

17. Log into the Saturnring web portal as superuser and under users create an account for a test user (fastiouser/fastiopassword).Do not change the storage quota while creating the user. Make the user a staff user and give it permission to add, remove and modify targets.

19. On the host  navigate to <DIRROOT>/deployments/vagrant
cd ~/DIRROOT/deployments/vagrant
vagrant up iscsiclient

20. Log into the iscsi client
vagrant ssh iscsiclient

21. Edit the script storage-provisioner.sh and set appropriate values
    for

##################################################
SIZEINGB=1.0
SERVICENAME="fastiorequired"
SATURNRINGUSERNAME="fastiouser"
SATURNRINGPASSWORD="fastiopassword"
ANTI_AFFINITY_GROUP=${SATURNRINGUSERNAME}"unique-string"
SATURNRINGURL="http://192.168.61.20/api/provisioner/"
##################################################

Then run the storage-provisioner.sh script

sudo ./storage-provisioner.sh
An iSCSI session from the iscsiclient to an iscsi server will be created. A block device will be inserted in the client VM's /dev directory. dmesg should show the initialization details, including the name of the new block device. More information about the iscsi Session is available on the client via the command
iscsiadm -m session -P3


22. Any filesystem can be created on the device. The target block device is thin provisioned, but sometimes thin provisioning's unmap doesnt play well if large files are deleted. For now, its best to create the filesystem with nodiscard options set and use fstrim for asynchronous unmapped block recovery.


## Saturnring iSCSI Target Properties

iSCSI targets have some unique properties

Here is the target IQN string created above:
 
iqn.2014.01.192.168.61.21:fastiorequired:47bb7658
The encoding is as follows: 
iqn.2014.01.<IP address of iscsiserver>:<servicename>:<client IQN hash>

The key to note is that the <servicename>:<client IQN hash> is unique so attempts to create the same target will instead result in the pre-existing target data to be returned in the provisioner API call. Access is by client IQN - meaning that only targets assigned to the client IQN at creation will be visible during iSCSI discovery and session establishment. Therefore the client IQN can double up as a security password (yep its not a very secure, but then the underlying assumption is that your VMs running on your networking under your cloud account are trustworthy); and its best to keep it secret. More security-conscious users may want to look at modifying Saturnring to include iSCSI CHAP authentication etc.

All targets provisioned with the same "anti affinity group" will be spread among the available iSCSI servers as much as possible. This creates smaller fault domains in case an iSCSI server fails.

## Deployment Considerations

Here are some ideas for Saturnring in production
1. Monitoring and Alerting - consider something like Zabbix or Nagios to keep tabs on Saturnring components
2. Configuration management (Puppet/Chef etc.) or pre-built images will reduce the pain and errors that come with managing multiple servers manually
3. SSDs wear out - they have limited PE cycles; best to keep a close eye on them  
4. Saturnring uses a recent LVM2 implementation, look at its documentation for its many features
5. The Vagrant example does not patch the Linux kernel for optimal SCST iSCSI target software performance. Read more here: http://scst.sourceforge.net/iscsi-scst-howto.txt

## License

Apache 2.0 license
http://www.apache.org/licenses/LICENSE-2.0
