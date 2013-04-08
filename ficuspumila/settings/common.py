# -*- coding: utf-8 -*-
import os                                            
import warnings

from .settings import *


# ficuspumila
FICUSPUMILA = {
    # version
    'APP_VERSION': '0.0.1',
    # pathes
    'APP_ROOT': os.environ.get('APP_ROOT',
                               os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                            '../..'))),
    # database
    'DATABASES_FOR_READ' : ('default',),
    'DATABASES_FOR_WRITE': ('default',),
    'SYNCDB_ALLOWED'     : ('south',),
    # core
    #'API_URL': '<url of the api server, https connection is strongly recommended for security>',
    'SYSTEM_USERNAME': '<django auth username>',
    'SYSTEM_PASSWORD': '<django auth password>',
    'SERVICES': {
        'ficuspumila.core.content.proxies.Source': {
            'user': 'ficuspumila.core.content.proxies.Owner',
        },
        # 'core.product.models.Store': {
        #     'user': 'core.product.models.Consumer',
        # },
        # 'core.playready.models.Lisenser': {
        #     'user': 'core.playready.models.Licency',
        # },
    },
    'CACHE_TIMEOUT' : 60 * 15,
    'TOKEN_TIMEOUT' : 60 * 2,
    'GC_DAYS_BEFORE': 60,
    'GC_PROBABILITY': 0.1,
    # core.common
    'IPINFODB_API_URL': 'http://api.ipinfodb.com/v3/ip-country/',
    'IPINFODB_API_KEY': '<api key for ipinfodb>',
    'GEONAMES_COUNTRY_INFO': 'http://download.geonames.org/export/dump/countryInfo.txt',
    # core.content
    # core.product
    # core.playready
    # core.transaction
}


gettext = lambda s: s


# debug
DEBUG = True
TEMPLATE_DEBUG = DEBUG


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
DATABASE_ROUTERS = ('settings.database.routers.Default',)


# cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:11211',
        'TIMEOUT': FICUSPUMILA['CACHE_TIMEOUT'],
        'VERSION': FICUSPUMILA['APP_VERSION'],
    }
}


# secrets
SECRET_KEY = '<overwrite with some unique value>'


# wsgi   
WSGI_APPLICATION = 'wsgi.local.application'


# apps
INSTALLED_APPS += (
    'django.contrib.admin',
    'queued_storage',
    'south',
)


# auth
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'ficuspumila.core.auth.backends.SSO',
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
            'filename': os.path.join(FICUSPUMILA['APP_ROOT'], 'logs/django.log'),
        },
        'debug_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(FICUSPUMILA['APP_ROOT'], 'logs/django-debug.log'),
        },
        'sql_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'simple',
            'filename': os.path.join(FICUSPUMILA['APP_ROOT'], 'logs/django-sql.log'),
        },
        'test_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'normal',
            'filename': os.path.join(FICUSPUMILA['APP_ROOT'], 'logs/django-test.log'),
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
