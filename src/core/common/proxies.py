# -*- coding: utf-8 -*-
import logging

from core.proxies import get, Proxy
from . import models


logger = logging.getLogger(__name__)


class CountryProxy(Proxy):
    pass


Country = get('Country')
