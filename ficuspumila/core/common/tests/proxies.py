# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.utils.unittest import skipIf
from mock import patch

from ficuspumila.core.common.proxies import Country
from ficuspumila.core.exceptions import ProxyException
from ficuspumila.core.test import TestCase


logger = logging.getLogger(__name__)


def query_country_code(ip):
    return 'JP'


class CountryTestCase(TestCase):

    # FIXME: how do I get this decorator to work?
    # @skipIf('IPINFODB_API_KEY' not in settings.FICUSPUMILA,
    #         u'"IPINFODB_API_KEY" is not defined in settings, skipping...')
    # @patch('ficuspumila.core.common.proxies.Country.query_country_code', query_country_code)
    # def test_get_by_ip(self):
    #     c = Country.get_by_ip('183.177.146.33')

    #     self.assertEqual(c.name, 'Japan')
    #     self.assertEqual(c.alpha2, 'JP')
    pass
