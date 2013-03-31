# -*- coding: utf-8 -*-
import logging

from ficuspumila.core.proxies import get, Proxy


logger = logging.getLogger(__name__)


class UserProxy(Proxy):

    pass


User = get('User', 'django.contrib.auth.models')
