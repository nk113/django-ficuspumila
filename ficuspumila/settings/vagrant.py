# -*- coding: utf-8 -*-
import djcelery

from .common import *


# ficuspumila
FICUSPUMILA['SYSTEM_USERNAME'] = 'dev'
FICUSPUMILA['SYSTEM_PASSWORD'] = 'dev'


# debug
DEBUG = True
TAMPLATE_DEBUG = DEBUG


# databse
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ficuspumila',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


# cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
        'VERSION': FICUSPUMILA['APP_VERSION'],
    }
}


# urls
ROOT_URLCONF = 'urls.vagrant'


# apps
INSTALLED_APPS += (
    'djcelery',
    'ficuspumila.core.auth',
    'ficuspumila.core.common',
    'ficuspumila.core.content',
)


# logging
LOGGING['loggers'] = {
    '': {
        'handlers': ('console', 'debug_log', 'django_log',),
        'level': 'DEBUG',
        'propagate': True,
    },
    'django.db.backends': {
        'handlers': ('console', 'sql_log',),
        'level': 'DEBUG',
        'propagate': False,
    },
}


# celery
djcelery.setup_loader()
