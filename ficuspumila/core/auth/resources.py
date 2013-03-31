# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.models import User
from tastypie import fields
from tastypie.api import Api

from ficuspumila.core.resources import (
    EXACT_IN, Meta, Resource,
)


logger = logging.getLogger(__name__)


class UserResource(Resource):

    class Meta(Meta):
        queryset = User.objects.filter(is_active=True)
        resource_name = 'user'
        excludes = ('password', 'is_active', 'is_superuser', 'is_staff',)
        filtering = {
           'username': EXACT_IN,
        }

    source = fields.ForeignKey('ficuspumila.core.content.resources.SourceResource',
                               'source')
    owner = fields.ForeignKey('ficuspumila.core.content.resources.OwnerResource',
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


def get_urls(version=1):
    api = Api(api_name='auth')

    if version == 1:
        api.register(UserResource())

    return api.urls
