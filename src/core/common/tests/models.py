# -*- coding: utf-8 -*-
import logging

from django.test import TestCase

from core.common.models import (
    Country, Currency
)


logger = logging.getLogger(__name__)


class BaseTestCase(TestCase):
    fixtures = ('initial_data.yaml',)

    def setUp(self):
        pass

    def tearDown(self):
        pass


class CountryTestCase(BaseTestCase):

    def test_get(self):
        c = Country.objects.get(name__startswith='Indi')

        self.assertEqual(c.name_caps, 'INDIA')
        self.assertEqual(c.alpha2, 'IN')

    def test_get_by_ip(self):
        c = Country.get_by_ip('183.177.146.33')

        self.assertEqual(c.name_caps, 'JAPAN')
        self.assertEqual(c.alpha2, 'JP')


class CurrencyTestCase(BaseTestCase):

    def test_get(self):
        c = Currency.objects.get(code='JPY')

        self.assertEqual(c.name, 'Japanese Yen')
        self.assertEqual(c.decimal_place, 0)

    def test_price_format(self):
        c = Currency.objects.get(code='JPY')


