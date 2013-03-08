# -*- coding: utf-8 -*-
import inspect
import logging

from dateutil import parser
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from queryset_client import Client
from queryset_client.client import FieldTypeError

from . import models
from .cache import cache
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


class ProxyClient(Client):

    @cache(keyarg=1)
    def schema(self, model_name=None):
        # overrides to support multiple api endpoints - app namespace
        api_name = self._base_url.replace(settings.API_URL,
                                          '').split('/')[0]

        if model_name is None:
            model_name = api_name
            url = self._base_url
        else:
            url = self._url_gen('%s/schema/' % model_name)

        if not model_name in self._schema_store:
            self._schema_store[model_name] = self.request(url)

        return self._schema_store[model_name]


class Proxy(object):

    def __init__(self, auth=None, strict_field=True, client=None, **kwargs):

        if not getattr(settings, 'API_URL', None):
            raise ProxyException(_(u'API_URL not found in settings.'))

        api_name = getattr(self, 'api_name', None)

        self._client = ProxyClient('%s%s/' % (settings.API_URL,
                           api_name if api_name else self.__module__.split('.')[1]),
                           (settings.SYSTEM_USERNAME,
                            settings.SYSTEM_PASSWORD))

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
            except FieldTypeError, e:
                error = '%s' % e
                if '\'datetime\'' in error:
                    self._fields[attr] = parser.parse(value)
                else:
                    raise e

        self._resource._setfield_original = self._resource._setfield
        self._resource._setfield = _setfield

        # proxy fields on resource
        for key, value in inspect.getmembers(self._resource):
            try:
                setattr(self, key, value)
            except:
                pass


class CoreProxy(Proxy):

    api_name = 'core'
