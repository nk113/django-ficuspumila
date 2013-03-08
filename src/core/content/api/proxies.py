# -*- coding: utf-8 -*-
import logging

from core.content.proxies import ContentProxy
from core.proxies import get
from . import models


COMMON_MODELS = 'core.content.common.models'

logger = logging.getLogger(__name__)


class GenreProxy(ContentProxy):

    pass


class GenreLocalizationProxy(ContentProxy):

    pass


class SourceProxy(ContentProxy):

    pass


class SourceAttributeProxy(ContentProxy):

    pass


class SourceEventProxy(ContentProxy):

    pass


class SourceNotificationProxy(ContentProxy):

    pass


class OwnerProxy(ContentProxy):

    pass


Genre              = get('Genre', COMMON_MODELS)
GenreLocaliazation = get('GenreLocalization', COMMON_MODELS)
Source             = get('Source', COMMON_MODELS)
SourceAttribute    = get('SourceAttribute', COMMON_MODELS)
SourceEvent        = get('SourceEvent', COMMON_MODELS)
SourceNotification = get('SourceNotification', COMMON_MODELS)
Owner              = get('Owner')
