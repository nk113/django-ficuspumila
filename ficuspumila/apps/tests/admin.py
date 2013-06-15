# -*- coding: utf-8 -*-
import logging

from datetime import datetime
from django.contrib import admin as djadmin
from django.utils.translation import ugettext as _

from ficuspumila.apps.tests import proxies
from ficuspumila.apps.tests import forms
from ficuspumila.core import admin as coreadmin
from ficuspumila.core.content import admin
from ficuspumila.settings import ficuspumila as settings


logger = logging.getLogger(__name__)


def _title(obj):
    localization = obj.localize()
    return '(%s): %s' % (localization.language_code, localization.title,)
_title.short_description = _(u'Title')

def _item(obj):
    return ('<a href="/%scontent/item/?id=%i">%s</a>' % (settings('ADMIN_PREFIX'),
                                                         obj.item.id,
                                                         obj.item))
_item.short_description = _(u'Item')
_item.allow_tags = True


class Metadata(admin.Metadata):

    def lookup_allowed(self, key, value):
        if key in ('item__parents', 'item__children',):
            return True
        return super(Metadata, self).lookup_allowed(key)


class TrackLocalizationInline(djadmin.TabularInline):

    extra = 0
    form = forms.TrackLocalizationModel
    model = proxies.TrackLocalization
    readonly_fields = ('id',)


class AlbumLocalizationInline(djadmin.TabularInline):

    extra = 0
    form = forms.AlbumLocalizationModel
    model = proxies.AlbumLocalization
    readonly_fields = ('id',)


class VideoLocalizationInline(djadmin.TabularInline):

    extra = 0
    form = forms.VideoLocalizationModel
    model = proxies.VideoLocalization
    readonly_fields = ('id',)


class Track(Metadata):

    form = forms.TrackModel
    init_options = False
    inlines = (TrackLocalizationInline,)
    list_display = (_title, _item, '_parents', 'length', 'isrc',)
    search_fields = ('^item__source_item_id', '^isrc',)

    def _parents(self, obj):
        return coreadmin.related_objects(obj.item,
                                         'parents',
                                         '/%stests/album/?item__children=%s' % (settings('ADMIN_PREFIX'),
                                                                                obj.item.pk))
    _parents.short_description = _(u'Parents')
    _parents.allow_tags = True


class Album(Metadata):

    form = forms.AlbumModel
    init_options = False
    inlines = (AlbumLocalizationInline,)
    list_display = (_title, _item, '_children',)
    search_fields = ('^item__source_item_id',)

    def _children(self, obj):
        return coreadmin.related_objects(obj.item,
                                         'children',
                                         '/%stests/track/?item__parents=%s' % (settings('ADMIN_PREFIX'),
                                                                               obj.item.pk))
    _children.short_description = _(u'Children')
    _children.allow_tags = True


class Video(Metadata):

    form = forms.VideoModel
    inlines = (VideoLocalizationInline,)
    init_options = False
    list_display = (_title, _item,)
    search_fields = ('^item__source_item_id',)


djadmin.site.register(proxies.Track, Track)
djadmin.site.register(proxies.Album, Album)
djadmin.site.register(proxies.Video, Video)
