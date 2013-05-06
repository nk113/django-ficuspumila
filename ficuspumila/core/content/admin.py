# -*- encoding: utf-8 -*-
import logging

from django.contrib import admin
from django.template.defaultfilters import date
from django.utils.translation import ugettext as _

from ficuspumila.core.admin import (
    EventModelAdmin, ModelAdmin,
    NotificationInline,
    TabularInline,
)
from ficuspumila.core.utils import get_default_language_code
from ficuspumila.settings import ficuspumila as settings
from .forms import (
    GenreModelForm, FileTypeModelForm,
    SourceModelForm, SourceEventModelForm,
)
from .models import (
    Genre, GenreLocalization, FileType,
    Source, SourceEvent, SourceEventName, SourceNotification,
)


logger = logging.getLogger(__name__)


class GenreLocalizationInline(TabularInline):

    extra = 0
    model = GenreLocalization


class GenreAdmin(ModelAdmin):

    form = GenreModelForm
    inlines = (
        GenreLocalizationInline,
    )
    list_display  = ('name', 'category',)
    readonly_fields = ('id',)
    search_fields = ('^name',)

admin.site.register(Genre, GenreAdmin)


class SourceAdmin(ModelAdmin):

    form = SourceModelForm
    list_display    = ('name', '_user',)
    raw_id_fields   = ('user',)
    readonly_fields = ('hmac_key', 'token_key', 'token_iv',)
    search_fields   = ('^user__username', '^name',)

    def _user(self, obj):
        return ('<a href="/%sauth/user/?id=%i">%s</a>' % (settings('ADMIN_PREFIX'),
                                                          obj.user.id,
                                                          obj.user))
    _user.short_description = _(u'Django auth user')
    _user.allow_tags = True

admin.site.register(Source, SourceAdmin)


class SourceEventNameAdmin(ModelAdmin):

    list_display  = ('name',)
    readonly_fields = ('id',)

admin.site.register(SourceEventName, SourceEventNameAdmin)


class SourceNotificationInline(NotificationInline):

    model = SourceNotification


class SourceEventAdmin(EventModelAdmin):

    form = SourceEventModelForm
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

admin.site.register(SourceEvent, SourceEventAdmin)


class FileTypeAdmin(ModelAdmin):

    form = FileTypeModelForm
    list_display  = ('name', '_mime_types', '_extensions',)
    readonly_fields = ('id',)

    def _mime_types(self, obj):
        return ', '.join(obj.mime_types)
    _mime_types.short_desciption = _(u'Mime types')

    def _extensions(self, obj):
        return ', '.join(obj.extensions)
    _extensions.short_desciption = _(u'Extensions')

admin.site.register(FileType, FileTypeAdmin)
