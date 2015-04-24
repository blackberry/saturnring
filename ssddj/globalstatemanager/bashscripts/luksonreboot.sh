#!/bin/bash
# Insert this script to run via rc.local, e.g. during reboot

#This is for the testing VMs where the PVs are loop devices
#Remove lines between #START and #STOP for the case when the 
#block device already exists, or the rc.local wont work on reboot
#START
losetup --find --show /loopdatadeviscsiserver1/file-nothin.img; losetup --find --show /loopdatadeviscsiserver1/file-thin.img
sleep 5
sudo vgs

service cryptdisks force-start
#Start SCST now, it should come up as the entries in crypttab are now open
service scst start

