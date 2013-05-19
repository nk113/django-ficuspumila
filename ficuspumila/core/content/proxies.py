# -*- coding: utf-8 -*-
import logging

from ficuspumila.core import proxies


logger = logging.getLogger(__name__)


class Genre(proxies.Localizable):

    pass


class GenreLocalization(proxies.Proxy):

    pass


class Source(proxies.Service):

    pass


class SourceAttributeName(proxies.Proxy):

    pass


class SourceAttribute(proxies.Attribute):

    pass


class SourceEventName(proxies.Proxy):

    pass


class SourceEvent(proxies.Event):

    pass


class SourceNotification(proxies.Proxy):

    pass


class Owner(proxies.Proxy):

    pass


class FileType(proxies.Proxy):

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


class FileSpecification(proxies.Attributable):

    pass


class FileSpecificationAttributeName(proxies.Proxy):

    pass


class FileSpecificationAttribute(proxies.Proxy):

    pass


class ResourceType(proxies.Proxy):

    pass
