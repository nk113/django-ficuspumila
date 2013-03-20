# -*- coding: utf-8 -*-
import logging

from ficuspumila.core.proxy import get, Proxy
from . import models


COMMON_MODELS = 'ficuspumila.core.content.common.models'

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


class FileTypeProxy(Proxy):

    pass


class ResourceTypeProxy(Proxy):

    pass


class FileSpecificationProxy(Proxy):

    pass


class FileSpecificationAttributeProxy(Proxy):

    pass


class OwnerProxy(Proxy):

    pass


Genre              = get('Genre', COMMON_MODELS)
GenreLocaliazation = get('GenreLocalization', COMMON_MODELS)
Source             = get('Source', COMMON_MODELS)
SourceAttribute    = get('SourceAttribute', COMMON_MODELS)
SourceEvent        = get('SourceEvent',)
SourceNotification = get('SourceNotification',)
FileType           = get('FileType', COMMON_MODELS)
ResourceType       = get('ResourceType', COMMON_MODELS)
FileSpecification  = get('FileSpecification')
FileSpecificationAttribute = get('FileSpecificationAttribute')
Owner              = get('Owner')
