#!/bin/bash
apt-get install open-iscsi curl -y
cp /vagrant/clientscripts/storage-provisioner.sh /home/vagrant/storage-provisioner.sh
chown vagrant:vagrant /home/vagrant/storage-provisioner.sh
cp /vagrant/clientscripts/README-client /home/vagrant/
chmod +x /home/vagrant/storage-provisioner.sh

