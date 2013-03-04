# -*- coding: utf-8 -*-
import logging

from core.proxies import get, Proxy
from . import models


logger = logging.getLogger(__name__)


class UserProxy(Proxy):
    pass


class CountryProxy(Proxy):

    @staticmethod
    def get_by_ip(ip):
        return models.Country.get_by_ip(ip)


User    = get('User')
Country = get('Country')
