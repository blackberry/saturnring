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
"""
Django settings for ssddj project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ConfigParser
import ldap
from django_auth_ldap.config import LDAPSearch,_LDAPConfig,ActiveDirectoryGroupType
import logging
import traceback
import django_auth_ldap
import sys

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#DEBUG = False
config = ConfigParser.RawConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
config.read(os.path.join(BASE_DIR,'saturn.ini'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('saturnring','django_secret_key')

if (config.get('activedirectory','enabled')=='1'):
    print "Configuring AD"
    try:
        logger = logging.getLogger('django_auth_ldap')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
        AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
            'django_auth_ldap.backend.LDAPBackend',
        )
        AUTH_LDAP_USER_FLAGS_BY_GROUP = {
            "is_staff": config.get('activedirectory','staff_group').strip('"'),
        }
        AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()
        AUTH_LDAP_BIND_DN = config.get('activedirectory','bind_user_dn').strip('"')
        AUTH_LDAP_BIND_PASSWORD = config.get('activedirectory','bind_user_pw').strip('"')
        AUTH_LDAP_SERVER_URI = config.get('activedirectory','ldap_uri').strip('"')
        AUTH_LDAP_CONNECTION_OPTIONS = {
                ldap.OPT_DEBUG_LEVEL: 255,
                ldap.OPT_PROTOCOL_VERSION: 3,
                ldap.OPT_REFERRALS: 0,
        }
        AUTH_LDAP_USER_SEARCH = LDAPSearch(config.get('activedirectory','user_dn').strip('"'), ldap.SCOPE_SUBTREE, '(SAMAccountName=%(user)s)')
        # Populate the Django user from the LDAP directory.
        AUTH_LDAP_USER_ATTR_MAP = {
            "first_name": "displayName",
            "last_name": "cn",
            "email": "mail"
        }
        AUTH_LDAP_GROUP_SEARCH = LDAPSearch(config.get('activedirectory','staff_group').strip('"'), ldap.SCOPE_SUBTREE)
        AUTH_LDAP_ALWAYS_UPDATE_USER = True
        # Use LDAP group membership to calculate group permissions.
        AUTH_LDAP_FIND_GROUP_PERMS = True
        # Cache group memberships for an hour to minimize LDAP traffic
        AUTH_LDAP_CACHE_GROUPS = True
        AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600


    except:
        var = traceback.format_exc()
        print var
else:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )

TEMPLATE_INFO = True
ALLOWED_HOSTS = ['*']
TEMPLATE_DIRS = (
            os.path.join(BASE_DIR,  'templates'),
            )

# Application definition

INSTALLED_APPS = (
    'django_jenkins',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ssdfrontend',
    'south',
    'rest_framework',
    'api',
    'globalstatemanager',
    'utils',
    'admin_stats',
    'django_rq',
    'snapbackup'
)
#PROJECT_APPS = (
#    'ssdfrontend',
#    'api',
#    'utils',
#    'django.contrib.admin',
#    'globalstatemanager',
#)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.exceptions.PlainExceptionsMiddleware',
)

ROOT_URLCONF = 'ssddj.urls'

#WSGI_APPLICATION = 'ssddj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'saturndb.sqlite3'),
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'docker',
        'PASSWORD':'docker',
        'HOST': 'db_1',
        'PORT': 5432,
    }
}

#Recreating this database
#drop old db
#GRANT ALL on demodb.* TO saturnadmin@'saturnring.store.altus.bblabs'
#syncdb
#schema migration 



RQ_QUEUES = {
    'default': {
        'HOST': 'redis_1',
        'PORT': 6379,
        'DB': 0,
    },
}

numqueues = config.get('saturnring','numqueues')
for ii in range(0,int(numqueues)):
    RQ_QUEUES['queue'+str(ii)]={
            'HOST': 'redis_1',
            'PORT' : 6379,
            'DB': 0,
            'DEFAULT_TIMEOUT': 20,
            }



# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = '/var/www/saturnring/static/'
STATIC_URL = '/static/'
REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
#    'DEFAULT_PERMISSION_CLASSES': [
#        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
#    ]
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
#            'filename':  os.path.join(BASE_DIR, 'saturn.log'),
            'filename': os.path.join(BASE_DIR,config.get('saturnring','logpath'),'saturn.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'INFO',
        },
        'ssdfrontend': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'INFO',
        },
        'globalstatemanager': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'INFO',
        },
        'api': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}


from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
         'django.core.context_processors.request',
    )
