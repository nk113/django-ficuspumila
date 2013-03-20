# -*- coding: utf-8 -*-
import logging

from core.proxy import get, Proxy


logger = logging.getLogger(__name__)


class UserProxy(Proxy):

    pass


class CountryProxy(Proxy):

    pass


User    = get('User', 'django.contrib.auth.models')
Country = get('Country', 'core.common.models')
