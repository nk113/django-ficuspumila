# -*- coding: utf-8 -*-
import copy
import inspect
import json
import logging

from dateutil import parser
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from queryset_client import client
from urlparse import urlparse

from . import cache
from .exceptions import ProxyException
from .models import Attribute, Choice, Model
from .utils import extend


PK_ID = ('pk', 'id',)

logger = logging.getLogger(__name__)


def get(name, model_module=None, proxy_module=None):
    if isinstance(proxy_module, str):
        proxy_module = import_module(proxy_module)

    if proxy_module is None:
        frame = inspect.stack()[1]
        proxy_module = inspect.getmodule(frame[0])

    if model_module is None:
        splitted = proxy_module.__name__.split('.')
        splitted[-1] = 'models'
        model_module = '.'.join(splitted)

    proxy = getattr(proxy_module, '%sProxy' % name)

    if 'API_URL' in settings.FICUSPUMILA:
        return proxy(auth=(settings.FICUSPUMILA['SYSTEM_USERNAME'],
                           settings.FICUSPUMILA['SYSTEM_PASSWORD']))
    else:
        model = getattr(import_module(model_module), name)

        # implement proxy mixin
        def __init__(obj, *args, **kwargs):
            super(obj.__class__, obj).__init__(*args, **kwargs)
            extend(obj, proxy, None, True)

        model.__init__ = __init__

        return model

def get_pk(obj):
    """
    For resources that do not have default ``id`` primary key

    TODO: think better way
    """
    foreign_keys = ('user',)
    for key in foreign_keys:
        if hasattr(obj, key):
            try:
                return getattr(obj, key).id
            except AttributeError, e:
                pass
    raise AttributeError()
            

class QuerySet(client.QuerySet):

    def __init__(self, model, responses=None, query=None, **kwargs):
        super(QuerySet, self).__init__(model, responses, query, **kwargs)
        self._response_class = Response

    def _wrap_response(self, dictionary):
        return self._response_class(self.model,
                                    dictionary,
                                    _to_many_class=ManyToManyManager)


class Response(client.Response):

    def __init__(self, model, response=None, url=None, **kwargs):

        # implement proxy mixin
        if model._model_name in model._base_client._proxies:
            extend(self, model._base_client._proxies[model._model_name].__class__)

        super(Response, self).__init__(model, response, url, **kwargs)

    def __repr__(self):
        if hasattr(self, 'resource_uri'):
            return self.resource_uri
        return super(Response, self).__repr__()

    def __getattr__(self, name):
        base_client = self.model._base_client

        try:
            return super(Response, self).__getattr__(name)
        except AttributeError, e:
            if name in PK_ID:
                return get_pk(self)
            return getattr(self.model, name)
        except KeyError, e:
            # resolves foreign key references in another api namespace
            # expects to be called with detail url like /api/v1/<resource>/<id>|schema/
            #
            # CAVEAT: resource_uri of referred resource has to have the same version
            schema = self._schema['fields'][name]
            if schema['related_type'] in ('to_one', 'to_many',):
                if schema.get('schema'):
                    resource_uri = schema.get('schema')
                else:
                    try:
                        resource_uri = self._response[name]
                        resource_uri = resource_uri[0] if (
                            isinstance(resource_uri, list)) else resource_uri

                        logger.debug(u'trying to identify schema info from ' +
                                     u'resource_uri (%s).' % resource_uri)
                    except Exception, e:
                        raise ProxyException(u'Couldn\'t identify related ' +
                                             u'field schema (%s).' % name)
            else:
                raise ProxyException(u'The field "%s" seems not to be defined ' +
                                     u'in the schema.')

            api_url = base_client._api_url
            version = base_client._version
            paths   = resource_uri.replace(
                          base_client._api_path, '')[:-1].split('/')

            # strip <id> or ``schema`` part and extract resource_name
            paths.pop()
            resource_name = paths.pop()

            if version in paths: paths.remove(version)
            namespace = '/'.join(paths)

            logger.debug(u'%s, need namespace schema (%s)' % (
                self._response[name],
                ProxyClient.build_base_url(base_client._api_url, **{
                    'version': base_client._version,
                    'namespace': namespace
                })))

            client = ProxyClient.get(base_client._api_url,
                                     version=base_client._version,
                                     namespace=namespace,
                                     auth=base_client._auth)
            client.schema()

            # set manager alias
            if name is not resource_name:
                setattr(self.model, resource_name, getattr(self.model, name))

            clone_original = self.model.clone
            self.model.clone = lambda model_name: client._model_gen(resource_name)

            model = super(Response, self).__getattr__(name)

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

    def invalidate(self):
        resource = getattr(self.model._main_client, self.model._model_name)
        self.__response = resource(client.parse_id(self.resource_uri)).get()


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
    _proxies = {}

    def __new__(cls, *args, **kwargs):
        if len(args): 
            key = ProxyClient.build_base_url(args[0], **kwargs)

            if not key in cls._instances:
                cls._instances[key] = super(ProxyClient,
                                            cls).__new__(cls,
                                                         *args,
                                                         **kwargs)

            proxy = kwargs.get('proxy')
            if proxy:
                cls._proxies[proxy.__class__.__name__.lower().replace('proxy', '')] = proxy

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

    def __init__(self, *args, **kwargs):

        if isinstance(self, Model):
            super(Proxy, self).__init__(*args, **kwargs)
            return

        api_url = kwargs.get('api_url', None) or settings.FICUSPUMILA['API_URL'] if (
                      'API_URL' in settings.FICUSPUMILA) else None

        if not api_url:
            raise ProxyException(_(u'"API_URL" not found in settings or ' +
                                   u'"api_url" not found in kwargs.'))

        version   = kwargs.get('version', 'v1')
        namespace = kwargs.get('namespace',
                               '/'.join(self.__module__.split('.')[1:-1]))
        auth      = kwargs.get('auth', None)

        resource_name = kwargs.get('resource_name',
                                   self.__class__.__name__[:-5].lower())


        self._client = ProxyClient.get(api_url,
                                       version=version,
                                       namespace=namespace,
                                       auth=auth,
                                       proxy=self)

        try:
            self._resource = getattr(self._client,
                                     resource_name)
        except AttributeError, e:
            raise ProxyException(_(u'API seems not to have endpoint ' +
                                   u'for the resource (%s).' % resource_name))

        # support special fields
        def _setfield(obj, name, value):
            try:
                obj._setfield_original(name, value)
            except client.FieldTypeError, e:
                error = '%s' % e
                if '\'datetime\'' in error:
                    obj._fields[name] = parser.parse(value)
                elif '\'list\'' in error:
                    obj._fields[name] = value
                else:
                    raise e
            super(obj.__class__, obj).__setattr__(name, value)

        self._resource._setfield_original = self._resource._setfield
        self._resource._setfield = _setfield

    def __getattr__(self, name):
        if name in PK_ID:
            return get_pk(self)

        if not isinstance(self, Model):
            if name is not '_resource':
                return getattr(self._resource, name)
        raise AttributeError()

    def invalidate(self):
        if isinstance(self, Model):
            pass
        else:
            super(Proxy, self).invalidate()

    @property
    def model_name(self):
        if isinstance(self, Model):
            return self.__class__.__name__.lower()
        else:
            return self.model._model_name


