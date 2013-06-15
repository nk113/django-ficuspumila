# -*- coding: utf-8 -*-
import logging

from ficuspumila.core import proxies


logger = logging.getLogger(__name__)


class Track(proxies.Localizable):

    pass


class TrackLocalization(proxies.Localization):

    pass


class Album(proxies.Localizable):

    pass


class AlbumLocalization(proxies.Localization):

    pass


class Video(proxies.Localizable):

    pass


class VideoLocalization(proxies.Localization):

    pass
