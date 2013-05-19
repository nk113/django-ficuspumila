# -*- coding: utf-8 -*-
import logging

from django.contrib.auth import models
from tastypie import fields
from tastypie.api import Api

from ficuspumila.core import resources


logger = logging.getLogger(__name__)


class User(resources.ModelResource):

    class Meta(resources.Meta):
        queryset = models.User.objects.filter(is_active=True)
        resource_name = 'user'
        excludes = ('password', 'is_active', 'is_superuser', 'is_staff',)
        filtering = {
           'username': resources.EXACT_IN,
        }

    source = fields.ForeignKey(
                         'ficuspumila.core.content.resources.Source',
                         'source')
    owner = fields.ForeignKey(
                         'ficuspumila.core.content.resources.Owner',
                         'owner')


    def obj_create(self, bundle, request=None, **kwargs):
        # TODO
        return super(User, self).obj_create(bundle,
                                                    request=None,
                                                    **kwargs)

    def apply_authorization_limits(self, request, object_list):
        # TODO
        return super(User, self).apply_authorization_limits(request,
                                                            object_list)


def get_urls(version=1):
    api = Api(api_name='auth')

    if version == 1:
        api.register(User())

    return api.urls
