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

set -e
TARGETMD5=`echo $2 | md5sum | cut -f1 -d" "`
lvolName=lvol-${TARGETMD5:0:8}
CSTR=`lvcreate -V$1G -T $6/thinpool -n $lvolName`

#lvolName=$(echo "$CSTR" | grep -o '\".*\"' | sed -e 's/\"//g')
lvu=`lvdisplay $6/$lvolName | grep "LV UUID" | sed  's/LV UUID\s\{0,\}//g' | tr -d '-' | tr -d ' '`
vgu=`vgdisplay $6 | grep "VG UUID" | sed  's/VG UUID\s\{0,\}//g' | tr -d '-' | tr -d ' '`
dmp='/dev/disk/by-id/dm-uuid-LVM-'$vgu$lvu
echo $dmp

#Please use the below line, the other one is a place holder for older saturn server testing on VMs
#scstadmin -open_dev disk-${lvu:0:8} -handler vdisk_blockio -attributes filename=$dmp,thin_provisioned=1,rotational=0,write_through=1,blocksize=4096
scstadmin -open_dev disk-${lvu:0:8} -handler vdisk_blockio -attributes filename=$dmp
echo "add_target $2" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $2 allowed_portal $3" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
if [ "$3" != "$4" ]
then
  echo "add_target_attribute $2 allowed_portal $4" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
fi
#echo "add_target_attribute $2 blocksize 4096" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
#echo "add_target_attribute $2 thin_provisioned 1" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
#echo "add_target_attribute $2 rotational 0" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
#echo "add_target_attribute $2 write_through 1" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "create allowed_ini" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/mgmt
echo "add disk-${lvu:0:8} 0" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/allowed_ini/luns/mgmt
echo "add $5" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/allowed_ini/initiators/mgmt
echo 1 >/sys/kernel/scst_tgt/targets/iscsi/$2/enabled

scstadmin -write_config /etc/scst.conf
sudo mkdir -p /temp
sudo cp /etc/scst.conf /temp
sudo cp /etc/lvm/backup/$6 /temp
sudo chmod  666 /temp/scst.conf
sudo chmod 666 /temp/$6
echo "SUCCESS"
