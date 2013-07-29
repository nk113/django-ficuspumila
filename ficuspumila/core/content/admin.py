# -*- encoding: utf-8 -*-
import logging

from django.contrib import admin as djadmin
from django.template.defaultfilters import date
from django.utils.translation import ugettext as _

from ficuspumila.core import admin
from ficuspumila.core.content import forms
from ficuspumila.core.content import proxies
from ficuspumila.core.utils import get_default_language_code
from ficuspumila.settings import ficuspumila as settings


logger = logging.getLogger(__name__)


def _user(obj):
    return ('<a href="/%sauth/user/?id=%i">%s</a>' % (settings('ADMIN_PREFIX'),
                                                      obj.user.id,
                                                      obj.user))
_user.short_description = _(u'Django auth user')
_user.allow_tags = True

def _owner(obj):
    if obj.owner:
        return '<a href="/%scontent/owner/?user_id=%i">%s</a>' % (settings('ADMIN_PREFIX'),
                                                                  obj.owner.user_id,
                                                                  obj.owner)
_owner.short_description = _(u'Owner')
_owner.allow_tags = True


class GenreLocalizationInline(admin.TabularInline):

    extra = 0
    model = proxies.GenreLocalization


class Genre(admin.ModelAdmin):

    form = forms.GenreModel
    inlines = (
        GenreLocalizationInline,
    )
    list_display  = ('name', 'media_type',)
    list_filter   = ('media_type',)
    readonly_fields = ('id',)
    search_fields = ('^name',)


class SourceAttributeName(admin.ModelAdmin):

    list_display  = ('name',)
    readonly_fields = ('id',)


class SourceAttributeInline(admin.TabularInline):

    model = proxies.SourceAttribute


class Source(admin.ModelAdmin):

    form = forms.SourceModel
    inlines = (
        SourceAttributeInline,
    )
    list_display    = ('name', _user,)
    raw_id_fields   = ('user',)
    readonly_fields = ('hmac_key', 'token_key', 'token_iv',)
    search_fields   = ('^user__username', '^name',)


class SourceEventName(admin.ModelAdmin):

    list_display  = ('name',)
    readonly_fields = ('id',)


class SourceNotificationInline(admin.NotificationInline):

    model = proxies.SourceNotification


class SourceEvent(admin.EventModelAdmin):

    form = forms.SourceEventModel
    inlines = (
        SourceNotificationInline,
    )
    list_display  = ('ctime', '_source', '_name',)
    list_filter   = ('source', 'name',)
    raw_id_fields = ('source',)

    def _source(self, obj):
        return ('<a href="/%scontent/source/?user__id=%i">%s</a>' % (settings('ADMIN_PREFIX'),
                                                          obj.source.user_id,
                                                          obj.source))
    _source.short_description = _(u'Source')
    _source.allow_tags = True

    def _name(self, obj):
        return ('<a href="/%scontent/sourceeventname/?id=%i">%s</a>' % (settings('ADMIN_PREFIX'),
                                                          obj.name.id,
                                                          obj.name))
    _name.short_description = _(u'Name')
    _name.allow_tags = True


class Owner(admin.ModelAdmin):

    init_options = False

    form = forms.OwnerModel
    list_display  = ('_owner', _user, 'source', 'source_owner_id', '_filespecifications', '_items',)
    list_filter   = ('source',)
    raw_id_fields   = ('user',)
    search_fields   = ('^user__username', '^name', '^source_owner_id',)

    def _owner(self, obj):
        return obj
    _owner.short_description = _(u'Owner')


    def _items(self, obj):
        return admin.related_objects(obj,
                                     'item_set',
                                     '/%scontent/item/?owner=%i' % (settings('ADMIN_PREFIX'),
                                                                    obj.user.id))
    _items.short_description = _(u'Items')
    _items.allow_tags = True

    def _filespecifications(self, obj):
        return admin.related_objects(obj,
                                     'filespecification_set',
                                     '/%scontent/filespecification/?owner=%s' % (settings('ADMIN_PREFIX'),
                                                                                 obj.user.id))
    _filespecifications.short_description = _(u'File specifications')
    _filespecifications.allow_tags = True



class FileType(admin.ModelAdmin):

    form = forms.FileTypeModel
    list_display  = ('name', '_mime_types', '_extensions',)
    readonly_fields = ('id',)

    def _mime_types(self, obj):
        return ', '.join(obj.mime_types)
    _mime_types.short_desciption = _(u'Mime types')

    def _extensions(self, obj):
        return ', '.join(obj.extensions)
    _extensions.short_desciption = _(u'Extensions')


class FileSpecification(admin.ModelAdmin):

    form = forms.FileSpecificationModel
    list_display  = ('id', 'name', 'type', _owner, '_parent',)
    list_filter  = ('owner__source', 'type',)
    raw_id_fields = ('owner', 'parent',)
    readonly_fields = ('id',)

    def _parent(self, obj):
        if obj.parent:
            return '<a href="/%scontent/filespecification/?id=%i">%s</a>' % (settings('ADMIN_PREFIX'),
                                                                             obj.parent.id,
                                                                             obj.parent)
        return None
    _parent.short_description = _(u'Parent')
    _parent.allow_tags = True


class Item(admin.ModelAdmin):

    form = forms.ItemModel
    list_display  = ('id', 'item_type', 'meta_type', _owner, 'source_item_id', '_parents', '_children', 'enabled',)
    list_filter  = ('owner__source', 'enabled',)
    raw_id_fields = ('owner', 'parents',)
    readonly_fields = ('id',)
    search_fields = ('^source_item_id', 'parents', 'children',)

    def _parents(self, obj):
        return admin.related_objects(obj,
                                     'parents',
                                     '/%scontent/item/?children=%s' % (settings('ADMIN_PREFIX'),
                                                                       obj.pk))
    _parents.short_description = _(u'Parents')
    _parents.allow_tags = True

    def _children(self, obj):
        return admin.related_objects(obj,
                                     'children',
                                     '/%scontent/item/?parents=%s' % (settings('ADMIN_PREFIX'),
                                                                     obj.pk))
    _children.short_description = _(u'Children')
    _children.allow_tags = True


class Metadata(admin.ModelAdmin):

    actions = ('delete_selected',)
    raw_id_fields = ('item',)

    def _item(self, obj):
        if obj.item:
            return '<a href="/%scontent/item/?id=%i">%s</a>' % (settings('ADMIN_PREFIX'),
                                                                item.id,
                                                                item)
        return None
    _item.short_description = _(u'Item')
    _item.allow_tags = True


djadmin.site.register(proxies.Genre, Genre)
djadmin.site.register(proxies.SourceAttributeName, SourceAttributeName)
djadmin.site.register(proxies.Source, Source)
djadmin.site.register(proxies.SourceEventName, SourceEventName)
djadmin.site.register(proxies.SourceEvent, SourceEvent)
djadmin.site.register(proxies.Owner, Owner)
djadmin.site.register(proxies.FileType, FileType)
djadmin.site.register(proxies.FileSpecification, FileSpecification)
djadmin.site.register(proxies.Item, Item)
