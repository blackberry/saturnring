#!/bin/bash
CAPACITY=`vgdisplay storevg | grep "Free  PE / Size" | cut -d'/' -f 3 | cut -d' ' -f 2 |tr -d ' '`
if [ `echo "$1 < $CAPACITY" | bc` == 1 ]; then
    echo "Capacity available, creating LV"
    cstr=`lvcreate -V${1}G -T storevg/thinpool`
    echo $cstr
    lvolName=`echo $cstr | grep -o '\".*\"' | sed -e 's/\"//g'`
    scstadmin -add_target $2 -driver iscsi
    scstadmin -open_dev disk-${lvolName} -handler vdisk_blockio -attributes filename=/dev/storevg/$lvolName,nv_cache=1
    scstadmin -add_lun 0 -driver iscsi -target $2 -device
    scstadmin -enable_target $2 -driver iscsi
    scstadmin -write_config /etc/scst.conf
else
    echo "Cannot create LV, capacity exceeded"
    exit 1
fi
