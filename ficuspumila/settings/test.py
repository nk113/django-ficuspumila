# -*- coding: utf-8 -*-                                     
from .local import *


# database
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


# logging
LOGGING['loggers'] = {
    '': {
        'handlers': ('console', 'test_log',),
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
             '--failed',
             '--stop',
             )

# core
API_URL = None
SYSTEM_USERNAME = 'test'
SYSTEM_PASSWORD = 'test'
