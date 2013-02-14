# -*- coding: utf-8 -*-
import inspect
import logging

from django.conf import settings
from django.utils.importlib import import_module
from queryset_client import Client

from . import models
from .cache import cache

logger = logging.getLogger(__name__)


def get(name):
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    splitted = module.__name__.split('.')

    if splitted.pop() != 'proxies':
        splitted.append('models')
        module = import_module('.'.join(splited))

    if settings.API_PROXY:
        return getattr(module, '%sProxy' % name)()
    else:
        return getattr(module, name)


class ProxyClient(Client):

    @cache(keyarg=1)
    def schema(self, model_name=None):
        return super(ProxyClient, self).schema(model_name)


class Proxy(object):

    def __init__(self, auth=None, strict_field=True, client=None, **kwargs):
        self._client = ProxyClient('%s%s/' % (settings.API_URL,
                                         self.__module__.split('.')[-2]),
                              auth)
        self._resource = getattr(self._client,
                                 self.__class__.__name__[:-5].lower())
        for key, value in inspect.getmembers(self._resource):
            try:
                setattr(self, key, value)
            except:
                pass


class CountryProxy(Proxy):
    pass


Country = get('Country')
