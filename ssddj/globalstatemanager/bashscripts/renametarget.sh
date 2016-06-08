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

#For now, this is the bailout mechanism
set -e

OLDTARGET=$1
NEWTARGET=$2
VG=`vgdisplay -c | grep $3 | cut -d: -f1 | tr -d ' ' | tr -cd '[[:alnum:]]._-'`
LV=$4
LVU=`lvdisplay $VG/$LV | grep "LV UUID" | sed  's/LV UUID\s\{0,\}//g' | tr -d '-' | tr -d ' '`
ALLOWEDPORTAL=$5
INITIATOR=$6
echo "Old target: $OLDTARGET"
echo "New target: $NEWTARGET"
echo "VG : $VG"
echo "LV : $LV"
echo "LVU: $LVU"
echo "ALLOWEDPORTAL: $ALLOWEDPORTAL"
echo "INITIATOR: $INITIATOR"
echo "add_target $NEWTARGET" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $NEWTARGET allowed_portal $ALLOWEDPORTAL" >/sys/kernel/scst_tgt/targets/iscsi/mgmt

echo "create allowed_ini" >/sys/kernel/scst_tgt/targets/iscsi/$NEWTARGET/ini_groups/mgmt
echo "add disk-${LVU:0:8} 0" >/sys/kernel/scst_tgt/targets/iscsi/$NEWTARGET/ini_groups/allowed_ini/luns/mgmt
if [[ $INITIATOR == *"iscsihypervisor"* ]]
then
  echo "add iqn.iscsihypervisor*" >/sys/kernel/scst_tgt/targets/iscsi/$NEWTARGET/ini_groups/allowed_ini/initiators/mgmt
else
  echo "add $INITIATOR" >/sys/kernel/scst_tgt/targets/iscsi/$NEWTARGET/ini_groups/allowed_ini/initiators/mgmt
fi

# Now remove old target
yes | scstadmin -rem_target $OLDTARGET -driver iscsi

echo 1 >/sys/kernel/scst_tgt/targets/iscsi/$NEWTARGET/enabled

scstadmin -write_config /etc/scst.conf
sudo mkdir -p /temp
sudo cp /etc/scst.conf /temp
sudo cp /etc/lvm/backup/$VG /temp/$3
sudo chmod  666 /temp/scst.conf
sudo chmod 666 /temp/$3

#The last thing - checking if everything looks good


if ! grep  --quiet "disk-${LVU:0:8}" /etc/scst.conf; then
  echo "FAILED = no disk-${LVU:0:8} in /etc/scst.conf"
  exit
fi

if ! grep  --quiet "$NEWTARGET" /etc/scst.conf; then
  echo "FAILED - no entry for target $NEWTARGET  in scst.conf"
  exit
fi



echo "SUCCESS: renamed $OLDTARGET to   $NEWTARGET on $VG:  ($3)"


