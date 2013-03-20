# -*- coding: utf-8 -*-
import os                                            
import warnings

from .settings import *


gettext = lambda s: s


# debug
DEBUG = True
TEMPLATE_DEBUG = DEBUG


# version
APP_VERSION = '0.0.1'


# pathes
APP_ROOT = os.environ.get('APP_ROOT',
                          os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                       '../..')))


# admin
ADMINS = (
    ('Nobu', 'nobu@nk113.com'),
)
MANAGERS = ADMINS


# locale
TIME_ZONE = 'Asia/Tokyo'
LANGUAGES = (
    ('ja', gettext('Japanese')),
    ('en', gettext('English')),
)


# database
DATABASES_FOR_READ = ('default',)
DATABASES_FOR_WRITE = ('default',)
DATABASE_ROUTERS = ('settings.database.routers.Default',)
SYNCDB_ALLOWED = ('south',)


# cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
        'TIMEOUT': 60 * 15,
        'VERSION': APP_VERSION,
    }
}


# wsgi   
WSGI_APPLICATION = 'wsgi.local.application'


# apps
INSTALLED_APPS += (
    'django.contrib.admin',
    'south',
    'core.common',
)


# auth
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'core.auth.SSOBackend'
)


# tastypie
TASTYPIE_CANNED_ERROR = 'Oops, a catastrophic error has occurred!'


# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s: %(levelname)s: %(name)s: %(funcName)s (%(pathname)s l.%(lineno)d): %(process)d.%(thread)d] %(message)s'
        },
        'normal': {
            'format': '[%(asctime)s: %(levelname)s: %(name)s: %(funcName)s] %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s] %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'settings.logging.handlers.NullHandler',
            'formatter': 'normal',
        },
        'fluent': {
            'level': 'DEBUG',
            'class': 'settings.logging.handlers.FluentLabelHandler',
            'tag': 'ficuspumila.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'normal',
        },
        # 'sentry': {
        #     'level': 'ERROR',
        #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        # },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ('require_debug_false',),
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'django_log': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'normal',
            'filename': os.path.join(APP_ROOT, 'logs/django.log'),
        },
        'debug_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(APP_ROOT, 'logs/django-debug.log'),
        },
        'sql_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'simple',
            'filename': os.path.join(APP_ROOT, 'logs/django-sql.log'),
        },
        'test_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'normal',
            'filename': os.path.join(APP_ROOT, 'logs/django-test.log'),
        },
    },
    'loggers': {
        # defined in local.py
    }
}


# warnings
warnings.filterwarnings(action='ignore',
                        category=UserWarning,
                        module=r'tastypie.*')
warnings.filterwarnings(action='ignore',
                        category=DeprecationWarning,
                        module=r'core.*')


# core
SYSTEM_USERNAME = '<django auth username>'
SYSTEM_PASSWORD = '<django auth password>'
SERVICES = {
    'ficuspumila.core.content.api.proxies.Source': {
        'user': 'ficuspumila.core.content.api.proxies.Owner',
    },
    # 'core.product.models.Store': {
    #     'user': 'core.product.models.Consumer',
    # },
    # 'core.playready.models.Lisenser': {
    #     'user': 'core.playready.models.Licency',
    # },
}
CACHE_TIMEOUT = CACHES['default']['TIMEOUT']
TOKEN_TIMEOUT = 60 * 2
GC_DAYS_BEFORE = 60
GC_PROBABILITY = 0.1


# core.common
IPINFODB_API_URL = 'http://api.ipinfodb.com/v3/ip-country/'
IPINFODB_API_KEY = '<api key for ipinfodb>'
GEONAMES_COUNTRY_INFO = 'http://download.geonames.org/export/dump/countryInfo.txt'


# core.content


# core.product


# core.playready


# core.transaction


