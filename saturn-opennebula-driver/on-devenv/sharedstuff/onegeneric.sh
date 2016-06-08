#!/bin/bash
cat <<EF > /etc/apt/sources.list
deb http://repo.bblabs/ubuntu trusty main restricted universe
deb http://repo.bblabs/ubuntu trusty-updates main restricted universe
deb http://repo.bblabs/ubuntu trusty-security main restricted universe
EF
apt-get update
export http_proxy="http://proxy.bblabs:80"
export https_proxy="https://proxy.bblabs:80"
apt-get install nfs-common fabric -y
mkdir -p /sharedstuff
NFSIPPREFIX=$(ifconfig eth0 | awk '/inet / { print $2 }' | sed 's/addr://' | cut -d . -f4 --complement)
cat <<EF >> /etc/fstab
$NFSIPPREFIX.1:/home/local/rig7/saturnring/saturn-opennebula-driver/on-devenv/sharedstuff /sharedstuff nfs
EF
mount -a

