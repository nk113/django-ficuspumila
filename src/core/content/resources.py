# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpForbidden

from core.resources import Resource


logger = logging.getLogger(__name__)


class ContentResource(Resource):

    def obj_create(self, bundle, request=None, **kwargs):
        if hasattr(request.user, 'owner'):
            if hasattr(self._meta.object_class, 'source'):
                kwargs['source'] = request.user.owner.source
            if hasattr(self._meta.object_class, 'owner'):
                kwargs['owner'] = request.user.owner
            if hasattr(self._meta.object_class, 'event'):
                kwargs['event__source'] = request.user.owner.source
            return super(ResourceBase, self).obj_create(bundle,
                                                        request,
                                                        **kwargs)

        raise ImmediateHttpResponse(response=HttpForbidden())

    def apply_authorization_limits(self, request, object_list):
        if hasattr(request.user, 'owner'):
            if hasattr(self._meta.object_class, 'source'):
                return object_list.filter(source=request.user.owner.source)
            if hasattr(self._meta.object_class, 'owner'):
                return object_list.filter(source=request.user.owner)
            if hasattr(self._meta.object_class, 'event'):
                return object_list.filter(event__source=request.user.owner.source)
            return object_list

        raise ImmediateHttpResponse(response=HttpForbidden())


