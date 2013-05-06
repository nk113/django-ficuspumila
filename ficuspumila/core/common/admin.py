# -*- encoding: utf-8 -*-
import logging

from django.contrib import admin
from django.template.defaultfilters import date
from django.utils.translation import ugettext as _

from ficuspumila.core.admin import ModelAdmin
from .models import Country


logger = logging.getLogger(__name__)


class CountryAdmin(ModelAdmin):

    list_display  = ('name', 'alpha2', 'currency_code', '_languages',
                     '_neighbours',)
    list_filter   = ('continent',)
    search_fields = ('=alpha2', '=alpha3', '=numeric3', '=fips', '^name',
                     '=currency_code', '^currency_name',
                     'languages', 'neighbours',)

    def _languages(self, obj):
        return ', '.join(obj.languages)
    _languages.short_desciption = _(u'Languages')

    def _neighbours(self, obj):
        return ', '.join(obj.neighbours)
    _neighbours.short_desciption = _(u'Neighbours')


admin.site.register(Country, CountryAdmin)
