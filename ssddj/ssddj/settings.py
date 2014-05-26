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
            'level':'INFO',
        },
        'ssdfrontend': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'globalstatemanager': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'api': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    }
}


from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
         'django.core.context_processors.request',
    )
