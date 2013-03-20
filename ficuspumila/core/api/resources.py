# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.api import Api
from tastypie.cache import SimpleCache

from ficuspumila.core.common.models import Country
from ficuspumila.core.resources import (
    EXACT_IN,
    EXACT_IN_CONTAINS,
    EXACT_IN_GTE_LTE,
    EXACT_IN_GET_LTE_DATE,
    EXACT_IN_STARTSWITH,
    AdminMeta, Resource,
)


logger = logging.getLogger(__name__)


class UserResource(Resource):

    class Meta(AdminMeta):
        queryset = User.objects.filter(is_active=True)
        resource_name = 'user'
        allowed_methods = ('get', 'post', 'put', 'patch',)
        cache = SimpleCache()
        excludes = ('password', 'is_active', 'is_superuser', 'is_staff',)
        filtering = {
           'username': EXACT_IN,
        }

    source = fields.ForeignKey('ficuspumila.core.content.api.resources.SourceResource',
                               'source')
    owner = fields.ForeignKey('ficuspumila.core.content.api.resources.OwnerResource',
                              'owner')


    def obj_create(self, bundle, request=None, **kwargs):
        # TODO
        return super(UserResource, self).obj_create(bundle,
                                                    request=None,
                                                    **kwargs)

    def apply_authorization_limits(self, request, object_list):
        # TODO
        return super(UserResource, self).apply_authorization_limits(request,
                                                                    object_list)


class CountryResource(Resource):

    class Meta:
        queryset = Country.objects.all()
        resource_name = 'country'
        allowed_methods = ('get',)
        cache = SimpleCache()
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


def get_urls(version=1):
    api = Api(api_name='core')

    if version == 1:
        api.register(UserResource())
        api.register(CountryResource())

    return api.urls
