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
source /vagrant/devenv/envvars.sh

cd $INSTALLLOCATION
#Get latest saturnringsoftware from master branch
#git clone https://github.com/sachinkagarwal/saturnring/
cd $INSTALLLOCATION
if [ $INSTALLLOCATION != $CODEROOT ]; then
  cp -R $CODEROOT .
fi
if [ ! -d "$INSTALLLOCATION/saturnenv" ]; then
  virtualenv saturnenv
fi
cd $INSTALLLOCATION/ssddj
source $INSTALLLOCATION/saturnenv/bin/activate

pip install  -r $INSTALLLOCATION/python-virtualenv-requirements.txt --allow-external django-admin-changelist-stats  --allow-unverified django-admin-changelist-stats

cat <<EOF > $INSTALLLOCATION/ssddj/saturn.ini
[saturnring]
#Cluster name used in the GUI and XLS stats file output
clustername=$CLUSTERNAME


#Location where the Saturnring picks up scripts to install 
#on the iscsi server(saturnnode) for things like creating/deleting iSCSI targets
bashscripts=globalstatemanager/bashscripts/

#The user needs to copy the corresponding public key to the saturn node's user 
#(specified in the [saturnnode] section using e.g. ssh-copy-id
privatekeyfile=$SATURNWKDIR/saturnringconfig/saturnkey

#This is where saturnring keeps the latest iscsi config file
iscsiconfigdir=$SATURNWKDIR/saturnringconfig/

#Django secret key (CHANGE in production)
django_secret_key=$DJANGOSECRETKEY

#Logging path
logpath=$SATURNWKDIR/saturnringlog
logfile=saturn.log
#Server that accepts pickled sockethandler log messages and puts them in the log gui+saves them
logserverhost=localhost
logwebmonitorport=9021
logfilerotatesize=50000000
logfilerotatecount=10


#Number of queues. A higher number will create more worker processes;
#Useful for clusters with many iSCSI servers. Note that each iSCSI server
#is always serviced by the same worker, so increasing this number will not
#speed up a single-iSCSI server cluster. The parameter is useful when many
#iSCSI servers are serviced by the same number of limited workers/
numqueues=$NUMWORKERS

#Proxyfolder
#This is the proxy subfolder if the application is being run behind a proxy.
#Used to manage appropriate BASE URLs
proxyfolder=$PROXYFOLDER

#Database settings
[database]

#sqlite or postgres
dbtype=$DATABASE_TYPE
dbname=$DATABASE_NAME
dbdir=$DATABASE_DIR
#These parameters are only applicable to postgres
dbhost=$DATABASE_HOST
dbport=$DATABASE_PORT
dbuser=$DATABASE_USER
dbpassword=$DATABASE_PASSWORD

#iSCSI server settings (also referred to as saturnnode or storage host)
#All iSCSI servers are assumed to have identical configurations
[saturnnode]
user=$INSTALLUSER
#Location on the saturnnode where the scripts are installed.
install_location=/home/vagrant/saturn/
bashpath=/bin/bash
pythonpath=/usr/bin/python

#LDAP/AD settings
[activedirectory]
enabled=$LDAP_ENABLED
ldap_uri=$LDAP_LDAP_URI
user_dn=$LDAP_USER_DN
staff_group=$LDAP_STAFF_GROUP
bind_user_dn=$LDAP_BIND_USER_DN
bind_user_pw=$LDAP_BIND_USER_PW

#Configuration to run unit tests.
[tests]
saturnringip=$SATURNRINGHOST
saturnringport=80
saturniscsiserver=192.168.56.21

EOF

python manage.py syncdb --noinput
python manage.py convert_to_south ssdfrontend
python manage.py schemamigration ssdfrontend --auto
python manage.py migrate


cd $INSTALLLOCATION/ssddj
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '$ADMINEMAIL', '$SATURNRINGPASSWORD')" | python manage.py shell

cat <<EOF > /var/www/saturnring/index.wsgi
import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('$INSTALLLOCATION/saturnenv/$INSTALLUSER/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('$INSTALLLOCATION/ssddj')
sys.path.append('$INSTALLLOCATION/ssddj/ssddj')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ssddj.settings'

# Activate your virtual env
activate_env=os.path.expanduser("$INSTALLLOCATION/saturnenv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
#Commented out above 2 lines, and added these for Django19
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

EOF
python manage.py collectstatic --noinput


#This little bit uses cron to keep updating stats within the application
rm mycron
if [ ! -f mycron ];then
        crontab -l > mycron
        #echo new cron into cron file
 	echo "12 22 * * * cd $INSTALLLOCATION/ssddj/; source ../saturnenv/bin/activate; python manage.py cleanup && echo 'vacuum (analyze, verbose);' | python manage.py dbshell" >> mycron
        echo "* * * * *  curl -X GET http://$SATURNRINGHOST:$SATURNRINGAPACHEPORT/api/stateupdate/" >> mycron
        #install new cron file
        crontab mycron
fi
git config --global user.email "$INSTALLUSER@changeme.com"
git config --global user.name "$INSTALLUSER"

# Create new keys
CONFIGDIR=$SATURNWKDIR/saturnringconfig
sudo -E mkdir -p $CONFIGDIR
sudo -E chown $INSTALLUSER:$INSTALLUSER $CONFIGDIR
cd $CONFIGDIR
git init
ssh-keygen -q -f saturnkey -N ''
ssh-keygen -f saturnkey.pub -e -m pem > saturnkey.pem
#dd if=/dev/random of=~/cryptokeyfile bs=8 count=1

# Write out the cryptokey to the config directory
echo "$CRYPTOKEY" > "$CONFIGDIR"/cryptokey

git add *
git commit -a -m "Created Saturn keys"

