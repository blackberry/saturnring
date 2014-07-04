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
config = ConfigParser.RawConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
print str(BASE_DIR)
config.read(os.path.join(BASE_DIR,'saturn.ini'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('saturnring','django_secret_key')

# SECURITY WARNING: don't run with debug turned on in production!
INFO = True


TEMPLATE_INFO = True
ALLOWED_HOSTS = ['*']
TEMPLATE_DIRS = (
            os.path.join(BASE_DIR,  'templates'),
            )

# Application definition

INSTALLED_APPS = (
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
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ssddj.urls'

#WSGI_APPLICATION = 'ssddj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'saturndb.sqlite3'),
    }
}

#DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': 'saturndb',                      # Or path to database file if using sqlite3.
       # The following settings are not used with sqlite3:
#         'USER': 'postgres',
#         'PASSWORD': 'passw0rd',
#         'HOST': '172.19.20.32',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
#         'PORT': '',                      # Set to empty string for default.
#     }
#}



#Recreating this database
#drop old db
#GRANT ALL on demodb.* TO saturnadmin@'saturnring.store.altus.bblabs'
#syncdb
#schema migration 



RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
}

numqueues = config.get('saturnring','numqueues')
for ii in range(0,int(numqueues)):
    RQ_QUEUES['queue'+str(ii)]={
            'HOST': 'localhost',
            'PORT' : 6379,
            'DB': 0,
            }



# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEBUG = True

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
            'level':'WARNING',
        },
        'ssdfrontend': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
        'globalstatemanager': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
        'api': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
    }
}


from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
         'django.core.context_processors.request',
    )
