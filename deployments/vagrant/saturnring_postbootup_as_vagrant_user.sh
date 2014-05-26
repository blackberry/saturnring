#!/bin/bash
cd /home/vagrant
git clone -b localrun http://gitlab.rim.net/ssd/saturnring.git

cd /home/vagrant/saturnring
if [ ! -d "/home/vagrant/saturnring/saturnenv" ]; then
  virtualenv saturnenv
fi
cd /home/vagrant/saturnring/ssddj
source /home/vagrant/saturnring/saturnenv/bin/activate
pip install -r /home/vagrant/saturnring/python-virtualenv-requirements.txt --allow-external django-admin-changelist-stats  --allow-unverified django-admin-changelist-stats

python manage.py syncdb --noinput
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
python manage.py collectstatic --noinput

#This little bit uses cron to keep updating stats within the application
if [ ! -f mycron ];then
        crontab -l > mycron
        #echo new cron into cron file
        echo "* * * * *  curl -X GET http://192.168.61.20/api/stateupdate/" >> mycron
        #install new cron file
        crontab mycron
fi

