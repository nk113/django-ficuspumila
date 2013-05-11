# -*- coding: utf-8 -*-
import copy
import inspect
import json
import logging
import time

from dateutil import parser
from django.core.exceptions import ObjectDoesNotExist
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from queryset_client import client
from urllib import urlencode
from urlparse import urlparse

from ficuspumila.core.utils import get_default_language_code
from ficuspumila.settings import ficuspumila as settings
from . import cache
from .auth.sso import Authenticator as SsoAuthenticator
from .crypto import Transcoder
from .exceptions import ProxyException
from .models import Attribute, Choice, Model
from .tasks import notify_event
from .utils import (
    curtail, extend, from_python, mixin,
    refresh, to_python
)

PK_ID = ('pk', 'id',)

logger = logging.getLogger(__name__)


def invalidate():
    for name, proxy in ProxyClient._proxies.items():
        refresh(proxy.__module__)

    for name, model in ProxyClient._models.items():
        curtail(model, Proxy)
        if getattr(model, '__init__original'):
            model.__init__ = model.__init__original

    ProxyClient._instances = {}
    ProxyClient._proxies = {}
    ProxyClient._models = {}

def get(name, model_module=None, proxy_module=None):
    if isinstance(proxy_module, str):
        proxy_module = import_module(proxy_module)

    if proxy_module is None:
        frame = inspect.stack()[1]
        proxy_module = inspect.getmodule(frame[0])

    if model_module is None:
        try:
            splitted = proxy_module.__name__.split('.')
            splitted[-1] = 'models'
            model_module = '.'.join(splitted)
        except AttributeError, e:
            logger.exception(u'seems not to be imported in django application context')

    proxy = getattr(proxy_module, '%sProxy' % name)

    if settings('API_URL'):
        if name.lower() in ProxyClient._proxies:
            return ProxyClient._proxies[name.lower()]

        return proxy(auth=(settings('SYSTEM_USERNAME'),
                           settings('SYSTEM_PASSWORD')))
    else:
        if name not in ProxyClient._models.keys():
            model = getattr(import_module(model_module), name)

            # implement proxy mixin
            def __init__(obj, *args, **kwargs):
                obj.__init__original(*args, **kwargs)
                mixin(obj.__class__, proxy)
                obj.__module__ = proxy.__module__
                obj.__init_proxy__()

            model.__init__original = model.__init__
            model.__init__ = __init__

            ProxyClient._models[name] = model

        return ProxyClient._models[name]

def get_pk(obj):
    """
    For resources that do not have default ``id`` primary key

    TODO: think better way
    """
    for key in ('user',):
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

    def _filter(self, *args, **kwargs):
        for key, value in kwargs.items():
            try:
                # convert resource_uri to numeric id
                id = client.parse_id('%s' % value)
                kwargs[key] = id
            except Exception, e:
                pass
        return super(QuerySet, self)._filter(*args, **kwargs)

    def _wrap_response(self, dictionary):
        return self._response_class(self.model,
                                    dictionary,
                                    _to_many_class=ManyToManyManager)

    def create(self, **kwargs):
        # FIXME: think better way
        obj = super(QuerySet, self).create(**kwargs)
        return self.get(id=obj.id)

    def get_or_create(self, **kwargs):
        # FIXME: think better way
        obj, created = super(QuerySet, self).get_or_create(**kwargs)
        if not created:
            return obj, created
        return self.get(id=obj.id), created


