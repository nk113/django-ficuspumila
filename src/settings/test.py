# -*- coding: utf-8 -*-                                     
from .local import *


# database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/dev/shm/api.db',
    }
}


# logging
LOGGING['loggers'] = {
    '': {
        'handlers': ['console', 'test_log'],
        'level': 'DEBUG',
        'propagate': True,
    },
    'django.request': {
        'handlers': [],
        'level': 'DEBUG',
        'propagate': True,
    },
}


# celery
CELERY_ALWAYS_EAGER = True


# test
# TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
