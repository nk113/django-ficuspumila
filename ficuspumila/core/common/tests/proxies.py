# -*- coding: utf-8 -*-
import inspect
import logging

from django.conf import settings
from django.utils.unittest import skipIf
from mock import patch

from ficuspumila.core.exceptions import ProxyException
from ficuspumila.core.proxies import get as get_proxy
from ficuspumila.core.test import (
    mock_api_testcase, ProxyTestCase,
)


PROXY_MODULE = 'ficuspumila.core.common.proxies'

logger = logging.getLogger(__name__)


def query_country_code(ip):
    return 'JP'


class CountryProxyTestCase(ProxyTestCase):

    # FIXME: how do I get this decorator to work?
    # @skipIf('IPINFODB_API_KEY' not in settings.FICUSPUMILA,
    #         u'"IPINFODB_API_KEY" is not defined in settings, skipping...')
    # @patch('ficuspumila.core.common.proxies.Country.query_country_code', query_country_code)
    # def test_get_by_ip(self):
    #     c = Country.get_by_ip('183.177.146.33')

    #     self.assertEqual(c.name, 'Japan')
    #     self.assertEqual(c.alpha2, 'JP')
    # pass

    def test_get_csv_fields(self):
        Country = get_proxy('Country', proxy_module=PROXY_MODULE)

        c = Country.objects.get(alpha2='ZW')

        self.assertEqual(type(c.languages) == list, True)
        self.assertEqual(type(c.neighbours) == list, True)

    def test_set_csv_fields(self):
        Country = get_proxy('Country', proxy_module=PROXY_MODULE)

        c = Country.objects.get(alpha2='ZW')
        c.languages = ['ja',]
        c.neighbours = ['JP',]
        c.save()

        self.assertEqual(type(c.languages) == list, True)
        self.assertEqual(c.languages[0], 'ja')
        self.assertEqual(c.neighbours[0], 'JP')


class CountryProxyApiTestCase(CountryProxyTestCase):

    pass

mock_api_testcase(CountryProxyApiTestCase)
