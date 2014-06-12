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
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if  python $DIR/parsetarget.py | grep $1 | grep "no sessions"
then
        yes | scstadmin -rem_target $1 -driver iscsi
        TARGETMD5=`echo $1 | md5sum | cut -f1 -d" "`
        lvolName=lvol-${TARGETMD5:0:8}
        lvu=`lvdisplay $2/$lvolName | grep "LV UUID" | sed  's/LV UUID\s\{0,\}//g' | tr -d '-' | tr -d ' '`
        yes | scstadmin -close_dev disk-${lvu:0:8} -handler vdisk_blockio
        echo "Trying to remove LV "$lvolName
        yes | lvremove -f $2/$lvolName
        scstadmin -write_config /etc/scst.conf
else
        echo "Error deleting "$1" , doing nothing (check if target exists, is the session down?)"
fi

mkdir -p /temp
sudo cp /etc/scst.conf /temp
sudo cp /etc/lvm/backup/$6 /temp
sudo chmod  666 /temp/scst.conf
sudo chmod 666 /temp/$6

