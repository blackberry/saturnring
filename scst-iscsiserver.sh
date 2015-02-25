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
apt-get -y install subversion openssh-server screen make gcc sysstat thin-provisioning-tools lvm2
mkdir -p /temp
cd /temp
svn checkout svn://svn.code.sf.net/p/scst/svn/trunk scst-svn
#If using the latest dev version doesnt seem appropriate then get a suitable version on to the vagrant directory and use these steps
#cp /vagrant/scst.tar.gz .
#tar -xvzf scst.tar.gz
cd scst-svn
make 2perf
make scst scst_install iscsi iscsi_install scstadm scstadm_install
#Twice - seems to fix the iscsi module missing problem
make scst scst_install iscsi iscsi_install scstadm scstadm_install
if [ -n "" ]; then chr="chroot "; else chr=""; fi; if type systemctl >/dev/null 2>&1; then echo $chr systemctl enable "scst.service"; elif type chkconfig >/dev/null 2>&1; then echo $chr chkconfig --add "scst"; elif type update-rc.d >/dev/null 2>&1; then echo $chr update-rc.d "scst" defaults; elif type rc-update >/dev/null 2>&1; then echo $chr rc-update add "scst" default; elif type /usr/lib/lsb/install_initd >/dev/null 2>&1; then echo $chr /usr/lib/lsb/install_initd "scst"; fi
update-rc.d scst defaults
echo

cat <<EF > /etc/scst.conf

HANDLER vdisk_fileio {
DEVICE disk1 {
filename /dev/ram11
nv_cache 1
}
}

TARGET_DRIVER iscsi {
enabled 1

TARGET iqn.2010-12.org.alpinelinux:tgt {
enabled 0
}

TARGET iqn.2012-04.com.ubuntu:tgt1 {
enabled 0
rel_tgt_id 1

LUN 0 disk1
}

}
EF
service scst start
service scst restart

#Setup a loop device to emulate the block device that needs to be shared
#In any real setup the device will instead be the block device that needs to be shared
mkdir -p /loopdatadev
dd if=/dev/zero of=/loopdatadev/file.img bs=1MiB count=10000
DEV=`losetup --find --show /loopdatadev/file.img`

#VG setup
pvcreate $DEV
vgcreate storevg $DEV
#the logical volumes are all thin provisioned.
#Overkill on metadatasize - although running out of metadata is a very bad thing; if the shared block device is big (e.g several 100s of GB
#, then its best to max out the metadatasize (16GiB)
lvcreate -L9000MiB --poolmetadatasize 950MiB --type thin-pool --thinpool storevg/thinpool








