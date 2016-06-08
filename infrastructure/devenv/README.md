# Development and Testing Environment for Saturnring  

Saturnring is built out of multiple components - the iSCSI server(s), the Django-driven Saturnring portal and API and Apache webserver with mod-wsgi extensions, the backend database (sqlite or other Django-compatible relational DB) and a redis-server and job workers for running periodic tasks. A Vagrant file and shell provisioner scripts are included to automatically setup these components for development and testing.

Vagrant is a system for creating and configuring virtual development environments. It is used to create  KVM-based virtual machine instances of the Saturnring server and the iSCSI servers. They emulate a real world Saturnring configuration.

Instead of supplying pre-baked and customized VM images, the idea is to provide scripts that can be adapted to instantiate Saturnring on any private or public cloud or on bare-metal, or used to create custom images for other environments. Vagrant brings up vanilla Ubuntu 14.04 images, and the shell provisioner scripts do the work of adapting the vanilla VMs into these different roles.

An unhindered Internet connection and a computer capable of running at least 3 VMs (256M RAM per VM, 1 vCPU per VM, 20GiB disk across the 3 VMs) is assumed here. 'Host' refers to the PC running the VMs, the SSH `login/password` for all VMs is `vagrant/vagrant`, and the Vagrant file defines an internal network 192.168.56/24 and a bridged adaptor to let VMs access the Internet. Here are the step-by-step installation instructions


## STAGE 0: Software installation and code download
  1. Install vagrant: http://docs.vagrantup.com/v2/installation/
  2. Install [libvirt](http://libvirt.org/) on the host operating System
  3. [Install](https://github.com/pradels/vagrant-libvirt) the Vagrant libvirt extension `vagrant-libvirt`
  4. The next step is to get a Vagrant libvirt KVM Ubuntu image. Look at the [vagrant-mutate](https://github.com/sciurus/vagrant-mutate) project to convert a virtualbox Vagrant box to libvirt. Or, a pre-tested libvirt vagrant box to use is available from [here](https://vagrantcloud.com/naelyn/boxes/ubuntu-trusty64-libvirt). For this example we will install and use this ready-made box. To install, run
  ```bash
  vagrant box add naelyn/ubuntu-trusty64-libvirt
  ```
  5. On the KVM host machine (your PC) Clone into    https://github.com/sachinkagarwal/Saturnring/; the chosen directory from which the clone command is run is henceforth designated `~/DIRROOT`.
  ```bash
   cd ~/DIRROOT
   git clone https://github.com/sachinkagarwal/Saturnring/
   ```
  6. Navigate to  `cd ~/DIRROOT/saturnring/`  
  7. Setup the NFS server on the host for the shared directory access. Note we do not use the Vagrant-provided shared directory.
  ```bash
    cd ~/DIRROOT/saturnring
    #Setup NFS
    sudo apt-get install nfs-kernel-server nfs-common rpcbind
    PWD=`pwd`
    sudo cat <<EOF >> /etc/exports
    $PWD *(rw,no_root_squash,no_subtree_check)
    EOF
    ```
    Edit the saturnring_postbootup.sh and scst-iscsiserver.sh scripts to insert the correct NFS mountpoint entry by running this command
    ```bash
    sed -i 's|^HOSTNFSDIR.*|HOSTNFSDIR='"$PWD"'|' ./devenv/saturnring_postbootup.sh
    sed -i 's|^HOSTNFSDIR.*|HOSTNFSDIR='"$PWD"'|'
./devenv/scst-iscsiserver.sh
    ```
    Export the directory via NFS
    ```bash
    exportfs -a
    ```

## STAGE 1: Bringing up Saturnring portal/API server
_Vagrant will set this up at IP 192.168.50.50, as described in the ~/DIRROOT/saturnring/devenv/Vagrantfile_

  1. Bring up the VM using
  `vagrant up saturnring --provider libvirt`
  2. If all goes well, (after a few minutes) you should be able to navigate to `http://192.168.50.50/admin`  from a web brower on the host machine. Check by logging in with credentials “admin/changeme”.

## STAGE 2: Bringing up the iSCSI server(s)
  1. Bring up an iSCSI VMs
`vagrant up iscsiserver1; vagrant up iscsiserver2`
  2. Log into the Saturnring VM and copy SSH keys for Saturning to access the iSCSI server  
  ```bash
  vagrant ssh Saturnring  
  cd ~/nfsmount/Saturnring/Saturnringconfig  
  ssh-copy-id -i saturnkey vagrant@192.168.50.51  #(password is vagrant)
  ```
  3. Log into the Saturnring portal as admin superuser and add the new iscsi servers. For this simple example, the two iSCSI servers are `dnsname=Ipaddress=Storageip1=Storageip2=192.168.50.51/192.168.50.52`.

  On clicking save, a failure notice indicates a problem in the configuration steps. Saturnring will not allow a Storagehost being saved before the configuration is right.
  4. From the VM host issue a "initial vgscan" request to the Saturnring   server so that it ingests the storage made available by iscsiservers at IP address 192.168.50.51 and .52.
  `curl -X GET http://192.168.50.50/api/vgscan/ -d "saturnserver=192.168.50.51"`
  Repeat for 192.168.50.52. Confirm in the web browser portal (under VGs) that there is a new volume group