class SubjectProxy(Proxy):

    class Attributes(Choice):

        NAME = 0
        DEFAULT = NAME

    _attribute = None
    _attribute_name = None

    def _seek_related_fields(self):
        class_name = self.__class__.__name__
        if isinstance(self, Proxy):
            class_name = class_name.replace('Response_extended_with_',
                                            '').replace('Proxy', '')
        self._attribute = get('%sAttribute' % class_name, proxy_module=self.__module__)
        self._attribute_name = get('%sAttributeName' % class_name, proxy_module=self.__module__)

    @property
    def attribute(self):
        if self._attribute is None:
            self._seek_related_fields()
        return self._attribute

    @property
    def attribute_name(self):
        if self._attribute_name is None:
            self._seek_related_fields()
        return self._attribute_name

    def get_attribute(self, name):
        kwargs = {
            self.model_name: self.id,
            'name__name': name,
        }
        return self.attributes.get(**kwargs)

    def getattr(self, name, default=None):
        try:
            return self.get_attribute(name).value
        except (client.ObjectDoesNotExist,
                ObjectDoesNotExist) as e:
            return default

    def setattr(self, name, value):
        try:
            attribute = self.get_attribute(name)
        except (client.ObjectDoesNotExist,
                ObjectDoesNotExist) as e:
            try:
                attribute_name = self.attribute_name.objects.get(name=name)
            except (client.ObjectDoesNotExist,
                    ObjectDoesNotExist) as e:
                raise e
            kwargs = {
                self.model_name: self,
                'name': attribute_name,
                'value': value,
            }
            attribute = self.attribute.objects.create(**kwargs)
            self.invalidate()
        else:
            attribute.value = value
            attribute.save()

    def delattr(self, name):
        try:
            attribute = self.get_attribute(name=name)
        except (client.ObjectDoesNotExist,
                ObjectDoesNotExist) as e:
            raise KeyError(name)
        else:
            attribute.delete()
            self.invalidate()


class AttributeProxy(Proxy):

    _logger = None

    def _seek_related_fields(self):
        class_name = self.__class__.__name__
        if isinstance(self, Model):
            self._logger = get(self.__class__.__name__.replace('Attribute', ''),
                               proxy_module=self.__module__)
        else:
            self._logger = get(self.__class__.__name__.replace(
                                   'Response_extended_with_',
                                   '').replace('AttributeProxy', ''),
                               proxy_module=self.__module__)

    @property
    def logger(self):
        if self._logger is None:
            self._seek_related_fields()
        return self._logger
