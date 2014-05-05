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

CSTR=`lvcreate -V$1G -T $6/thinpool`
lvolName=$(echo "$CSTR" | grep -o '\".*\"' | sed -e 's/\"//g')
lvu=`lvdisplay $6/$lvolName | grep "LV UUID" | sed  's/LV UUID\s\{0,\}//g' | tr -d '-' | tr -d ' '`
vgu=`vgdisplay $6 | grep "VG UUID" | sed  's/VG UUID\s\{0,\}//g' | tr -d '-' | tr -d ' '`
dmp='/dev/disk/by-id/dm-uuid-LVM-'$vgu$lvu
echo $dmp

#Please use the below line, the other one is a place holder for older saturn server testing on VMs
#scstadmin -open_dev disk-${lvu:0:8} -handler vdisk_blockio -attributes filename=$dmp,thin_provisioned=1,rotational=0,write_through=1,blocksize=4096
scstadmin -open_dev disk-${lvu:0:8} -handler vdisk_blockio -attributes filename=$dmp
echo "add_target $2" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $2 allowed_portal $3" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $2 allowed_portal $4" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
#echo "add_target_attribute $2 nv_cache 1" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $2 blocksize 4096" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $2 thin_provisioned 1" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $2 rotational 0" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "add_target_attribute $2 write_through 1" >/sys/kernel/scst_tgt/targets/iscsi/mgmt
echo "create allowed_ini" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/mgmt
echo "add disk-${lvu:0:8} 0" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/allowed_ini/luns/mgmt
echo "add $5" >/sys/kernel/scst_tgt/targets/iscsi/$2/ini_groups/allowed_ini/initiators/mgmt
echo 1 >/sys/kernel/scst_tgt/targets/iscsi/$2/enabled

scstadmin -write_config /etc/scst.conf
echo "SUCCESS"

