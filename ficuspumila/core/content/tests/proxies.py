# -*- coding: utf-8 -*-
import inspect
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.unittest import skipIf
from mock import patch
from queryset_client import client

from ficuspumila.core.exceptions import ProxyException
from ficuspumila.core.proxies import get as get_proxy
from ficuspumila.core.test import (
    mock_api_testcase, ProxyTestCase,
)


PROXY_MODULE = 'ficuspumila.core.content.proxies'
TEST_SOURCE_ATTIRBUTE   = 'DELETE_SOURCE_RESOURCE_ON_ITEM_READY'
TEST_FILESPEC_ATTIRBUTE = 'WIDTH'

logger = logging.getLogger(__name__)


class SourceProxyTestCase(ProxyTestCase):

    def test_get(self):
        Source = get_proxy('Source', proxy_module=PROXY_MODULE)

        s = Source.objects.get(user__username=settings.FICUSPUMILA['SYSTEM_USERNAME'])
        self.assertEqual(s.user.username, settings.FICUSPUMILA['SYSTEM_USERNAME'])
        return s

    def test_getattr(self):
        s = self.test_get()
        self.assertEqual(s.getattr(TEST_SOURCE_ATTIRBUTE) is None, True)
        return s

    def test_setattr(self):
        s = self.test_get()

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: s.setattr('SHITHEAD', 'blah'))

        s.setattr(TEST_SOURCE_ATTIRBUTE, 'True')
        self.assertEqual(s.getattr(TEST_SOURCE_ATTIRBUTE), 'True')

        return s

    def test_delattr(self):
        s = self.test_setattr()

        s.delattr(TEST_SOURCE_ATTIRBUTE)
        self.test_getattr()

        self.assertRaises(KeyError, lambda: s.delattr('SHITHEAD'))

        return s


class SourceProxyApiTestCase(SourceProxyTestCase):

    pass

mock_api_testcase(SourceProxyApiTestCase)
