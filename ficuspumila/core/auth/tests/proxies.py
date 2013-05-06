# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist
from queryset_client import client

from ficuspumila.core.exceptions import ProxyException
from ficuspumila.core.proxies import get as get_proxy
from ficuspumila.core.test import (
    mock_api_testcase, ProxyTestCase
)
from ficuspumila.core.utils import to_python
from ficuspumila.settings import ficuspumila as settings


PROXY_MODULE = 'ficuspumila.core.auth.proxies'

logger = logging.getLogger(__name__)


class UserProxyTestCase(ProxyTestCase):

    def test_get(self):
        User = get_proxy('User', 'django.contrib.auth.models', PROXY_MODULE)

        u = User.objects.get(username=settings('SYSTEM_USERNAME'))
        self.assertEqual(u.username, settings('SYSTEM_USERNAME'))
        self.assertEqual(to_python(u.is_superuser), True)

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: User.objects.get(username='crazymonkey'))

        return u


class UserApiProxyTestCase(UserProxyTestCase):

    pass

mock_api_testcase(UserApiProxyTestCase)
