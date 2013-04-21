# -*- coding: utf-8 -*-
import base64
import inspect
import json
import logging
import requests
import types

from django.conf import settings
from django.core.management import call_command
from django.utils.importlib import import_module
from django_nose import FastFixtureTestCase as DjangoTestCase
from functools import wraps
from mock import patch
from operator import itemgetter
from tastypie.test import (
    TestApiClient as TastypieTestApiClient,
    ResourceTestCase as TastypieResourceTestCase
)


INITIAL_DATA = ('initial_data', 'ficuspumila',)
TEST_DATA = ('test_data', 'ficuspumila',)
API_PATH = '/api/v1/core/'

logger = logging.getLogger(__name__)


def mock_request(self, method, url, **kwargs):
    client = TastypieTestApiClient()
    authentication = 'Basic %s' % base64.b64encode(':'.join([
        settings.FICUSPUMILA['SYSTEM_USERNAME'],
        settings.FICUSPUMILA['SYSTEM_PASSWORD'],
    ]))

    if method == 'GET':
        data = kwargs.get('params', {})
        djresponse = client.get(url, data=data, authentication=authentication)
    elif method == 'POST':
        data = json.loads(kwargs.get('data', '{}'))
        djresponse = client.post(url, data=data, authentication=authentication)
    elif method == 'PUT':
        data = json.loads(kwargs.get('data', '{}'))
        djresponse = client.put(url, data=data, authentication=authentication)
    elif method == 'PATCH':
        data = json.loads(kwargs.get('data', '{}'))
        djresponse = client.patch(url, data=data, authentication=authentication)
    elif method == 'DELETE':
        data = kwargs.get('params', {})
        djresponse = client.delete(url, data=data, authentication=authentication)

    # convert django.http.HttpResponse to requests.models.Response
    response = requests.models.Response()
    response.status_code = djresponse.status_code
    response.headers = {}
    try:
        response.headers['content-type'] = djresponse['content-type']
        response.headers['location'] = djresponse['location']
    except:
        pass
    response.encoding = requests.utils.get_encoding_from_headers(response.headers)
    response._content = djresponse.content

    return response

def mock_api(func, **decorator_kwargs):
    @patch.dict(settings.FICUSPUMILA, API_URL='/api/')
    @patch('requests.sessions.Session.request', mock_request)
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def mock_api_testcase(testcase=None):
    if testcase is None:
        return

    try:
        func_type = types.UnboundMethodType
    except:
        func_type = types.FunctionType
    for name, func in inspect.getmembers(testcase):
        if isinstance(func, func_type) and name.startswith('test_'):
            setattr(testcase, name, mock_api(func))


class TestCase(DjangoTestCase):

    fixtures = INITIAL_DATA

    def setUp(self):
        call_command('loaddata', *TEST_DATA)
        super(TestCase, self).setUp()


class ProxyTestCase(TestCase):

    pass


class ResourceTestCase(TestCase, TastypieResourceTestCase):

    version  = 1
    api_name = 'auth'
    resource_name = 'user'

    def setUp(self):
        super(ResourceTestCase, self).setUp()

        self.list_endpoint = '%s%s/%s/' % (API_PATH,
                                 self.api_name,
                                 self.resource_name,)
        self.detail_endpoint = '%s1/' % self.list_endpoint

    def get_credentials(self):
        return self.create_basic(username=settings.FICUSPUMILA['SYSTEM_USERNAME'],
                                 password=settings.FICUSPUMILA['SYSTEM_PASSWORD'])

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

        self.service = getattr(import_module('core.content.models'),
                               'Source').objects.get(pk=1)
        self.token = self.service.generate_token({'source_owner_id': ''})

        super(AuthTestCase, self).setup()
