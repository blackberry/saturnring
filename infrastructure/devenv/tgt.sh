#!/bin/bash
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
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


# For ideal performance SCST should be installed on a patched kernel. For how to patch the Ubuntu kernel for SCST see link:
# http://scst.sourceforge.net/iscsi-scst-howto.txt

apt-get update
apt-get -y install subversion openssh-server screen make gcc sysstat thin-provisioning-tools lvm2 unzip cryptsetup cryptsetup-bin tgt

sudo su -c "useradd oneadmin -s /bin/bash -m"
if [ -z "$1" ]; then
    echo "Starting up visudo with this script as first parameter"
    export EDITOR=$0 && sudo -E visudo
    else
        echo "Changing sudoers"
        echo "oneadmin ALL=(ALL) NOPASSWD: ALL" >> $1
fi



mkdir -p /temp
#Setup a loop device to emulate the block device that needs to be shared
#In any real setup the device will instead be the block device that needs to be shared
mkdir -p /loopdatadev
rm -rf /loopdatadev/*
if [ ! -f /loopdatadev/filetgt.img ]; then
  dd if=/dev/zero of=/loopdatadev/filetgt.img bs=1MiB count=3000 && sync
fi
DEV=`losetup --find --show /loopdatadev/filetgt.img`

sleep 5
#VG setup
vgs
pvcreate $DEV
vgcreate vg-one $DEV
vgs
#the logical volumes here are all thin provisioned.
#Overkill on metadatasize - although running out of metadata is a very bad thing; if the shared block device is big (e.g several 100s of GB
#, then its best to max out the metadatasize (16GiB)
#lvcreate -L9600MiB --type thin-pool --thinpool storevg-thin/thinpool

#if [ ! -f /loopdatadev/file-nothin.img ]; then
#  dd if=/dev/zero of=/loopdatadev/file-nothin.img bs=1MiB count=10000 && sync
#fi

#DEV=`losetup --find --show /loopdatadev/file-nothin.img`
#sleep 5
#VG setup
#vgs
#pvcreate $DEV
#vgcreate storevg-nothin $DEV
#vgs
#the logical volumes are not thin provisioned.







