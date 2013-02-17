# -*- coding: utf-8 -*-                                                
import logging

from tastypie.authentication import BasicAuthentication

from auth import SSOAuthenticator


logger = logging.getLogger(__name__)


class SSOAuthentication(BasicAuthentication):

    def __init__(self, *args, **kwargs):
        super(SSOAuthetication, self).__init__()

    def is_authenticated(self, request, **kwargs):
        if super(SSOAuthentication, self).is_authenticated(request, **kwargs):
            return true
        else:
            return SSOAuthenticator.from_request(request).is_authenticated()

    def get_identifier(self, request):
        return getattr(request, 'user', None)


class SSOAuthorization(ResourceAuthorization):

    def is_authorized(self, request, obj=None):
        return True
