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

function GetKey () {
	PY_SCRIPT="import sys;import json;print json.loads(sys.argv[1])[sys.argv[2]];"
	OUTPUT=$(  python -c "$PY_SCRIPT" "$1" "$2"  )
	echo ${OUTPUT}
}

apt-get install -y open-iscsi

#User defines these variables
##################################################
SIZEINGB=1.0
SERVICENAME="fastiorequired-target1"
SATURNRINGUSERNAME="fastiouser"
SATURNRINGPASSWORD="fastiopassword"
ANTI_AFFINITY_GROUP=${SATURNRINGUSERNAME}"mdraidgroup"
SATURNRINGURL="http://192.168.61.20/api/provisioner/"
##################################################

IQNINI=`cat /etc/iscsi/initiatorname.iscsi | grep ^InitiatorName=  | cut -d= -f2`
RTNSTR=$( unset http_proxy && curl -s -X GET "${SATURNRINGURL}" --user "${SATURNRINGUSERNAME}":"${SATURNRINGPASSWORD}" --data clientiqn="${IQNINI}"'&'sizeinGB="${SIZEINGB}"'&'serviceName="${SERVICENAME}"'&'aagroup="${ANTI_AFFINITY_GROUP}" )
echo $RTNSTR | python -mjson.tool

ERROR=`GetKey "${RTNSTR}" "error"`

if [ "$ERROR" -eq "0" ] 
then
	SESSIONUP=`GetKey "${RTNSTR}" "sessionup"`
	if [ ${SESSIONUP} = False ] 
	then
		IQNTARGET=`GetKey "$RTNSTR" "iqntar"`
		STOREPORTAL=`GetKey "$RTNSTR" "targethost__storageip1"`
		echo $IQNTARGET
		echo $STOREPORTAL
		iscsiadm -m discovery -t st -p "$STOREPORTAL"
		iscsiadm -m node --targetname "$IQNTARGET" --portal "$STOREPORTAL" --login
	else
		echo "STOPPED: Active session detected on target "$IQNTARGET
	fi
else
	echo "Error in getting IQNTARGET from saturn server "$IQNTARGET	
fi
#Now, there should be a block device in /dev corresponding to the iSCSI session
#Check iSCSI session status via sudo iscsiadm -m session -P3

#Provision second target
$SERVICENAME=fastiorequired-target2
RTNSTR=$( unset http_proxy && curl -s -X GET "${SATURNRINGURL}" --user "${SATURNRINGUSERNAME}":"${SATURNRINGPASSWORD}" --data clientiqn="${IQNINI}"'&'sizeinGB="${SIZEINGB}"'&'serviceName="${SERVICENAME}-target2"'&'aagroup="${ANTI_AFFINITY_GROUP}" )
echo $RTNSTR | python -mjson.tool
ERROR=`GetKey "${RTNSTR}" "error"`
if [ "$ERROR" -eq "0" ]
then
  STOREPORTAL2=`GetKey "$RTNSTR" "targethost__storageip1"`
  if [ ${STOREPORTAL1} = ${STOREPORTAL2} ]
  then
    echo "WARNING - ANTI-AFFINITY FAILURE, both targets provisioned on ${STOREPORTAL1}"
    iscsiadm -m session -u ##Use these lines for exiting if AA doesnt work out
    exit 1
  fi
  echo "Ok, different storeportals for the 2 targets so the anti-affinity is working"
        SESSIONUP=`GetKey "${RTNSTR}" "sessionup"`
        if [ ${SESSIONUP} = False ]
        then
                IQNTARGET=`GetKey "$RTNSTR" "iqntar"`
                STOREPORTAL2=`GetKey "$RTNSTR" "targethost__storageip1"`
                echo $IQNTARGET
                echo $STOREPORTAL2
                iscsiadm -m discovery -t st -p "$STOREPORTAL2"
                iscsiadm -m node --targetname "$IQNTARGET" --portal "$STOREPORTAL2" --login
        else
                echo "STOPPED: Active session detected on target "$IQNTARGET
    iscsiadm -m session -u
    exit 1
        fi
else
        echo "Error in getting IQNTARGET from saturn server "$IQNTARGET
fi
#If all is well until this time, we should have 2 block devices - assuming sda and sdb
#Next - install md and create RAID 1 array
#First, read this about how to manage your RAID 1 software arrays using md
#http://www.tldp.org/HOWTO/Software-RAID-HOWTO-6.html
apt-get install mdadm -y --no-install-recommends
#Check if a pre-existing md array is on the drives, and if so assemble it
ASSEMBLESCAN=`mdadm --assemble --scan`
if echo "$ASSEMBLESCAN" | grep -q "has been started with 2 drives."; then
    echo "Array already existed";
    cat /proc/mdstat 
else
  yes | mdadm --create --verbose /dev/md0 --level=mirror --raid-devices=2 /dev/sda /dev/sdb
  mdadm --grow --bitmap=internal /dev/md0
  mkfs.ext4 /dev/md0 -b 4096 -m 1 -E nodiscard
fi
mkdir -p /datadir
mount /dev/md0 /datadir


