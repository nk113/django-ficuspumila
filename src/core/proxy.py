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
from urlparse import urlparse

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
        return getattr(module, '%sProxy' % name)(auth=(settings.SYSTEM_USERNAME,
                                                       settings.SYSTEM_PASSWORD))
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
            #
            # CAVEAT: resource_url of referred resource has to have the same version
            base_client = self.model._base_client
            api_url = base_client._api_url
            version = base_client._version
            paths   = self._response[attr].replace(
                          base_client._api_path, '')[:-1].split('/')[:-2]
            if version in paths: paths.remove(version)
            namespace = '/'.join(paths)

            logger.debug(u'%s, need namespace schema (%s)' % (
                self._response[attr],
                ProxyClient.build_base_url(base_client._api_url, **{
                    'version': base_client._version,
                    'namespace': namespace
                })))

            client = ProxyClient.get(base_client._api_url,
                                     version=base_client._version,
                                     namespace=namespace,
                                     auth=base_client._auth)
            client.schema()

            clone_original = self.model.clone
            self.model.clone = lambda model_name: client._model_gen(model_name)

            model = super(Response, self).__getattr__(attr)

            self.model.clone = clone_original

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
            key = ProxyClient.build_base_url(args[0], **kwargs)

            if not key in cls._instances:
                cls._instances[key] = super(ProxyClient,
                                            cls).__new__(cls,
                                                         *args,
                                                         **kwargs)
            return cls._instances[key]
        return cls._instances[cls._instances.keys()[0]]

    def __init__(self, base_url, auth=None, strict_field=True, client=None, **kwargs):

        self._api_url   = '%s%s' % (base_url,
                                    '/' if not base_url.endswith('/') else '')

        parsed = urlparse(self._api_url)

        self._api_path  = parsed.path
        self._version   = kwargs.get('version', None)
        self._namespace = kwargs.get('namespace', None)
        self._auth      = kwargs.get('auth', auth)

        super(ProxyClient, self).__init__(ProxyClient.build_base_url(base_url,
                                                                     **kwargs),
                                          self._auth,
                                          strict_field,
                                          client)

    def _model_gen(self, model_name, strict_field=True, base_client=None):
        model = super(ProxyClient, self)._model_gen(model_name,
                                                    strict_field,
                                                    self)

        # overwrite manager
        model.objects = Manager(model)
        model.save_original = model.save
        model.delete_original = model.delete

        def break_cache(obj):
            url = '%s%s/' % (obj._base_client._api_path,
                             obj._client._store['base_url'].replace(
                                 obj._base_client._api_url,
                                 ''))

            if hasattr(obj, 'id'):
                url = '%s%s/' % (url, obj.id,)

            cache.delete(url)

        def save(obj): 
            break_cache(obj)
            model.save_original(obj)

        def delete(obj):
            break_cache(obj)
            model.delete_original(obj)

        model.save = save
        model.delete = delete

        return model

    @staticmethod
    def get(url, **kwargs):
        key = ProxyClient.build_base_url(url, **kwargs)
        return ProxyClient._instances.get(key,
                                          ProxyClient(url,
                                                      **kwargs))

    @staticmethod
    def get_by_schema(schema):
        for instance in ProxyClient._instances.values():
            if schema in instance._schema_store:
                return instance
        return None

    @staticmethod
    def build_base_url(url, **kwargs):
        return '%s%s%s' % (url,
                   '%s/' % kwargs.get('version') if kwargs.get('version') else '',
                   '%s/' % kwargs.get('namespace') if kwargs.get('namespace') else '')

    def schema(self, model_name=None, namespace=None):
        namespace = namespace or '.'.join(
                        self._base_url.replace(self._api_url,
                                               '').split('/')[:-1])

        if model_name is None:
            model_name = namespace
            url = self._base_url
        else:
            url = self._url_gen('%s/schema/' % model_name)

        # logger.debug(u'schema %s (%s)' % (model_name, url,))

        if not model_name in self._schema_store:
            self._schema_store[model_name] = self.request(url)

        return self._schema_store[model_name]

    @cache.cache(keyarg=1,
                 breakson=lambda *args, **kwargs: len(args) >= 3 and args[2] is not 'GET',
                 nocacheonbreak=True,
                 timeout=60*60)
    def request(self, url, method='GET'):
        return super(ProxyClient, self).request(url, method)


class Proxy(object):

    def __init__(self, **kwargs):

        api_url = kwargs.get('api_url', None) or getattr(settings, 'API_URL', None)

        if not api_url:
            raise ProxyException(_(u'"API_URL" not found in settings or ' +
                                   u'"api_url" not found in kwargs'))

        version   = kwargs.get('version', 'v1')
        namespace = kwargs.get('namespace',
                               '/'.join(self.__module__.split('.')[:-2]))
        auth      = kwargs.get('auth', None)

        resource_name = kwargs.get('resource_name',
                                   self.__class__.__name__[:-5].lower())


        self._client = ProxyClient.get(api_url,
                                       version=version,
                                       namespace=namespace,
                                       auth=auth)

        try:
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
