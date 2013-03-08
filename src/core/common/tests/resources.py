# -*- coding: utf-8 -*-
from core.test import ResourceTestCase


class CountryResourceTestCase(ResourceTestCase):
    app_name = 'common'
    resource_name = 'country'

    def setUp(self):
        super(CountryResourceTestCase, self).setUp()

        self.detail_endpoint = '%sjp/' % self.list_endpoint

    def test_get_list_unauthorzied(self):
        pass

    def test_get_detail_unauthenticated(self):
        pass
