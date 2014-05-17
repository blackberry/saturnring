#!/bin/bash
source /home/vagrant/saturnring/godjango/bin/activate
python /home/vagrant/saturnring/ssddj/manage.py rqworker default
