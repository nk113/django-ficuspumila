# -*- coding: utf-8 -*-        
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


# urls
ROOT_URLCONF = 'urls.vagrant'


# apps
INSTALLED_APPS += (
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
    'django.request': {
        'handlers': ('mail_admins',),
        'level': 'DEBUG',
        'propagate': True,
    },
    'django.db.backends': {
        'handlers': ('console', 'sql_log',),
        'level': 'DEBUG',
        'propagate': False,
    },
}
