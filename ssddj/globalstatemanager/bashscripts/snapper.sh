#!/bin/bash
set -e
VGNAME=$1
LVNAME=$2
TARGETNAME=$3
#Number of processors devided by 4 - this is the maximum we want to spare for pigz at any time
PROCSBY4=$( echo `grep -c ^processor /proc/cpuinfo`/8  | bc)
if [ ! -f /dev/$1/$2-snap ];
then
        lvcreate  -s -n $2-snap $1/$2
fi
pv /dev/$1/$2-snap | pigz --fast --rsyncable --processes $PROCSBY4 > $3-_-$1-_-$2.gzip
lvremove -f $1/$2-snap

