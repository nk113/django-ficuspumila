# -*- encoding: utf-8 -*-
import logging

from django.contrib.admin import (
    ModelAdmin as DjangoModelAdmin,
    TabularInline as DjangoTabularInline,
)


logger = logging.getLogger(__name__)


class ModelAdmin(DjangoModelAdmin):

    actions = None

    def __init__(self, *args, **kwargs):
        model = args[0]

        if len(self.readonly_fields) < 1:
            self.readonly_fields = [f.name for f in model._meta.fields if hasattr(f, 'help_text')]

        super(ModelAdmin, self).__init__(*args, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False


class DateHierarchicalModelAdmin(ModelAdmin):

    date_hierarchy = 'ctime'


class EventModelAdmin(DateHierarchicalModelAdmin):

     def has_add_permission(self, request):
        return False


class TabularInline(DjangoTabularInline):

    pass


class NotificationInline(TabularInline):

    extra = 0
    fields = ('status_code', 'url', 'content',)
    readonly_fields = ('status_code', 'url', 'content',)
