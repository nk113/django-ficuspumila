# -*- encoding: utf-8 -*-
import logging

from django.contrib import admin


logger = logging.getLogger(__name__)


def related_objects(obj, related_field, url, default=None):
    manager = getattr(obj, related_field)
    count = manager.count()
    if count:
        latest = manager.latest('pk')
        text = ('%s' % latest).decode('utf-8')
        return '<a href="%s">%s</a>%s%s' % (url,
                                            text[0:25],
                                            ' ...' if len(text) > 25 or count > 1 else '',
                                            '(%s)' % count if count > 1 else '',)
    return default


class ModelAdmin(admin.ModelAdmin):

    actions = None
    init_options = True

    def __init__(self, *args, **kwargs):
        model = args[0]

        if self.init_options and len(self.readonly_fields) < 1:
            self.readonly_fields = [f.name for f in model._meta.fields if hasattr(f, 'help_text')]

        super(ModelAdmin, self).__init__(*args, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False


class DateHierarchicalModelAdmin(ModelAdmin):

    date_hierarchy = 'ctime'


class EventModelAdmin(DateHierarchicalModelAdmin):

     def has_add_permission(self, request):
        return False


class TabularInline(admin.TabularInline):

    pass


class NotificationInline(admin.TabularInline):

    extra = 0
    fields = ('status_code', 'url', 'content',)
    readonly_fields = ('status_code', 'url', 'content',)
