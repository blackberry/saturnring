#!/bin/bash
apt-get update
apt-get install nfs-common -y
mkdir -p /sharedstuff
NFSIPPREFIX=$(ifconfig eth0 | awk '/inet / { print $2 }' | sed 's/addr://' | cut -d . -f4 --complement)
mount $NFSIPPREFIX.1:/home/local/rig6/saturnondriver/sharedstuff /sharedstuff
