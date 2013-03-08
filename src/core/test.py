# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.test import TestCase
from tastypie.test import ResourceTestCase as TastypieResourceTestCase


FIXTURES = ('initial_data.json',)

logger = logging.getLogger(__name__)


class ResourceTestCase(TastypieResourceTestCase):
    fixtures = FIXTURES
    app_name = ''
    resource_name = ''

    def setUp(self):
        super(ResourceTestCase, self).setUp()

        self.list_endpoint = '/%s%s/%s/' % (settings.API_PATH,
                                            self.app_name,
                                            self.resource_name,)
        self.detail_endpoint = '%s1/' % self.list_endpoint

    def get_credentials(self):
        return self.create_basic(username=settings.SYSTEM_USERNAME,
                                 password=settings.SYSTEM_PASSWORD)

    def test_get_list_unauthorzied(self):
        r = self.api_client.get(self.list_endpoint)
        self.assertHttpUnauthorized(r)
        return r

    def test_get_list_json(self):
        r = self.api_client.get(self.list_endpoint,
                                authentication=self.get_credentials())
        self.assertValidJSONResponse(r)
        return r

    def test_get_detail_unauthenticated(self):
        r = self.api_client.get(self.detail_endpoint)
        self.assertHttpUnauthorized(r)
        return r

    def test_get_detail_json(self):
        r = self.api_client.get(self.detail_endpoint,
                                authentication=self.get_credentials())
        self.assertValidJSONResponse(r)
        return r
