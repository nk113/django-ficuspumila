# -*- coding: utf-8 -*-
import logging

from ficuspumila.core import test


logger = logging.getLogger(__name__)


class UserResource(test.Resource):

    api_name = 'auth'
    resource_name = 'user'
