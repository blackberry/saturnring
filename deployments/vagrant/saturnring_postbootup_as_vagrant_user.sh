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

cd /home/$USER
#Get latest saturnringsoftware from master branch
git clone https://github.com/sachinkagarwal/saturnring/

cd /home/$USER/saturnring
if [ ! -d "/home/$USER/saturnring/saturnenv" ]; then
  virtualenv saturnenv
fi
cd /home/$USER/saturnring/ssddj
source /home/$USER/saturnring/saturnenv/bin/activate
pip install -r /home/$USER/saturnring/python-virtualenv-requirements.txt --allow-external django-admin-changelist-stats  --allow-unverified django-admin-changelist-stats

python manage.py syncdb --noinput
python manage.py convert_to_south ssdfrontend
python manage.py schemamigration ssdfrontend --auto
python manage.py migrate

cat <<EOF > /home/$USER/saturnring/redisqconf/rqworker.sh
#!/bin/bash
source /home/$USER/saturnring/saturnenv/bin/activate
python /home/$USER/saturnring/ssddj/manage.py rqworker default

EOF

cat <<EOF > /var/www/saturnring/index.wsgi
import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/$USER/saturnring/saturnenv/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/$USER/saturnring/ssddj')
sys.path.append('/home/$USER/saturnring/ssddj/ssddj')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ssddj.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/home/$USER/saturnring/saturnenv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

EOF
python manage.py collectstatic --noinput


#This little bit uses cron to keep updating stats within the application
if [ ! -f mycron ];then
        crontab -l > mycron
        #echo new cron into cron file
        echo "* * * * *  curl -X GET http://$SATURNRINGHOST:$SATURNRINGAPACHEPORT/api/stateupdate/" >> mycron
        #install new cron file
        crontab mycron
fi

# Create new keys
CONFIGDIR=$SATURNRINGHOST/saturnconfig
sudo mkdir -p $CONFIGDIR
sudo chown $USER:$USER $CONFIGDIR
cd $CONFIGDIR
git init
ssh-keygen -q -f saturnkey -N ''
ssh-keygen -f saturnkey.pub -e -m pem > saturnkey.pem
git add *
git commit -a -m "Created Saturn keys"

