# -*- coding: utf-8 -*-
import logging

from ficuspumila.core.test import ResourceTestCase


logger = logging.getLogger(__name__)


class UserResourceTestCase(ResourceTestCase):

    api_name = 'auth'
    resource_name = 'user'
