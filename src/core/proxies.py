# -*- coding: utf-8 -*-
import copy
import inspect
import json
import logging

from dateutil import parser
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from queryset_client import client

from . import cache
from .exceptions import ProxyException


logger = logging.getLogger(__name__)


def get(name, model_module=None):

    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])

    splitted = module.__name__.split('.')

    if splitted.pop() != 'proxies':
        if model_module is None:
            splitted.append('models')
            module = import_module('.'.join(splited))
        else:
            module = import_module(model_module)

    if getattr(settings, 'API_URL', None):
        return getattr(module, '%sProxy' % name)()
    else:
        return getattr(module, name)


class QuerySet(client.QuerySet):

    def _wrap_response(self, dictionary):
        return self._response_class(self.model,
                                    dictionary,
                                    _to_many_class=ManyToManyManager)


class Response(client.Response):

    def __getattr__(self, attr):
        try:
            return super(Response, self).__getattr__(attr)
        except KeyError, e:
            # handles foreign key references in another api namespace
            # expects to be called with detail url like /api/v1/<resource>/<id>/
            url = '%s%s/' % (settings.API_URL,
                      '/'.join(
                          self._response[attr][1:-1].replace(settings.API_PATH,
                                                             '').split('/')[:-2]))

            logger.debug('need namespace schema (%s)' % url)

            client = ProxyClient.get(url)
            client.schema()

            old_clone = self.model.clone
            self.model.clone = lambda model_name: client._model_gen(model_name)

            model = super(Response, self).__getattr__(attr)

            self.model.clone = old_clone

            return model


    @property
    def _response(self):
        if self.__response:
            return self.__response

        if self._url is not None:
            cached = cache.get(self._url)
            if cached:
                self.__response = json.loads(cached)
                self.model = self.model(**self.__response)
                return self.__response

        response = super(Response, self)._response

        if self._url is not None:
            if 'model' in response:
                del(response['model'])
            cache.set(self._url, json.dumps(response))

        return response


class Manager(client.Manager):

    def get_query_set(self):
        return QuerySet(self.model,
                        response_class=Response)


class ManyToManyManager(client.ManyToManyManager):

    def get_query_set(self):
        return QuerySet(self.model,
                        query=self._query,
                        response_class=Response).filter()

    def filter(self, *args, **kwargs):
        if 'id__in' in kwargs:
            raise ProxyException(_(u'"id__in" is not supported ' +
                                   u'in ManyToManyManager.'))
        return QuerySet(self.model,
                        query=self._query,
                        response_class=Response).filter(*args, **kwargs)


class ProxyClient(client.Client):

    _instances = {}

    def __new__(cls, *args, **kwargs):
        if len(args):
            if not args[0] in cls._instances:
                cls._instances[args[0]] = super(ProxyClient,
                                                cls).__new__(cls,
                                                             *args,
                                                             **kwargs)
            return cls._instances[args[0]]
        return cls._instances[cls._instances.keys()[0]]

    def __init__(self, base_url, auth=None, strict_field=True, client=None):
        super(ProxyClient, self).__init__(base_url,
                                          auth,
                                          strict_field,
                                          client)

    def _namespace_gen(self, path):
        return '.'.join(path.split('/')[:-1])

    def _model_gen(self, model_name, strict_field=True, base_client=None):
        model = super(ProxyClient, self)._model_gen(model_name,
                                                    strict_field,
                                                    self)

        # overwrite manager
        model.objects = Manager(model)
        model.old_save = model.save
        model.old_delete = model.delete

        def break_cache(obj):
            url = '/%s%s/' % (settings.API_PATH,
                              obj._client._store['base_url'].replace(
                                  settings.API_URL,
                                  ''))

            if hasattr(obj, 'id'):
                url = '%s%s/' % (url, obj.id,)

            cache.delete(url)

        def save(obj): 
            break_cache(obj)
            model.old_save(obj)

        def delete(obj):
            break_cache(obj)
            model.old_delete(obj)

        model.save = save
        model.delete = delete

        return model

    @staticmethod
    def get(url):
        return ProxyClient._instances.get(url,
                                          ProxyClient(url,
                                                      (settings.SYSTEM_USERNAME,
                                                       settings.SYSTEM_PASSWORD)))

    @staticmethod
    def get_by_schema(schema):
        for instance in ProxyClient._instances.values():
            if schema in instance._schema_store:
                return instance
        return None

    def schema(self, model_name=None, namespace=None):
        namespace = namespace or self._namespace_gen(
                        self._base_url.replace(settings.API_URL, ''))

        if model_name is None:
            model_name = namespace
            url = self._base_url
        else:
            url = self._url_gen('%s/schema/' % model_name)

        if not model_name in self._schema_store:
            self._schema_store[model_name] = self.request(url)

        return self._schema_store[model_name]

    @cache.cache(keyarg=1,
                 breakson=lambda *args, **kwargs: len(args) >= 3 and args[2] is not 'GET',
                 nocacheonbreak=True)
    def request(self, url, method='GET'):
        return super(ProxyClient, self).request(url, method)


class Proxy(object):

    def __init__(self):

        if not getattr(settings, 'API_URL', None):
            raise ProxyException(_(u'API_URL not found in settings.'))

        self._client = ProxyClient.get('%s%s/' % (settings.API_URL,
                           '/'.join(self.__module__.split('.')[:-2])))

        try:
            resource_name = self.__class__.__name__[:-5].lower()
            self._resource = getattr(self._client,
                                     resource_name)
        except AttributeError, e:
            raise ProxyException(_(u'API seems not to have endpoint ' +
                                   u'for the resource: %s' % resource_name))

        # support timezone
        def _setfield(self, attr, value):
            try:
                self._setfield_original(attr, value)
            except client.FieldTypeError, e:
                error = '%s' % e
                if '\'datetime\'' in error:
                    self._fields[attr] = parser.parse(value)
                else:
                    raise e

        self._resource._setfield_original = self._resource._setfield
        self._resource._setfield = _setfield

        # proxy fields on resource
        for field, value in inspect.getmembers(self._resource):
            try:
                setattr(self, field, value)
            except:
                pass
