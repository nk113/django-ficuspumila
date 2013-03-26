# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.utils.unittest import skipIf

from ficuspumila.core.api.proxies import Country
from ficuspumila.core.exceptions import ProxyException
from ficuspumila.core.test import TestCase


logger = logging.getLogger(__name__)


class CountryTestCase(TestCase):

    # FIXME: how do I get this decorator to work?
    @skipIf(not getattr(settings, 'IPINFODB_API_KEY', False),
            u'"IPINFODB_API_KEY" is not defined in settings, skipping...')
    def test_get_by_ip(self):
        try:
            c = Country.get_by_ip('183.177.146.33')

            self.assertEqual(c.name, 'Japan')
            self.assertEqual(c.alpha2, 'JP')
        except ProxyException, e:

            logger.debug(u'"IPINFODB_API_KEY" is not defined in settings, skipping...')
