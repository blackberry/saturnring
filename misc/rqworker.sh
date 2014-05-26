#!/bin/bash
source /home/vagrant/saturnring/saturnenv/bin/activate
python /home/vagrant/saturnring/ssddj/manage.py rqworker default
