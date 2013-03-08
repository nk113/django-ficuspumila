# -*- coding: utf-8 -*-
import logging

from core.proxies import Proxy


logger = logging.getLogger(__name__)


class ContentProxy(Proxy):

    api_name = 'content'
