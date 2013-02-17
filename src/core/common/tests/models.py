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
        c = Country.objects.get(pk='IN')

        self.assertEqual(c.name, 'India')

    def test_get_csv_fields(self):
        c = Country.objects.get(pk='ZW')

        self.assertEqual(type(c.languages) == list, True)
        self.assertEqual(type(c.neighbours) == list, True)

    def test_set_csv_fields(self):
        c = Country.objects.get(pk='ZW')
        c.languages = ['ja',]
        c.neighbours = ['JP',]
        c.save()

        self.assertEqual(type(c.languages) == list, True)
        self.assertEqual(c.languages[0], 'ja')
        self.assertEqual(c.neighbours[0], 'JP')

    def test_get_by_ip(self):
        c = Country.get_by_ip('183.177.146.33')

        self.assertEqual(c.name, 'Japan')
        self.assertEqual(c.alpha2, 'JP')
