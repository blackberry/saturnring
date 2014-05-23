#!/bin/bash
function GetKey () {
	PY_SCRIPT="import sys;import json;print json.loads(sys.argv[1])[sys.argv[2]];"
	OUTPUT=$(  python -c "$PY_SCRIPT" "$1" "$2"  )
	echo ${OUTPUT}
}

apt-get install -y open-iscsi

#User defines these variables
##################################################
SIZEINGB=1.0
SERVICENAME="fastiorequired"
SATURNRINGUSERNAME="fastiouser"
SATURNRINGPASSWORD="fastiopassword"
ANTI_AFFINITY_GROUP=${SATURNRINGUSERNAME}"unique-string"
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

	
	


