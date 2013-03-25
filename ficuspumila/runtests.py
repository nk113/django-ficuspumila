# -*- coding: utf-8 -*-
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.test'
sys.path.insert(0, os.path.dirname(__file__))

from django.conf import settings
from django.test.utils import get_runner

def runtests():
    runner = get_runner(settings)(verbosity=1, interactive=True)
    sys.exit(bool(runner.run_tests(('ficuspumila',))))

if __name__ == '__main__':
    runtests()
