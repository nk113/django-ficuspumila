# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from tastypie import fields
from tastypie.api import Api
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.cache import SimpleCache
from tastypie.resources import ModelResource

from .models import Country, Currency


logger = logging.getLogger(__name__)

EXACT_IN = ('exact', 'in',)
EXACT_IN_STARTSWITH = EXACT_IN + ('startswith',)
EXACT_IN_CONTAINS = EXACT_IN + ('contains',)
EXACT_IN_GTE_LTE = EXACT_IN + ('gte', 'lte',)
EXACT_IN_GET_LTE_DATE = EXACT_IN_GTE_LTE + ('date',)


class Resource(ModelResource):
    pass


class Meta(object):
    allowed_methods = ('get',)
    authentication = Authentication()
    authorization = Authorization()


class CountryResource(Resource):

    class Meta(Meta):
        queryset = Country.objects.all()
        resource_name = 'country'
        cache = SimpleCache()
        filtering = {
            'alpha2': EXACT_IN,
            'alpha3': EXACT_IN,
            'numeric3': EXACT_IN,
            'fips': EXACT_IN,
            'name': EXACT_IN_STARTSWITH,
            'capital': EXACT_IN_STARTSWITH,
            'area': EXACT_IN_GET_LTE,
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


def get():
    api = Api(api_name='common')
    api.register(CountryResource())
    return api.urls

urls = get()
