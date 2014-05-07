#!/bin/bash
if  python /home/local/saturn/saturn-bashscripts/parsetarget.py | grep $1 | grep "no sessions"
then
        yes | scstadmin -rem_target $1 -driver iscsi
        TARGETMD5=`echo $1 | md5sum | cut -f1 -d" "`
        lvolName=lvol-${TARGETMD5:0:8}
        echo "Trying to remove LV "$lvolName
        yes | lvremove -f $2/$lvolName
        scstadmin -write_config /etc/scst.conf
else
        echo "Error deleting "$1" , doing nothing (check if target exists, is the session down?)"
fi

