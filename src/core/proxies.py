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


def get(name):

    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    splitted = module.__name__.split('.')

    if splitted.pop() != 'proxies':
        splitted.append('models')
        module = import_module('.'.join(splited))

    if getattr(settings, 'API_URL', None):
        return getattr(module, '%sProxy' % name)()
    else:
        return getattr(module, name)


class ProxyClient(Client):

    @cache(keyarg=1)
    def schema(self, model_name=None):
        # overrides to support multiple api endpoints - app namespace
        app_name = self._base_url.replace(settings.API_URL,
                                          '').split('/')[0]
        if not app_name in self._schema_store:
            schema = super(ProxyClient, self).schema(model_name)
            del(self._schema_store[None])
            self._schema_store[app_name] = schema

        logger.debug(self._schema_store)
        return self._schema_store[app_name]


class Proxy(object):

    def __init__(self, auth=None, strict_field=True, client=None, **kwargs):

        if not getattr(settings, 'API_URL', None):
            raise ProxyException(_(u'API_URL not found in settings.'))

        self._client = ProxyClient('%s%s/' % (settings.API_URL,
                                       self.__module__.split('.')[1]),
                                   (settings.SYSTEM_USERNAME,
                                    settings.SYSTEM_PASSWORD))
        self._resource = getattr(self._client,
                                 self.__class__.__name__[:-5].lower())

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
