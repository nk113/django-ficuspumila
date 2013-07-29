# -*- coding: utf-8 -*-
import logging

from rpc_proxy.test import TestCase
from tastypie.test import ResourceTestCase

from ficuspumila.settings import ficuspumila as settings


API_PATH = '/api/v1/core/'

logger = logging.getLogger(__name__)


class Resource(TestCase, ResourceTestCase):
    """
    Don't be smart so much in test cases!
    """

    api_name = 'auth'
    resource_name = 'user'

    def setUp(self):
        super(Resource, self).setUp()

        self.list_endpoint = '%s%s/%s/' % (API_PATH,
                                 self.api_name,
                                 self.resource_name,)
        self.detail_endpoint = '%s1/' % self.list_endpoint

    def get_credentials(self):
        return self.create_basic(username=settings('SUPERUSER_USERNAME'),
                                 password=settings('SUPERUSER_PASSWORD'))

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
