#!/bin/bash
#No trainling slashes in the directroy arguments please
set -e
VGNAME=$1
LVNAME=$2
TARGETDIR=$3
NFSDIR=$4
VERSION=$5
#Number of processors devided by 4 - this is the maximum we want to spare for pigz at any time
PROCSBY4=$( echo `grep -c ^processor /proc/cpuinfo`/4  | bc)

if [ ! -f /dev/$VGNAME/$LVNAME-snap ];
then
        lvcreate  -s -n $LVNAME-snap $VGNAME/$LVNAME
fi

#Setup tempstorage to hold the tempsnap
if [ ! -f /dev/$VGNAME/tempsnapvol ];
then
        lvcreate -V250G -T $VGNAME/thinpool -n tempsnapvol
fi

mkfs.ext4 -F /dev/$VGNAME/tempsnapvol
mkdir -p  $TARGETDIR
mount /dev/$VGNAME/tempsnapvol $TARGETDIR

#Do the pv/gzip
pv /dev/$VGNAME/$LVNAME-snap | pigz --rsyncable --fast --processes $PROCSBY4 > $TARGETDIR/$VGNAME-_-$LVNAME-_-$VERSION.gzip
#pv /dev/$VGNAME/$LVNAME-snap | gzip --rsyncable  > $TARGETDIR/$VGNAME-_-$LVNAME.gzip
lvremove -f $VGNAME/$LVNAME-snap
rsync -avzh $TARGETDIR/$VGNAME-_-$LVNAME-_-$VERSION.gzip $NFSDIR/$VGNAME-_-$LVNAME-_-$VERSION.gzip
umount /dev/$VGNAME/tempsnapvol
lvremove -f $VGNAME/tempsnapvol


