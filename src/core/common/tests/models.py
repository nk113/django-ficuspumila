# -*- coding: utf-8 -*-
import logging

from django.test import TestCase

from core.common.models import Country


logger = logging.getLogger(__name__)


class BaseTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


class CountryTestCase(BaseTestCase):

    def test_get(self):
        c = Country.objects.get(name__startswith='Indi')

        self.assertEqual(c.name, 'India')
        self.assertEqual(c.alpha2, 'IN')

    def test_get_by_ip(self):
        c = Country.get_by_ip('183.177.146.33')

        self.assertEqual(c.name, 'Japan')
        self.assertEqual(c.alpha2, 'JP')
