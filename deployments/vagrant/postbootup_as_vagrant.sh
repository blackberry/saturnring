#!/bin/bash
cd /home/vagrant
git clone http://gitlab.rim.net/ssd/saturnring.git
cat <<EOF > /home/vagrant/saturnring/pyton-virtualenv-requirements.txt
Django==1.6.2
Markdown==2.4
PyYAML==3.10
South==0.8.4
argparse==1.2.1
distribute==0.6.24
django-admin-changelist-stats==0.2
django-filter==0.7
django-rq==0.6.1
djangorestframework==2.3.13
ecdsa==0.11
paramiko==1.13.0
pycrypto==2.6.1
pysqlite==2.6.3
python-dateutil==2.2
pytz==2014.2
redis==2.9.1
rq==0.3.13
rq-scheduler==0.4.0
six==1.6.1
times==0.6.2
wsgiref==0.1.2

EOF

cd /home/vagrant/saturnring
if [ ! -d "/home/vagrant/saturnring/saturnenv" ]; then
  virtualenv saturnenv
fi
cd /home/vagrant/saturnring/ssddj
source /home/vagrant/saturnring/saturnenv/bin/activate
pip install -r python-virtualenv-requirements.txt --allow-external django-admin-changelist-stats  --allow-unverified django-admin-changelist-stats

python manage.py syncdb
python manage.py convert_to_south ssdfrontend
python manage.py schemamigration ssdfrontend --auto
python manage.py migrate

cat <<EOF > /home/vagrant/saturnring/redisqconf/rqworker.sh
#!/bin/bash
source /home/vagrant/saturnring/saturnenv/bin/activate
python /home/vagrant/saturnring/ssddj/manage.py rqworker default

EOF

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

#This little bit uses cron to keep updating stats within the application
if [ ! -f mycron ];then
        crontab -l > mycron
        #echo new cron into cron file
        echo "* * * * *  curl -X GET http://localhost/api/stateupdate/" >> mycron
        #install new cron file
        crontab mycron
fi

