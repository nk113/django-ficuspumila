# -*- coding: utf-8 -*-                                     
from .vagrant import *


# rpc_proxy
TASTYPIE_RPC_PROXY['SUPERUSER_USERNAME'] = 'test'
TASTYPIE_RPC_PROXY['SUPERUSER_PASSWORD'] = 'test'


# database
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'ficuspumila'
TEST_DATABASE_NAME = 'ficuspumila-test.db'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/dev/shm/api.db',
    }
}


# urls
ROOT_URLCONF = 'urls.test'


# apps
INSTALLED_APPS += (
    'django_nose',
    # 'ficuspumila.apps.example,
)


# logging
LOGGING['loggers'] = {
    '': {
        'handlers': ('console',),
        'level': 'CRITICAL',
        'propagate': True,
    },
}


# celery
CELERY_ALWAYS_EAGER = True


# test
# TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ('--with-fixture-bundling',
             # '--failed',
             # '--stop',
             )
