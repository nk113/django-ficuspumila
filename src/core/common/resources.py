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


class Resource(ModelResource):
    id = fields.IntegerField(attribute='id',
                         readonly=True)


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
            'name': ('exact', 'startswith',),
            'alpha2': ('exact',),
        }


class CurrencyResource(Resource):

    class Meta(Meta):
        queryset = Currency.objects.all()
        resource_name = 'currency'
        cache = SimpleCache()
        filtering = {
            'name': ('exact', 'startswith',),
            'code': ('exact',),
        }


def get_urls():
    api = Api(api_name='common')
    api.register(CountryResource())
    api.register(CurrencyResource())
    return api.urls

urls = get_urls()
