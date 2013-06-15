# -*- coding: utf-8 -*-
import logging

from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
from tastypie import fields
from tastypie.api import Api
from tastypie.http import HttpForbidden
from tastypie.resources import ALL, ALL_WITH_RELATIONS

from ficuspumila.apps.tests import models
from ficuspumila.core import resources
from ficuspumila.settings import (
    get as settings_get,
    ficuspumila as settings,
)


logger = logging.getLogger(__name__)


class Track(resources.ModelResource):

    class Meta(resources.Meta):

        queryset = models.Track.objects.all()
        resource_name = 'track'
        filtering = {
            'item': ALL_WITH_RELATIONS,
        }


class TrackLocalization(resources.ModelResource):

    class Meta(resources.Meta):

        queryset = models.TrackLocalization.objects.all()
        resource_name = 'tracklocalization'
        filtering = {
            'language_code': resources.EXACT_IN,
            'track': ALL_WITH_RELATIONS,
            'title': resources.EXACT_IN_STARTSWITH,
        }

    track = fields.ForeignKey(Track, 'track')


class Album(resources.ModelResource):

    class Meta(resources.Meta):

        queryset = models.Album.objects.all()
        resource_name = 'album'
        filtering = {
            'item': ALL_WITH_RELATIONS,
        }


class AlbumLocalization(resources.ModelResource):

    class Meta(resources.Meta):

        queryset = models.AlbumLocalization.objects.all()
        resource_name = 'albumlocalization'
        filtering = {
            'album': ALL_WITH_RELATIONS,
            'language_code': resources.EXACT_IN,
            'title': resources.EXACT_IN_STARTSWITH,
        }

    album = fields.ForeignKey(Album, 'album')



class Video(resources.ModelResource):

    class Meta(resources.Meta):

        queryset = models.Video.objects.all()
        resource_name = 'video'
        filtering = {
            'item': ALL_WITH_RELATIONS,
        }


class VideoLocalization(resources.ModelResource):

    class Meta(resources.Meta):

        queryset = models.TrackLocalization.objects.all()
        resource_name = 'videolocalization'
        filtering = {
            'language_code': resources.EXACT_IN,
            'title': resources.EXACT_IN_STARTSWITH,
            'video': ALL_WITH_RELATIONS,
        }

    video = fields.ForeignKey(Video, 'video')


def get_urls(version=1):
    api = Api(api_name='tests')

    if version == 1:
        api.register(Track())
        api.register(TrackLocalization())
        api.register(Album())
        api.register(AlbumLocalization())
        api.register(Video())
        api.register(VideoLocalization())

    return api.urls
