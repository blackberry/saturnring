
#!/bin/bash

export http_proxy="http://proxy.bblabs:80"
export https_proxy="https://proxy.bblabs:80"
apt-get install ruby-dev sqlite3 fabric -y 
gem install json
mv /usr/lib/ruby/1.9.1/json.rb /usr/lib/ruby/1.9.1/json.rb.no
echo "deb http://downloads.opennebula.org/repo/4.14/Ubuntu/14.04 stable opennebula" > /etc/apt/sources.list.d/opennebula.list
wget -q -O- http://downloads.opennebula.org/repo/Debian/repo.key | apt-key add -
apt-get update
apt-get install opennebula-sunstone opennebula -y

#Problem with automating this script: - Y and enter and y needed
/usr/share/one/install_gems


echo "Stopping one"
sudo -H -u oneadmin bash -c 'one stop'
echo "Creating some shared directories"
mkdir -p /onedbfolder
chown oneadmin:oneadmin /onedbfolder
mkdir -p /sharedstuff
chown -R oneadmin:oneadmin /sharedstuff
echo "Mounting nfs shares"
NFSIPPREFIX=$(ifconfig eth0 | awk '/inet / { print $2 }' | sed 's/addr://' | cut -d . -f4 --complement)
cat <<EF >> /etc/fstab
$NFSIPPREFIX.1:/home/local/rig7/saturnring/saturn-opennebula-driver/on-devenv/ontestbed/oneds0 /var/lib/one/datastores/0 nfs
$NFSIPPREFIX.1:/home/local/rig7/saturnring/saturn-opennebula-driver/on-devenv/ontestbed/oneds1 /var/lib/one/datastores/1 nfs
$NFSIPPREFIX.1:/home/local/rig7/saturnring/saturn-opennebula-driver/on-devenv/ontestbed/onedbfolder /onedbfolder nfs
EF
mount -a
echo "SSH keys"
cp /sharedstuff/sshkeys.tar.gz /var/lib/one
chown oneadmin:oneadmin /var/lib/one/sshkeys.tar.gz
sudo -H -u oneadmin bash -c 'cd /var/lib/one; tar -xvzf sshkeys.tar.gz'

#one start
echo "Starting one"
sudo -H -u oneadmin bash -c 'one start'
echo "Done!"
exit 0


