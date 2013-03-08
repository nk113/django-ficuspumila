# -*- coding: utf-8 -*-
import logging

from core.proxies import get, CoreProxy


logger = logging.getLogger(__name__)


class UserProxy(CoreProxy):

    pass


class CountryProxy(CoreProxy):

    pass


User    = get('User', 'django.contrib.auth.models')
Country = get('Country', 'core.common.models')
