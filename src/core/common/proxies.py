# -*- coding: utf-8 -*-
import logging

from core.proxies import get, Proxy
from . import models


logger = logging.getLogger(__name__)


class UserProxy(Proxy):
    pass


class CountryProxy(Proxy):
    pass


User    = get('User')
Country = get('Country')
