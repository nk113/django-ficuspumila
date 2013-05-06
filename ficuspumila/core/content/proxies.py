# -*- coding: utf-8 -*-
import logging

from ficuspumila.core.proxies import (
    AttributableProxy, AttributeProxy, EventProxy,
    get, LocalizableProxy, Proxy,
    ServiceProxy,
)


logger = logging.getLogger(__name__)


class GenreProxy(LocalizableProxy):

    pass


class GenreLocalizationProxy(Proxy):

    pass


class SourceProxy(ServiceProxy):

    pass


class SourceAttributeNameProxy(Proxy):

    pass


class SourceAttributeProxy(AttributeProxy):

    pass


class SourceEventNameProxy(Proxy):

    pass


class SourceEventProxy(EventProxy):

    pass


class SourceNotificationProxy(Proxy):

    pass


class OwnerProxy(Proxy):

    pass


class FileTypeProxy(Proxy):

    @property
    def mime_type(self):
        try:
            return self.mime_types[0]
        except IndexError, e:
            return None

    @property
    def extension(self):
        try:
            return self.extensions[0]
        except IndexError, e:
            return None


class FileSpecificationProxy(AttributableProxy):

    pass


class FileSpecificationAttributeNameProxy(Proxy):

    pass


class FileSpecificationAttributeProxy(Proxy):

    pass


class ResourceTypeProxy(Proxy):

    pass


Genre               = get('Genre')
GenreLocalization   = get('GenreLocalization')
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
