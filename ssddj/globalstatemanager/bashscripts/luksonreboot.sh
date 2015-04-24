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

