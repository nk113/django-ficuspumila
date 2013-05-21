# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist
from queryset_client import client

from ficuspumila.core.exceptions import ProxyException
from ficuspumila.core import test
from ficuspumila.core.utils import to_python
from ficuspumila.settings import ficuspumila as settings


logger = logging.getLogger(__name__)


class UserProxy(test.Proxy):

    def test_get(self):
        from ficuspumila.core.auth.proxies import User

        u = User.objects.get(username=settings('SYSTEM_USERNAME'))
        self.assertEqual(u.username, settings('SYSTEM_USERNAME'))
        self.assertEqual(to_python(u.is_superuser), True)

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: User.objects.get(username='crazymonkey'))

        return u
