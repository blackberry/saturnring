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
#set -e

service scst status
[ $? -ne 0 ] && echo "FAILURE, SCST not loaded on $HOSTNAME" && exit

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if  python $DIR/parsetarget.py | grep $1 | grep "no sessions"
then
        lvolName=$3
        VG=`vgdisplay -c | grep $2 | cut -d: -f1 | tr -d ' '`
        lvu=`lvdisplay $VG/$lvolName | grep "LV UUID" | sed  's/LV UUID\s\{0,\}//g' | tr -d '-' | tr -d ' '`
        
        #SCST
        yes | scstadmin -rem_target $1 -driver iscsi
        yes | scstadmin -close_dev disk-${lvu:0:8} -handler vdisk_blockio
        scstadmin -write_config /etc/scst.conf
        sudo mkdir -p /temp
        sudo cp /etc/scst.conf /temp
        sudo chmod  666 /temp/scst.conf

        #LVM - disk deletion
        echo "Trying to remove LV "$lvolName 
        if [ -b /dev/mapper/encrypted_$lvolName ]; then
          cryptsetup luksClose /dev/mapper/encrypted_$lvolName
          #remove cryptographic header backup
          rm /cryptbackups/$lvolName.cryptbackup.img
        fi
        #Zero the first 2MB to remove any metadata
        dd if=/dev/zero of=/dev/$VG/$lvolName bs=1M count=2 && sync 
        #Remove any tail metadata - 2MB
        dd if=/dev/zero of=/dev/$VG/$lvolName bs=512 count=400 seek=$(($(blockdev --getsz /dev/$VG/$lvolName)  - 400))
        yes | lvremove -f $VG/$lvolName
        sudo cp /etc/lvm/backup/$VG /temp/$2
        sudo chmod 666 /temp/$2
else
        echo "Error deleting "$1" , doing nothing (check if target exists, is the session down?)"
fi


