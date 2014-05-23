#!/bin/bash
apt-get install open-iscsi curl
cp /vagrant/clientscripts/storage-provisioner.sh /home/vagrant/storage-provisioner.sh
cp /vagrant/clientscripts/README-client /home/vagrant/
chown vagrant:vagrant /home/vagrant/storage-provisioner.sh
chmod +x /home/vagrant/storage-provisioner.sh

