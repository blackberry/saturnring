#!/bin/bash
#TOTALCAP=`lvs | grep "\s\sthinpool*" | cut -d" " -f10- | tr -d " " | cut -d"g" -f1`
#echo $TOTALCAP
#PERCENTUSED=`lvs | grep "\s\sthinpool*" | cut -d" " -f10- | tr -d " " | cut -d"g" -f2`
#echo $PERCENTUSED
#GBAVL=`echo "$TOTALCAP*(100-$PERCENTUSED)/100" | bc`
#echo $GBAVL
#echo $1
#echo $2
#if [ `echo "$1 < $GBAVL" | bc`==1 ]; then
#    echo "Capacity available, creating LV"
#    CSTR=`lvcreate -V$1G -T storevg/thinpool`
#    lvolName=$(echo "$CSTR" | grep -o '\".*\"' | sed -e 's/\"//g')
#    scstadmin -add_target "$2" -driver iscsi
#    scstadmin -open_dev disk-"$lvolName" -handler vdisk_blockio -attributes filename=/dev/storevg/"$lvolName",nv_cache=1
#    scstadmin -add_lun 0 -driver iscsi -target "$2" -device disk-"$lvolName"
#    scstadmin -enable_target "$2" -driver iscsi
#    scstadmin -write_config /etc/scst.conf
#    echo "SUCCESS"
#else
#    echo "Cannot create LV, capacity exceeded"
#    exit 1
#fi

CSTR=`lvcreate -V$1G -T storevg/thinpool`
lvolName=$(echo "$CSTR" | grep -o '\".*\"' | sed -e 's/\"//g')
scstadmin -open_dev disk-"$lvolName" -handler vdisk_blockio -attributes filename=/dev/storevg/"$lvolName",nv_cache=1

echo "add_target $2" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $2 allowed_portal $3" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $2 allowed_portal $4" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "create allowed_ini" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/mgmt
echo "add disk-$lvolName 0" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/allowed_ini/luns/mgmt
echo "add $5" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/allowed_ini/initiators/mgmt
echo 1 >/sys/kernel/scst_tgt/targets/iscsi/$2/enabled

scstadmin -write_config /etc/scst.conf
echo "SUCCESS"
