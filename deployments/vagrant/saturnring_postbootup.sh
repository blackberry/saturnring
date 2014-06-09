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


apt-get update
apt-get install -y apache2 python-dev python-pip redis-server git python-virtualenv sqlite3 libsqlite3-dev supervisor libapache2-mod-wsgi curl
mkdir -p /nfsmount/saturnringlog
chown vagrant:vagrant /nfsmount/saturnringlog


mkdir -p /var/www/saturnring
chown -R vagrant:vagrant /var/www


sudo -u vagrant -H bash -c "cd /vagrant; ./saturnring_postbootup_as_vagrant_user.sh"

cd /home/vagrant/saturnring/ssddj
cat <<EOF > /etc/supervisor/conf.d/saturnworker.conf
[program:django-rqworker-1]
command=/home/vagrant/saturnring/misc/rqworker.sh queue1
user=vagrant
stdout_logfile=/nfsmount/saturnringlog/rqworker-1.log
redirect_stderr=true

[program:django-rqworker-2]
command=/home/vagrant/saturnring/misc/rqworker.sh queue2
user=vagrant
stdout_logfile=/nfsmount/saturnringlog/rqworker-2.log
redirect_stderr=true

[program:django-rqworker-3]
command=/home/vagrant/saturnring/misc/rqworker.sh queue3
user=vagrant
stdout_logfile=/nfsmount/saturnringlog/rqworker-3.log
redirect_stderr=true

[program:django-rqworker-4]
command=/home/vagrant/saturnring/misc/rqworker.sh queue4
user=vagrant
stdout_logfile=/nfsmount/saturnringlog/rqworker-4.log
redirect_stderr=true

[program:django-rqworker-5]
command=/home/vagrant/saturnring/misc/rqworker.sh queue5
user=vagrant
stdout_logfile=/nfsmount/saturnringlog/rqworker-5.log
redirect_stderr=true
EOF
cat <<EOF > /etc/apache2/sites-available/saturnring.conf
<VirtualHost *:80>
  LogLevel warn
  CustomLog /nfsmount/saturnringlog/access.log combined
  ErrorLog /nfsmount/saturnringlog/error.log
        ServerAdmin saturnadmin@yourdomain.com
        ServerName 192.168.61.20
        WSGIScriptAlias / /var/www/saturnring/index.wsgi
        WSGIDaemonProcess vagrant  user=vagrant
        WSGIProcessGroup vagrant
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

