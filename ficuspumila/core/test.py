# -*- coding: utf-8 -*-
import base64
import django
import inspect
import json
import logging
import requests
import types

from django.core.management import call_command
from django_nose import FastFixtureTestCase
from functools import wraps
from mock import patch
from operator import itemgetter
from tastypie.test import ResourceTestCase, TestApiClient 

from ficuspumila.settings import ficuspumila as settings
from .proxies import invalidate


INITIAL_DATA = ('initial_data', 'ficuspumila',)
TEST_DATA = ('test_data', 'ficuspumila',)
API_PATH = '/api/v1/core/'

logger = logging.getLogger(__name__)


def mock_request(obj, method, url, **kwargs):
    client = TestApiClient()
    authentication = 'Basic %s' % base64.b64encode(':'.join([
        settings('SYSTEM_USERNAME'),
        settings('SYSTEM_PASSWORD'),
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

def mock_cache_set(key, value, timeout=None):
    # do nothing
    pass

def mock_api(func, **decorator_kwargs):
    @patch.dict(django.conf.settings.FICUSPUMILA, API_URL='/api/')
    @patch('requests.sessions.Session.request', mock_request)
    @patch('tastypie.cache.SimpleCache.set', mock_cache_set)
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


class TestCase(FastFixtureTestCase):
    """
    Don't be smart so much in test cases!
    """

    fixtures = INITIAL_DATA

    def setUp(self):
        invalidate()
        call_command('loaddata', *TEST_DATA)
        super(TestCase, self).setUp()


class Proxy(TestCase):
    """
    Don't be smart so much in test cases!
    """

    pass


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
        return self.create_basic(username=settings('SYSTEM_USERNAME'),
                                 password=settings('SYSTEM_PASSWORD'))

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
