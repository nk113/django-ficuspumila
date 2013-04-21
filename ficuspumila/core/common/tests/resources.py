# -*- coding: utf-8 -*-
from ficuspumila.core.test import ResourceTestCase


class CountryResourceTestCase(ResourceTestCase):
    api_name = 'common'
    resource_name = 'country'

    def setUp(self):
        super(CountryResourceTestCase, self).setUp()

        self.detail_endpoint = '%sJP/' % self.list_endpoint
