# -*- coding: utf-8 -*-
import logging

from ficuspumila.core.proxy import get, Proxy


logger = logging.getLogger(__name__)


class UserProxy(Proxy):

    pass


class CountryProxy(Proxy):

    pass


User    = get('User', 'django.contrib.auth.models')
Country = get('Country', 'ficuspumila.core.common.models')
