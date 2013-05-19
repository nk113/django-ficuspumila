# -*- coding: utf-8 -*-
import logging

from django.contrib.auth import models

from ficuspumila.core import proxies


logger = logging.getLogger(__name__)


class User(proxies.Proxy):

    class Meta:

        model = models.User
