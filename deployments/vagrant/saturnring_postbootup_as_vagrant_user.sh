
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

#!/bin/bash
cd /home/vagrant
git clone https://github.com/sachinkagarwal/saturnring/

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

# Create new keys
mkdir -p /home/vagrant/saturnring/ssddj/config
cd /home/vagrant/saturnring/ssddj/config
ssh-keygen -q -f saturnkey -N ''
ssh-keygen -f saturnkey.pub -e -m pem > saturnkey.pem

