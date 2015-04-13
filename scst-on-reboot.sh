#!/bin/bash
# Insert this script to run via rc.local, e.g. during reboot

#This is for the testing VMs where the PVs are loop devices
losetup --find --show /loopdatadeviscsiserver1/file-nothin.img; losetup --find --show /loopdatadeviscsiserver1/file-thin.img
sleep 5
sudo vgs

#Read the crypttab and start the disk
while read encdev; do
  devName=`echo $encdev | cut -d" " -f1`
  devStr="encrypted"
  if /bin/grep -q $devStr <<<$devName; then
        echo $devName
        /usr/sbin/cryptdisks_start $devName;
  fi
done < /etc/crypttab

#Start SCST now, it should come up as the entries in crypttab are now open
service scst start

