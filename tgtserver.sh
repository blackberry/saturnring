#!/bin/bash
rm /etc/apt/sources.list
cat <<EOF > /etc/apt/sources.list.d/localrepo.list
deb http://repo.bblabs/ubuntu trusty universe multiverse main restricted
deb-src http://repo.bblabs/ubuntu trusty universe multiverse main restricted

deb http://repo.bblabs/ubuntu trusty-updates universe multiverse main restricted
deb-src http://repo.bblabs/ubuntu trusty-updates universe multiverse main restricted

deb http://repo.bblabs/ubuntu trusty-security universe multiverse main restricted
deb-src http://repo.bblabs/ubuntu trusty-security universe multiverse main restricted

EOF

apt-get update
apt-get install tgt lvm2 sysstat -y

mkdir -p /loopdatadev$HOSTNAME
if [ ! -f /loopdatadev$HOSTNAME/file-nothin.img ]; then
  dd if=/dev/zero of=/loopdatadev$HOSTNAME/file-nothin.img bs=1MiB count=10000 && sync
fi

DEV=`losetup --find --show /loopdatadev$HOSTNAME/file-nothin.img`
sleep 5
#VG setup
pvcreate $DEV
vgcreate vg-one $DEV
vgs
#the logical volumes are not thin provisioned.
