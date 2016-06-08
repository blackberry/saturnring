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


#Modify this for your setup - this is the $DIRROOT/saturnring directory on the host; absolute path is required.
HOSTNFSDIR=/home/local/rig6/saturnring

mv /etc/apt/sources.list /etc/apt/sources


apt-get install nfs-common -y
mkdir -p /vagrant
NFSIPPREFIX=$(ifconfig eth0 | awk '/inet / { print $2 }' | sed 's/addr://' | cut -d . -f4 --complement)
mount $NFSIPPREFIX.1:$HOSTNFSDIR /vagrant
sleep 1
. /vagrant/devenv/envvars.sh
apt-get update
apt-get install -y apache2 python-dev python-pip redis-server git python-virtualenv sqlite3 libsqlite3-dev supervisor libapache2-mod-wsgi curl libsasl2-dev libldap2-dev libpq-dev

mkdir -p $SATURNWKDIR/saturnringlog
chown $INSTALLUSER:$INSTALLUSER $SATURNWKDIR/saturnringlog


mkdir -p $SATURNWKDIR/saturnringconfig
chown $INSTALLUSER:$INSTALLUSER $SATURNWKDIR/saturnringconfig

mkdir -p /var/www/saturnring
chown -R $INSTALLUSER:$INSTALLUSER /var/www

mkdir -p $DATABASE_DIR
chown $INSTALLUSER:$INSTALLUSER $DATABASE_DIR

mkdir -p $INSTALLLOCATION
chown $INSTALLUSER:$INSTALLUSER $INSTALLLOCATION

sudo -u $INSTALLUSER -H bash -c "cd /vagrant; ./devenv/saturnring_postbootup_as_"$INSTALLUSER"_user.sh"

cd $INSTALLLOCATION/ssddj
rm /etc/supervisor/conf.d/saturnworker.conf
COUNTMAX=`expr $NUMWORKERS - 1`
for ii in `seq 0 $COUNTMAX`;
do
  cat <<EOF >> /etc/supervisor/conf.d/saturnworker.conf
[program:django-rqworker-$ii]
command=$INSTALLLOCATION/saturnenv/bin/python $INSTALLLOCATION/ssddj/manage.py rqworker queue$ii
user=$INSTALLUSER
stdout_logfile=$SATURNWKDIR/saturnringlog/rqworker-$ii.log
redirect_stderr=true
stopasgroup=true
numprocs=1
stopsignal=TERM
autostart=true
autorestart=true

EOF
done
cat <<EOF > /etc/supervisor/conf.d/logserver.conf
[program:logserver]
command=python $INSTALLLOCATION/ssddj/logserver/logserver.py
user=$INSTALLUSER
stopasgroup=true
EOF


rm /etc/apache2/sites-enabled/000-default.conf
cat <<EOF > /etc/apache2/sites-available/saturnring.conf
<VirtualHost *:$SATURNRINGAPACHEPORT>
  LogLevel warn
  CustomLog $SATURNWKDIR/saturnringlog/access.log combined
  ErrorLog $SATURNWKDIR/saturnringlog/error.log
        ServerAdmin saturnadmin@yourdomain.com
        ServerName $SATURNRINGHOST
        WSGIScriptAlias / /var/www/saturnring/index.wsgi
        WSGIDaemonProcess $INSTALLUSER  user=$INSTALLUSER
        WSGIProcessGroup $INSTALLUSER
        WSGIPassAuthorization On
        Alias /static/ /var/www/saturnring/static/
        <Location "/static/">
            Options -Indexes
        </Location>
    <Directory /var/www/saturnring>
      Order allow,deny
      Allow from all
    </Directory>
</VirtualHost>

EOF

ln -s /etc/apache2/sites-available/saturnring.conf /etc/apache2/sites-enabled/saturnring.conf

#chown -R www-data:www-data  $DATABASE_DIR
service apache2 restart

service supervisor stop
service supervisor start

