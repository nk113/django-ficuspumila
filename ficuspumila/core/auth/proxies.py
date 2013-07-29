# -*- coding: utf-8 -*-
import logging

from django.contrib.auth import models
from rpc_proxy import proxies


logger = logging.getLogger(__name__)


class User(proxies.Proxy):

    class Meta:

        model = models.User
