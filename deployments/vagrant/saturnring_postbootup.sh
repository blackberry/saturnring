sudo apt-get update
sudo apt-get install -y apache2 python-dev python-pip redis-server git python-virtualenv sqlite3 libsqlite3-dev
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
python manage.py runserver 0.0.0.0:8000

