# -*- coding: utf-8 -*-
import os                                            
import warnings

from Crypto.pct_warnings import RandomPool_DeprecationWarning

from .settings import *


gettext = lambda s: s


# debug
DEBUG = True
TEMPLATE_DEBUG = DEBUG


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


# wsgi   
WSGI_APPLICATION = 'wsgi.local.application'


# core.common
API_VERSION = 'v1'
IPINFODB_API_URL = 'http://api.ipinfodb.com/v3/ip-country/'
IPINFODB_API_KEY = 'a1b1ce36d81cf0cbadc82f5f087584a7bdd8f21212f87c63de2236acd47b5bef'


# apps
INSTALLED_APPS += (
    'django.contrib.admin',
)


# core.content


# core.product


# core.playready


# core.transaction


# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s: %(levelname)s/%(name)s(%(process)d.%(thread)d)] %(message)s'
        },
        'normal': {
            'format': '[%(asctime)s: %(levelname)s/%(name)s] %(message)s'
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
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'django_log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'normal',
            'filename': os.path.join(APP_ROOT, 'logs/django.log'),
        },
        'debug_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(APP_ROOT, 'logs/django_debug.log'),
        },
        'sql_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': os.path.join(APP_ROOT, 'logs/django_sql.log'),
        },
        'test_log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'normal',
            'filename': os.path.join(APP_ROOT, 'logs/django_test.log'),
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
                        module=r'lib.crypto')
warnings.filterwarnings(action='ignore',
                        category=RandomPool_DeprecationWarning,
                        module=r'Crypto.Util.randpool')
