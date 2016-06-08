
#!/bin/bash
export http_proxy="http://proxy.bblabs:80"
export https_proxy="https://proxy.bblabs:80"
echo "deb http://downloads.opennebula.org/repo/4.14/Ubuntu/14.04 stable opennebula" > /etc/apt/sources.list.d/opennebula.list
wget -q -O- http://downloads.opennebula.org/repo/Debian/repo.key | apt-key add -
apt-get update
apt-get install opennebula-node bridge-utils -y

apt-get install open-iscsi openvswitch-switch -y
RANDOM=144362421121951
cat <<EF > /etc/iscsi/initiatorname.iscsi
InitiatorName=iqn.iscsihypervisor3140128870.ini
EF
service open-iscsi restart

NFSIPPREFIX=$(ifconfig eth0 | awk '/inet / { print $2 }' | sed 's/addr://' | cut -d . -f4 --complement)
mkdir -p /var/lib/one/datastores/0
chown oneadmin:oneadmin /var/lib/one/datastores/0
mkdir -p /var/lib/one/datastores/1
chown oneadmin:oneadmin /var/lib/one/datastores/1
cat <<EF >> /etc/fstab
$NFSIPPREFIX.1:/home/local/rig7/saturnring/saturn-opennebula-driver/on-devenv/ontestbed/oneds0 /var/lib/one/datastores/0 nfs
$NFSIPPREFIX.1:/home/local/rig7/saturnring/saturn-opennebula-driver/on-devenv/ontestbed/oneds1 /var/lib/one/datastores/1 nfs
EF
mount -a
echo "SSH keys"
cp /sharedstuff/sshkeys.tar.gz /var/lib/one
chown oneadmin:oneadmin /var/lib/one/sshkeys.tar.gz
sudo -H -u oneadmin bash -c 'cd /var/lib/one; tar -xvzf sshkeys.tar.gz'

#OVS configuration - assumes eth1 has to be reassigned to the bridge
#Assume /24
#Assume gateway is at .1
PHYDEV="eth1"
ovs-vsctl add-br onebridge
ifconfig onebridge up
IPADDR=$(ifconfig ${PHYDEV} | awk '/inet / { print $2 }' | sed 's/addr://')
GWPREFIX=$(ifconfig ${PHYDEV} | awk '/inet / { print $2 }' | sed 's/addr://' | cut -d . -f4 --complement)
ip addr del ${IPADDR}/24 dev ${PHYDEV}
ovs-vsctl add-port onebridge ${PHYDEV}
ifconfig onebridge ${IPADDR} netmask 255.255.255.0
ifconfig ${PHYDEV} 0
route del default
route add default gw ${GWPREFIX}.1 dev onebridge

