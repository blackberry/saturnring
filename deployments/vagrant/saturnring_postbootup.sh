#!/bin/bash
apt-get update
apt-get install -y apache2 python-dev python-pip redis-server git python-virtualenv sqlite3 libsqlite3-dev supervisor libapache2-mod-wsgi curl
mkdir -p /nfsmount/saturnringlog
chown vagrant:vagrant /nfsmount/saturnringlog


sudo -u vagrant -H bash -c "cd /vagrant; ./postbootup_as_vagrant.sh" 

cd /home/vagrant/saturnring/ssddj
cat <<EOF > /etc/supervisor/conf.d/saturnworker.conf
[program:django-rqworker-1]
command=/home/vagrant/saturnring/redisqconf/rqworker.sh
user=vagrant
stdout_logfile=/nfsmount/saturnringlog/rqworker-1.log
redirect_stderr=true


[program:django-rqworker-2]
command=/home/vagrant/saturnring/redisqconf/rqworker.sh
user=vagrant
stdout_logfile=/nfsmount/saturnringlog/rqworker-2.log
redirect_stderr=true


[program:django-rqworker-3]
command=/home/vagrant/saturnring/redisqconf/rqworker.sh
user=vagrant
stdout_logfile=/nfsmount/saturnringlog/rqworker-3.log
redirect_stderr=true



[program:django-rqworker-4]
command=/home/vagrant/saturnring/redisqconf/rqworker.sh
user=vagrant
stdout_logfile=/nfsmount/saturnringlog/rqworker-4.log
redirect_stderr=true

EOF

mkdir -p /var/www/saturnring
chown -R vagrant:vagrant /var/www

cat <<EOF > /etc/apache2/sites-available/saturnring
<VirtualHost *:80>
  LogLevel warn
  CustomLog /nfsmount/saturnringlog/access.log combined
  ErrorLog /nfsmount/saturnringlog/error.log
        ServerAdmin saturnadmin@yourdomain.com
        ServerName saturnring
        ServerAlias www.saturnring.labs
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

ln -s /etc/apache2/sites-available/saturnring /etc/apache2/sites-enabled/000-default 

service apache2 restart

service supervisor stop
service supervisor start

