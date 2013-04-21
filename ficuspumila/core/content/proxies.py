# -*- coding: utf-8 -*-
import logging

from ficuspumila.core.proxies import (
    AttributeProxy,
    get, Proxy,
    SubjectProxy,
)


logger = logging.getLogger(__name__)


class GenreProxy(Proxy):

    pass


class GenreLocalizationProxy(Proxy):

    pass


class SourceProxy(SubjectProxy):

    pass


class SourceAttributeNameProxy(Proxy):

    pass


class SourceAttributeProxy(AttributeProxy):

    pass


class SourceEventNameProxy(Proxy):

    pass


class SourceEventProxy(Proxy):

    pass


class SourceNotificationProxy(Proxy):

    pass


class OwnerProxy(Proxy):

    pass


class FileTypeProxy(Proxy):

    pass


class FileSpecificationProxy(Proxy):

    pass


class FileSpecificationAttributeNameProxy(Proxy):

    pass


class FileSpecificationAttributeProxy(Proxy):

    pass


class ResourceTypeProxy(Proxy):

    pass


# FIXME: uncomment the line below causes maximum recursion error...
# Genre               = get('Genre')
GenreLocaliazation  = get('GenreLocalization')
Source              = get('Source')
SourceAttributeName = get('SourceAttributeName')
SourceAttribute     = get('SourceAttribute')
SourceEventName     = get('SourceEventName')
SourceEvent         = get('SourceEvent')
SourceNotification  = get('SourceNotification')
Owner               = get('Owner')
FileType            = get('FileType')
FileSpecification   = get('FileSpecification')
FileSpecificationAttributeName = get('FileSpecificationAttributeName')
FileSpecificationAttribute = get('FileSpecificationAttribute')
ResourceType        = get('ResourceType')
