# -*- encoding: utf-8 -*-
import logging

from django.contrib import admin as djadmin
from django.utils.translation import ugettext as _

from ficuspumila.core import admin
from ficuspumila.core.common import models


logger = logging.getLogger(__name__)


class Country(admin.ModelAdmin):

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


djadmin.site.register(models.Country, Country)
