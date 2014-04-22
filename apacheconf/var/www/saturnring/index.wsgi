import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/local/ssddj/saturnring/godjango/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/local/ssddj/saturnring/ssddj')
sys.path.append('/home/local/ssddj/saturnring/ssddj/ssddj')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ssddj.settings'

# Activate your virtual env
activate_env=os.path.expanduser("/home/local/ssddj/saturnring/godjango/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
