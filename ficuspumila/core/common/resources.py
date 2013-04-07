# -*- coding: utf-8 -*-
import logging

from tastypie import fields
from tastypie.api import Api

from ficuspumila.core.resources import (
    EXACT_IN,
    EXACT_IN_CONTAINS,
    EXACT_IN_GTE_LTE,
    EXACT_IN_GET_LTE_DATE,
    EXACT_IN_STARTSWITH,
    Meta, ModelResource,
)
from .models import Country


logger = logging.getLogger(__name__)


class CountryResource(ModelResource):

    class Meta(Meta):
        queryset = Country.objects.all()
        resource_name = 'country'
        filtering = {
            'alpha2': EXACT_IN,
            'alpha3': EXACT_IN,
            'numeric3': EXACT_IN,
            'fips': EXACT_IN,
            'name': EXACT_IN_STARTSWITH,
            'capital': EXACT_IN_STARTSWITH,
            'area': EXACT_IN_GTE_LTE,
            'population': EXACT_IN_GTE_LTE,
            'continent': EXACT_IN,
            'tld': EXACT_IN,
            'currency_code': EXACT_IN,
            'currency_name': EXACT_IN_STARTSWITH,
            'phone': EXACT_IN_STARTSWITH,
            'postal_code_format': EXACT_IN_STARTSWITH,
            'postal_code_regex': EXACT_IN_STARTSWITH,
            'languages': EXACT_IN_CONTAINS,
            'geonameid': EXACT_IN_GTE_LTE,
            'neighbours': EXACT_IN_CONTAINS,
            'equivalent_fips_code': EXACT_IN,
        }

    languages = fields.ListField('languages')
    neighbours = fields.ListField('neighbours')


def get_urls(version=1):
    api = Api(api_name='common')

    if version == 1:
        api.register(CountryResource())

    return api.urls
