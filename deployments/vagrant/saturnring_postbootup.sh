sudo apt-get update
sudo apt-get install -y apache2 python-dev python-pip redis-server git python-virtualenv sqlite3 libsqlite3-dev supervisor libapache2-mod-wsgi curl
cd /home/vagrant
git clone -b external http://gitlab.rim.net/ssd/saturnring.git
cd /home/vagrant/saturnring
virtualenv saturnenv
source ./saturnenv/bin/activate
pip install -r python-virtualenv-requirements.txt --allow-external django-admin-changelist-stats  --allow-unverified django-admin-changelist-stats
sudo mkdir -p /nfsmount/saturnringlog
sudo chown vagrant:vagrant /nfsmount/saturnringlog
cd /home/vagrant/saturnring/ssddj
rm db.sqllite3
python manage.py syncdb
python manage.py convert_to_south ssdfrontend
python manage.py schemamigration ssdfrontend --auto
python manage.py migrate

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

cat <<EOF > /var/www/saturnring/index.wsgi
import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/vagrant/saturnring/saturnenv/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/vagrant/saturnring/ssddj')
sys.path.append('/home/vagrant/saturnring/ssddj/ssddj')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ssddj.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/home/vagrant/saturnring/saturnenv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

EOF
python manage.py collectstatic

service apache2 restart

service supervisor stop
service supervisor start

#This little bit uses cron to keep updating stats within the application
if [ ! -f mycron ];then
        crontab -l > mycron
        #echo new cron into cron file
        echo "* * * * *  curl -X GET http://localhost/api/stateupdate/" >> mycron
        #install new cron file
        crontab mycron
fi

