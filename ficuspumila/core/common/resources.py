# -*- coding: utf-8 -*-
import logging

from tastypie import fields
from tastypie.api import Api

from ficuspumila.core import resources
from ficuspumila.core.common import models


logger = logging.getLogger(__name__)


class Country(resources.ModelResource):

    class Meta(resources.Meta):
        queryset = models.Country.objects.all()
        resource_name = 'country'
        filtering = {
            'alpha2': resources.EXACT_IN,
            'alpha3': resources.EXACT_IN,
            'numeric3': resources.EXACT_IN,
            'fips': resources.EXACT_IN,
            'name': resources.EXACT_IN_STARTSWITH,
            'capital': resources.EXACT_IN_STARTSWITH,
            'area': resources.EXACT_IN_GTE_LTE,
            'population': resources.EXACT_IN_GTE_LTE,
            'continent': resources.EXACT_IN,
            'tld': resources.EXACT_IN,
            'currency_code': resources.EXACT_IN,
            'currency_name': resources.EXACT_IN_STARTSWITH,
            'phone': resources.EXACT_IN_STARTSWITH,
            'postal_code_format': resources.EXACT_IN_STARTSWITH,
            'postal_code_regex': resources.EXACT_IN_STARTSWITH,
            'languages': resources.EXACT_IN_CONTAINS,
            'geonameid': resources.EXACT_IN_GTE_LTE,
            'neighbours': resources.EXACT_IN_CONTAINS,
            'equivalent_fips_code': resources.EXACT_IN,
        }

    languages = fields.ListField('languages')
    neighbours = fields.ListField('neighbours')


def get_urls(version=1):
    api = Api(api_name='common')

    if version == 1:
        api.register(Country())

    return api.urls
