# -*- coding: utf-8 -*-
import logging
import math
import os
import requests
import StringIO

from django.conf import settings
from django.utils import timezone

from ficuspumila.core import fixture


logger = logging.getLogger(__name__)


class Generator(fixture.Generator):

    fixture = '%s/initial_data.json' % os.path.dirname(__file__)

    def update_objects(self):
        pass
