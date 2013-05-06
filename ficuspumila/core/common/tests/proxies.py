# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils.unittest import skipIf
from mock import patch
from queryset_client import client

from ficuspumila.core.exceptions import ProxyException
from ficuspumila.core.proxies import get as get_proxy
from ficuspumila.core.test import (
    mock_api_testcase, ProxyTestCase,
)
from ficuspumila.settings import (
    get as settings_get,
    ficuspumila as settings,
)


PROXY_MODULE = 'ficuspumila.core.common.proxies'

logger = logging.getLogger(__name__)


def query_country_code(ip):
    return 'JP'


class CountryProxyTestCase(ProxyTestCase):

    # FIXME: how do I get this decorator to work?
    # @skipIf(settings('IPINFODB_API_KEY') is None,
    #         u'"IPINFODB_API_KEY" is not defined in settings, skipping...')
    # @patch('ficuspumila.core.common.proxies.Country.query_country_code', query_country_code)
    # def test_get_by_ip(self):
    #     c = Country.get_by_ip('183.177.146.33')

    #     self.assertEqual(c.name, 'Japan')
    #     self.assertEqual(c.alpha2, 'JP')
    # pass

    def test_get(self):
        Country = get_proxy('Country', proxy_module=PROXY_MODULE)

        c = Country.objects.get(alpha2='ZW')
        self.assertEqual(c.name, 'Zimbabwe')

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: Country.objects.get(name='crazymonkey'))

        return c

    def test_get_csv_fields(self):
        c = self.test_get()

        self.assertEqual(type(c.languages), list)
        self.assertEqual(type(c.neighbours), list)

    def test_set_csv_fields(self):
        c = self.test_get()

        c.languages.append('ja')
        c.neighbours = ['JP']
        c.save()

        self.assertEqual(type(c.languages), list)
        self.assertEqual(c.languages.pop(), 'ja')
        self.assertEqual(c.neighbours.pop(), 'JP')


class CountryApiProxyTestCase(CountryProxyTestCase):

    pass

mock_api_testcase(CountryApiProxyTestCase)
