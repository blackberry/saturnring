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

function VGisThin () {
        VGSTR=`lvs --noheadings --units g --separator , | grep thinpool`
        if grep -q $1 <<<$VGSTR; then
                return 1
        else
                return 0
        fi
}


service scst status
[ $? -ne 0 ] && echo "FAILURE, SCST not loaded on $HOSTNAME" && exit

TARGETMD5=`echo $2 | md5sum | cut -f1 -d" "`
lvolName=lvol-${TARGETMD5:0:8}
VG=`vgdisplay -c | grep $6 | cut -d: -f1 | tr -d ' ' | tr -cd '[[:alnum:]]._-'`
if sudo lvs | grep $VG | egrep -q "$lvolName"; then
   echo "Warning: Using previously-created LV "$lvolName "on VG "$VG
else
  VGisThin $VG
  if [ $? -eq 1 ]; then
    echo "Trying to provision thinpool LV on $VG"
    LVCOUTPUT=`lvcreate -V$1G -T $VG/thinpool -n $lvolName`
  else
    echo "Trying to provision non-thin LV on $VG"
    LVCOUTPUT=`lvcreate -L$1G $VG -n $lvolName`
  fi
  echo $LVCOUTPUT
fi
#dd if=/dev/zero of=/dev/$VG/$lvolName && sync #Zero the LV to make sure dm-crypt/LUKs do not get confused by old stuff
cryptsetup luksFormat /dev/$VG/$lvolName -q -caes-cbc-essiv:sha256 $7
cryptsetup luksOpen /dev/$VG/$lvolName encrypted_$lvolName  --key-file $7

mkdir -p /cryptbackups
cryptsetup luksHeaderBackup /dev/$VG/$lvolName --header-backup-file /cryptbackups/$lvolName.cryptbackup.img

lvu=`lvdisplay $VG/$lvolName | grep "LV UUID" | sed  's/LV UUID\s\{0,\}//g' | tr -d '-' | tr -d ' '`
#vgu=`echo $6 | tr -d '-' | tr -d ' '`
dmp="/dev/mapper/encrypted_$lvolName"
#Please use the below line, the other one is a place holder for older saturn server testing on VMs
scstadmin -open_dev disk-${lvu:0:8} -handler vdisk_blockio -attributes filename=$dmp,thin_provisioned=0,rotational=0,write_through=1,blocksize=4096
#scstadmin -open_dev disk-${lvu:0:8} -handler vdisk_blockio -attributes filename=$dmp
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
if [[ $5 == *"iscsihypervisor"* ]]
then
  echo "add iqn.iscsihypervisor*" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/allowed_ini/initiators/mgmt
else
  echo "add $5" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/allowed_ini/initiators/mgmt
fi
echo 1 >/sys/kernel/scst_tgt/targets/iscsi/$2/enabled

scstadmin -write_config /etc/scst.conf
sudo mkdir -p /temp
sudo cp /etc/scst.conf /temp
sudo cp /etc/lvm/backup/$VG /temp/$6
sudo chmod  666 /temp/scst.conf
sudo chmod 666 /temp/$6

#The last thing - checking if everything looks good


if ! grep  --quiet "disk-${lvu:0:8}" /etc/scst.conf; then
  echo "FAILED = no disk-${lvu:0:8} in /etc/scst.conf"
  exit
fi

if ! grep  --quiet "$2" /etc/scst.conf; then
  echo "FAILED - no entry for target $2  in scst.conf"
  exit
fi



echo "SUCCESS: created target $2 on $VG:  ($6)"


