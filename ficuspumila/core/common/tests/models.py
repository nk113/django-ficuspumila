# -*- coding: utf-8 -*-
import logging

from ficuspumila.core.test import TestCase
from ficuspumila.core.common.models import Country


logger = logging.getLogger(__name__)


class CountryTestCase(TestCase):

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
