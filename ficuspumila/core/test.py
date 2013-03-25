# -*- coding: utf-8 -*-
import inspect
import json
import logging
import os

from django.conf import settings
from django.core.management import call_command
from django.utils.importlib import import_module
from django_nose import FastFixtureTestCase as DjangoTestCase
from operator import itemgetter
from tastypie.test import ResourceTestCase as TastypieResourceTestCase


INITIAL_DATA = ('initial_data', 'ficuspumila',)
TEST_DATA = ('test_data', 'ficuspumila',)
API_PATH = '/api/v1/'

logger = logging.getLogger(__name__)


class TestCase(DjangoTestCase):

    fixtures = INITIAL_DATA

    def setUp(self):
        call_command('loaddata', *TEST_DATA, verbosity=2)
        super(TestCase, self).setUp()


class ResourceTestCase(TestCase, TastypieResourceTestCase):

    version  = 1
    api_name = 'core'
    resource_name = 'user'

    def setUp(self):
        super(ResourceTestCase, self).setUp()

        self.list_endpoint = '%s%s/%s/' % (API_PATH,
                                 self.api_name,
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


class AuthTestCase(TestCase):

    def setUp(self):

        self.service = getattr(import_module('core.content.common.models'),
                               'Source').objects.get(pk=1)
        self.token = self.service.generate_token({'source_owner_id': ''})

        super(AuthTestCase, self).setup()
