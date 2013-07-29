# -*- coding: utf-8 -*-
import logging

from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from rpc_proxy.proxies import Proxy

from ficuspumila.core import proxies
from ficuspumila.core import exceptions
from ficuspumila.settings import ficuspumila as settings


logger = logging.getLogger(__name__)


class ContentMeta:

    namespace = 'core/content'


class Genre(proxies.Localizable):

    class Meta(ContentMeta):

        pass


class GenreLocalization(proxies.Localization):

    class Meta(ContentMeta):

        pass


class Source(proxies.Service):

    class Meta(ContentMeta):

        pass


class SourceAttributeName(Proxy):

    class Meta(ContentMeta):

        pass


class SourceAttribute(proxies.Attribute):

    class Meta(ContentMeta):

        pass


class SourceEventName(Proxy):

    class Meta(ContentMeta):

        pass


class SourceEvent(proxies.Event):

    class Meta(ContentMeta):

        pass


class SourceNotification(Proxy):

    class Meta(ContentMeta):

        pass


class Owner(Proxy):

    class Meta(ContentMeta):

        pass


class FileType(Proxy):

    class Meta(ContentMeta):

        pass

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

    class Meta(ContentMeta):

        pass


class FileSpecificationAttributeName(Proxy):

    class Meta(ContentMeta):

        pass


class FileSpecificationAttribute(Proxy):

    class Meta(ContentMeta):

        pass


class Item(Proxy):

    class Meta(ContentMeta):

        pass

    @property
    def item_type_display(self):
        if 'get_item_type_display' in dir(self):
            return self.get_item_type_display()

        from ficuspumila.core.content.models import ItemTypes
        return ItemTypes.get_value(self.item_type)

    @property
    def meta_type_display(self):
        if 'get_meta_type_display' in dir(self):
            return self.get_meta_type_display()

        meta_types = settings('META_TYPES')

        if not meta_types:
            return None

        try:
            return meta_types[self.meta_type][1]
        except IndexError, e:
            raise exceptions.ProxyException(_('Unexpected meta type detected '
                                              '(%s, %s).') % (self.meta_type,
                                                               meta_types,))

    @property
    def metadata(self):
        try:
            meta = getattr(import_module(settings('META_PROXIES_MODULE')),
                           self.meta_type_display)
        except Exception, e:
            logger.exception(e)
            raise exceptions.ProxyException(_('No metadata model found, check '
                                              'if META_TYPES and '
                                              'META_PROXIES_MODULE settings are '
                                              'correct.'))

        return meta.objects.get(item=self)


class ResourceType(Proxy):

    class Meta(ContentMeta):

        pass