class Response(client.Response):

    def __init__(self, model, response=None, url=None, **kwargs):

        # implement proxy mixin
        if model._model_name in ProxyClient._proxies:
            proxy = ProxyClient._proxies[model._model_name].__class__
            extend(self, proxy, replace_module=True)
            self.__init_proxy__()

        super(Response, self).__init__(model, response, url, **kwargs)

    def __repr__(self):
        if hasattr(self, 'resource_uri'):
            return self.resource_uri
        return super(Response, self).__repr__()

    def __getattr__(self, name):
        """
        Overrides to support api namespace and to_one class diversity
        """
        try:
            if not name in self._response:
                raise AttributeError(name)

            elif not 'related_type' in self._schema['fields'][name]:
                return self.__getitem__(name)

        except AttributeError, e:
            if name in PK_ID:
                return get_pk(self)
            return getattr(self.model, name)

        # resolves foreign key references in another api namespace
        # expects to be called with detail url like /api/v1/<resource>/<id>|schema/
        #
        # CAVEAT: resource_uri of referred resource has to have the same version 
        base_client = self.model._base_client

        if name in self._schema['fields']:
            schema = self._schema['fields'][name]

            if ('related_type' in schema and
                schema['related_type'] in ('to_one', 'to_many',)):
                if schema.get('schema'):
                    schema_uri = schema.get('schema')
                else:
                    try:
                        schema_uri = self._response[name]
                        schema_uri = schema_uri[0] if (
                            isinstance(schema_uri, list)) else schema_uri

                        logger.debug(u'trying to identify schema info from ' +
                                     u'schema_uri (%s).' % schema_uri)
                    except Exception, e:
                        raise ProxyException(u'Couldn\'t identify related ' +
                                             u'field schema (%s).' % name)
        else:
            raise ProxyException(u'The field "%s" seems not to be defined ' +
                                 u'in the schema.')

        api_url = base_client._api_url
        version = base_client._version
        paths   = schema_uri.replace(
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

        proxy_client = ProxyClient.get(base_client._api_url,
                                       version=base_client._version,
                                       namespace=namespace,
                                       auth=base_client._auth)
        proxy_client.schema()

        model = proxy_client._model_gen(resource_name)

        # set manager alias
        if name is not resource_name:
            setattr(self.model, resource_name, getattr(self.model, name))

        if schema['related_type'] == 'to_many':
            return ManyToManyManager(
                       model=model,
                       query={'id__in': [client.parse_id(resource_uri) for resource_uri in self._response[name]]},
                       instance=self.model)

        elif schema['related_type'] == 'to_one':
            return Response(model=model, url=self._response[name])

    @property
    def _response(self):
        if self.__response:
            return self.__response

        if self._url is not None:
            cached = cache.get(self._url)
            if cached:
                self.refresh(json.loads(cached))
                return self.__response

        response = super(Response, self)._response

        if self._url is not None:
            if 'model' in response:
                del(response['model'])
            cache.set(self._url, json.dumps(response))

        return response

    def refresh(self, data):
        self.__response = data
        try:
            self.model = self.model(**self.__response)
        except:
            self.model = self.model.__class__(**self.__response)

    def invalidate(self):
        resource = getattr(self.model._main_client, self.model._model_name)
        self.refresh(resource(client.parse_id(self.resource_uri)).get())


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
    _models = {}

    def __new__(*args, **kwargs):
        if len(args): 
            key = ProxyClient.build_base_url(args[1], **kwargs)

            if not key in ProxyClient._instances:
                ProxyClient._instances[key] = super(ProxyClient,
                                                    ProxyClient).__new__(*args, **kwargs)

            proxy = kwargs.get('proxy')
            if proxy:
                ProxyClient._proxies[proxy.__class__.__name__.lower().replace('proxy', '')] = proxy

            return ProxyClient._instances[key]
        return ProxyClient._instances[ProxyClient._instances.keys()[0]]

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
 
        # overwrite manager and model members
        model.objects = Manager(model)

        model._setfield_original = model._setfield
        model.save_original = model.save
        model.delete_original = model.delete

        def _setfield(obj, name, value):
            try:
                obj._setfield_original(name, value)
            except client.FieldTypeError, e:
                error = '%s' % e
                if '\'datetime\'' in error:
                    obj._fields[name] = parser.parse(value)
                elif '\'list\'' in error:
                    obj._fields[name] = value 
                elif '\'json\'' in error:
                    obj._fields[name] = value
                else:
                    raise e
            super(obj.__class__, obj).__setattr__(name, value)

        def break_cache(obj):
            cache.delete(getattr(obj,
                                 'resource_uri',
                                 '%s%s/' % (obj._base_client._api_path,
                                            obj._client._store['base_url'].replace(
                                                obj._base_client._api_url,
                                                ''))))

        def save(obj):
            break_cache(obj) 
            model.save_original(obj)                

        def delete(obj):
            break_cache(obj)
            model.delete_original(obj)

        model._setfield = _setfield
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

    def schema(self, model_name=None):
        path = '.'.join(self._base_url.replace(self._api_url,
                                               '').split('/')[:-1])

        if model_name is None:
            model_name = path
            url = self._base_url
        else:
            url = self._url_gen('%s/schema/' % model_name)

        if not model_name in self._schema_store:
            self._schema_store[model_name] = self.request(url)

        # try to import proxies
        try:
            module = '%s.%s.proxies' % (self.__module__.split('.')[0],
                                        self._namespace.replace('/', '.'))
            import_module(module)
        except Exception, e:
            logger.debug(u'failed to import proxies module (%s)' % module)

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

        api_url = kwargs.get('api_url', None) or settings('API_URL') if settings('API_URL') else None

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

    def __init_proxy__(self):
        pass

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


class AttributableProxy(Proxy):

    _attribute_names = ('attribute',)

    def __init_proxy__(self):
        super(AttributableProxy, self).__init_proxy__()

        class_name = self.__class__.__name__
        if isinstance(self, Proxy):
            class_name = class_name.replace('Proxy', '')
 
        for name in self._attribute_names:
            attribute_class_name = '%s%s' % (class_name, name.title(),)
            setattr(self, '%s' % name, get(attribute_class_name,
                                           proxy_module=self.__module__))
            # set the name proxy if the attribute has its name field as foreign key
            try:
                setattr(self, '%s_name' % name, get('%sName' % attribute_class_name,
                                                    proxy_module=self.__module__))
            except AttributeError, e:
                # could occur
                pass

    def get_attribute(self, name):
        kwargs = {
            self.model_name: self.id,
            'name__name': name,
        }
        return self.attributes.get(**kwargs)

    def getattr(self, name, default=None):
        try:
            return to_python(self.get_attribute(name).value)
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
                'value': from_python(value),
            }
            attribute = self.attribute.objects.create(**kwargs)
            self.invalidate()
        else:
            attribute.value = from_python(value)
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

    @property
    def attribute(self):
        return self.name.name


