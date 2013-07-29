# -*- coding: utf-8 -*-
import djcelery

from .common import *


# rpc_proxy
TASTYPIE_RPC_PROXY['SUPERUSER_USERNAME'] = 'dev'
TASTYPIE_RPC_PROXY['SUPERUSER_PASSWORD'] = 'dev'


# ficuspumila
FICUSPUMILA['META_TYPES'] = ((0, 'Track',), (1, 'Album',), (2, 'Video',),)
FICUSPUMILA['META_PROXIES_MODULE'] = 'ficuspumila.apps.example.proxies'


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
