# -*- encoding: utf-8 -*-
import logging

from django.contrib import admin


logger = logging.getLogger(__name__)


class DateHierarchicalAdmin(admin.ModelAdmin):

    date_hierarchy = 'ctime'

