# -*- coding: utf-8 -*-
import logging

from ficuspumila.core import proxies


logger = logging.getLogger(__name__)


class ExampleMeta:

    namespace = 'apps/example'


class Track(proxies.Localizable):

    class Meta(ExampleMeta):

        pass


class TrackLocalization(proxies.Localization):

    class Meta(ExampleMeta):

        pass


class Album(proxies.Localizable):

    class Meta(ExampleMeta):

        pass


class AlbumLocalization(proxies.Localization):

    class Meta(ExampleMeta):

        pass


class Video(proxies.Localizable):

    class Meta(ExampleMeta):

        pass


class VideoLocalization(proxies.Localization):

    class Meta(ExampleMeta):

        pass
