#!/bin/bash
source /home/local/ssddj/saturnring/godjango/bin/activate
python /home/local/ssddj/saturnring/ssddj/manage.py rqworker default
