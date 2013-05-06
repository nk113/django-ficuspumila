# -*- coding: utf-8 -*-                                     
from .vagrant import *


# ficuspumila
FICUSPUMILA['SYSTEM_USERNAME'] = 'test'
FICUSPUMILA['SYSTEM_PASSWORD'] = 'test'


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


# apps
INSTALLED_APPS += (
    'django_nose',
)
INSTALLED_APPS = tuple(app for app in INSTALLED_APPS if not app == 'djcelery')


# logging
LOGGING['loggers'] = {
    '': {
        'handlers': ('test_log',),
        'level': 'INFO',
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
