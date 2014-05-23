Introduction

Saturnring enables efficient sharing of block storage devices among multiple clients (loud VM instances). For example, a solid state device or QoS-guaranteed block storage like AWS provisioned IOPs can be shared by multiple VMs using Saturnring. The key motivation for doing this is that the IO capabilities of high performance block storage offered by cloud providers (e.g. SSDs attached to VMs) often exceed the requirements of that one VM, and therefore the excess IO capabilities (IO/sec, throughput, low latency) of SSDs can be exported to other VMs that then no longer need to provision dedicated SSD. A use case might be an application that uses a relational database (e.g. PostgresSQL) and a persistent messaging system (e.g. RabbitMQ) that are deployed on VMs in the cloud. Both class of applications benefit from high-performing SSD storage, but may not individually require the full capabilities of 2 independent SSDs. Saturnring aggregates block storage resources and enables architects to move block storage capabilities to where they are required in the application.

Another use case may be to build a SSD storage array for a private cloud by using Saturnring to provision and manage multiple bare-metal x86 boxes containing multiple SSD or PCIe solid-state cards.

Saturnring relies on recent versions of Linux LVM (Logical volume manager) to divide up block device(s) into logical volumes, which are then exported via an iSCSI server (currently, SCST) as iSCSI targets.Clients of this storage - iSCSI initiators use the corresponding LVs as block storage devices. Saturn provides mechanisms for orchestrating multiple multiple block devices. This is useful for example, when the user has multiple VMs with SSDs, and she would like to export this block storage to several other "client VMs". Saturn can also provision targets that belong to anti-affinity groups, meaning that targets belonging to the same AAG will be placed on different target block devices if possible. This is useful in controlling failure domains for applications like Cassandra or active-active replicated storage back-ends for relational databases.

Unlike clustered data storage systems (e.g. GPFS, Gluster, CEPH etc.) Saturnring makes no effort of replicating data on the back-end. There are no multiple copies being created on write. Instead Saturn defers high-availability and data protection to the application (e.g. NoSQL database replication or software RAID 1 across 2 target LVs on the initiator). Saturn's focus is on preserving low latency, highIOPs and high throughput properties of SSDs or other "fast" storage over the cloud network. For this it relies on the well vetted Linux iSCSI implementation SCST (other iSCSI implmentations can be substituted with moderate effort). Saturn's value add is manageability and RESTFul block storage sharing and provisioning amenable to cloud applications.

Architecture

Saturnring provides the following components:

1. A web portal and API which 
a)allows the storage administrator to manage users and their iSCSI targets
b) A HTTP RESTful-API call to provision iSCSI targets
c) Facilities like user quotas, ingesting multiple iSCSI target servers into a Saturnring cluster, deleting storage, thin provisioning, and basic monitoring support etc.
2 A Vagrant environment where all of the above is setup; this example should give enough guidance to move to AWS or other suitable public or private cloud provider.

Fig 1. shows the concepts in action. clients can use the RESTful provisioner call to create iSCSI targets on saturn servers' LVM volume groups. The portal allows administrators to track the overal storage in the Saturnring cluster. It also provides user views to track Saturn storage for individual users.

The web portal is a modified Django admin interface. It provides user management, saturn server management and information about targets, logical volumes and volume groups. By hacking the default Django interface rather than creating custom views the core functioanlity  (managing iSCSI block devices) has been the key development focus. A single pr


Running the Vagrant Setup

Vagrant, along with the underlying virtualbox hypervisor, is used to demonstrate and develop Saturnring here. There are two categories of VMs. The first is the Saturnring portal. The second is the Saturn server. A third category, the iSCSI client, is also included for completeness. Each of the VMs is derived from the stock Ubuntu 14.04 distribution; scripts are provided for each step in order to make saturnring images for any cloud provider.






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

