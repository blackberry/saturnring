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

source ./envvars.sh

apt-get update
apt-get install -y apache2 python-dev python-pip redis-server git python-virtualenv sqlite3 libsqlite3-dev supervisor libapache2-mod-wsgi curl libsasl2-dev libldap2-dev
mkdir -p $SATURNWKDIR/saturnringlog
chown $USER:$USER $SATURNWKDIR/saturnringlog


mkdir -p /var/www/saturnring
chown -R $USER:$USER /var/www


sudo -u $USER -H bash -c "cd /$USER; ./saturnring_postbootup_as_$USER_user.sh"

cd /home/$USER/saturnring/ssddj
rm /etc/supervisor/conf.d/saturnworker.conf
for ii in `seq 1 $NUMWORKERS`;
do
  cat <<EOF >> /etc/supervisor/conf.d/saturnworker.conf
  [program:django-rqworker-$ii]
  command=/home/$USER/saturnring/misc/rqworker.sh queue$ii
  user=$USER
  stdout_logfile=$SATURNWKDIR/saturnringlog/rqworker-$ii.log
  redirect_stderr=true
  
EOF
done


cat <<EOF > /etc/apache2/sites-available/saturnring.conf
<VirtualHost *:$SATURNRINGAPACHEPORT>
  LogLevel warn
  CustomLog $SATURNWKDIR/saturnringlog/access.log combined
  ErrorLog $SATURNWKDIR/saturnringlog/error.log
        ServerAdmin saturnadmin@yourdomain.com
        ServerName $SATURNRINGHOST
        WSGIScriptAlias / /var/www/saturnring/index.wsgi
        WSGIDaemonProcess $USER  user=$USER
        WSGIProcessGroup $USER
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

service apache2 restart

service supervisor stop
service supervisor start

