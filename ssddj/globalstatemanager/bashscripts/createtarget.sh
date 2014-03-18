#!/bin/bash
#CAPACITY=`vgdisplay storevg | grep "Free  PE / Size" | cut -d'/' -f 3 | cut -d' ' -f 2 |tr -d ' '`
TOTALCAP=`lvs | grep "\s\sthinpool*" | cut -d" " -f10- | tr -d " " | cut -d"g" -f1`
PERCENTUSED=`lvs | grep "\s\sthinpool*" | cut -d" " -f10- | tr -d " " | cut -d"g" -f2`
GBAVL=`echo "$TOTALCAP*(100-$PERCENTUSED)/100" | bc`
echo "$GBAVL"
echo "$1"
echo "$2"
if [ `echo "$1 < $GBAVL" | bc`==1 ]; then
    echo "Capacity available, creating LV"
    cstr=`lvcreate -V${1}G -T storevg/thinpool`
    echo "LVCREATE: $cstr"
    lvolName=`echo $cstr | grep -o '\".*\"' | sed -e 's/\"//g'`
    scstadmin -add_target $2 -driver iscsi
    scstadmin -open_dev disk-${lvolName} -handler vdisk_blockio -attributes filename=/dev/storevg/$lvolName,nv_cache=1
    scstadmin -add_lun 0 -driver iscsi -target $2 -device disk-${lvolName}
    scstadmin -enable_target $2 -driver iscsi
    scstadmin -write_config /etc/scst.conf
    echo "SUCCESS"
else
    echo "Cannot create LV, capacity exceeded"
    exit 1
fi

