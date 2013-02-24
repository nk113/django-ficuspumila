# -*- coding: utf-8 -*-
import logging

from core.proxies import get, Proxy
from . import models


logger = logging.getLogger(__name__)


class GenreProxy(Proxy):
    pass


class GenreLocalizationProxy(Proxy):
    pass


class SourceProxy(Proxy):
    pass


class SourceAttributeProxy(Proxy):
    pass


class SourceEventProxy(Proxy):
    pass


class SourceNotificationProxy(Proxy):
    pass


class OwnerProxy(Proxy):
    pass


Genre              = get('Genre')
GenreLocaliazation = get('GenreLocalization')
Source             = get('Source')
SourceAttribute    = get('SourceAttribute')
SourceEvent        = get('SourceEvent')
SourceNotification = get('SourceNotification')
Owner              = get('Owner')
