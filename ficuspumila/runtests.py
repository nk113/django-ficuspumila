# -*- coding: utf-8 -*-
import os
import sys

DJANGO_SETTINGS_MODULE = sys.argv[1] if len(sys.argv) > 1 else 'settings.test'

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = os.environ.get('DJANGO_SETTINGS_MODULE',
                                                      DJANGO_SETTINGS_MODULE)

from django.conf import settings
from django.test.utils import get_runner

def runtests():
    runner = get_runner(settings)(verbosity=1, interactive=True)
    sys.exit(bool(runner.run_tests(('ficuspumila',))))

if __name__ == '__main__':
    runtests()