class LoggerProxy(AttributableProxy):

    _attribute_names = ('event',)

    @property
    def latest(self):
        try:
            return self.events.latest('id')
        except:
            return None

    def fire(self, name, message=''):
        try:
            event_name = self.event_name.objects.get(name=name)
        except (client.ObjectDoesNotExist,
                ObjectDoesNotExist) as e:
            raise e
        kwargs = {
            self.model_name: self,
            'name': event_name,
        }
        if message:
            kwargs['message'] = message
        event = self.event.objects.create(**kwargs)
        self.invalidate()
        return event


class EventProxy(Proxy):

    @property
    def event(self):
        return self.name.name


class StatefulProxy(LoggerProxy):

    @property
    def state(self):

        return self.latest


class NotifierProxy(LoggerProxy):

    _attribute_names = ('event', 'notification',)


class LocalizableProxy(AttributableProxy):

    _attribute_names = ('localization',)

    def localize(self, language_code=None):
        self.__init_proxy__()

        localizations = []
        if language_code:
            localizations = self.localization.objects.filter(language_code=language_code.lower())
        if len(localizations) < 1:
            localizations = self.localization.objects.filter(
                language_code=get_default_language_code())
        if len(localizations) < 1:
            return self.localization()
        return localizations[0]


class ServiceProxy(NotifierProxy):

    _attribute_names = ('attribute', 'event', 'notification',)

    def generate_token(self, data={}, format='json'):
        try:
            if format == 'json':
                data = json.dumps((
                           time.time() + settings('TOKEN_TIMEOUT'),
                           data,))
            else:
                raise ProxyException(_(u'Format not supported: %s') % format)

            return Transcoder(
                       key=self.token_key,
                       iv=self.token_iv).algorithm.encrypt(data)

        except Exception, e:
            logger.exception(u'an error has occurred during generating token: %s' % e)
            raise e

    def decrypt_token(self, token, format='json', expiration=False):
        try:
            token = Transcoder(
                        key=self.token_key,
                        iv=self.token_iv).algorithm.decrypt(token)

            if format == 'json':
                token = json.loads(token)
            else:
                raise ProxyException(_(u'Format not supported: %s') % format)

            if expiration:
                return token

            return token[1]

        except Exception, e:
            logger.exception(u'an error has occurred during decrypting token: %s' % e)
            raise e

    def update_token(self, token, format='json'):
        try:
            return self.generate_token(self.decrypt_token(token, format), format)
        except Exception, e:
            logger.exception(u'an error has occurred during updating token: %s' % e)
            raise e

    def generate_sso_params(self, data={}, format='json'):
        try:
            return urlencode({self.model_name: self.user.id,
                              SsoAuthenticator.TOKEN_PARAM: self.generate_token(data, format),})
        except Exception, e:
            logger.exception(u'an error has occurred during generating sso params: %s' % e)
            raise e
