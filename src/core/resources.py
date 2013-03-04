# -*- coding: utf-8 -*-                                                
import logging

from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization as TastypieAuthorization
from tastypie.exceptions import ImmediateHttpResponse, InvalidFilterError
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource

from .auth import SSOAuthenticator


EXACT_IN = ('exact', 'in',)
EXACT_IN_CONTAINS = EXACT_IN + ('contains',)
EXACT_IN_GTE_LTE = EXACT_IN + ('gte', 'lte',)
EXACT_IN_GET_LTE_DATE = EXACT_IN_GTE_LTE + ('date',)
EXACT_IN_STARTSWITH = EXACT_IN + ('startswith',)

logger = logging.getLogger(__name__)


class Authentication(BasicAuthentication):

    def is_authenticated(self, request, **kwargs):
        authenticated = super(Authentication,
                              self).is_authenticated(request, **kwargs)
        if not authenticated or isinstance(authenticated, HttpUnauthorized):
            authenticated = SSOAuthenticator.from_request(
                                request).is_authenticated()

        logger.debug('authenticated as user: %s' % request.user)

        return authenticated

    def get_identifier(self, request):
        return getattr(request, 'user', None)


class Authorization(TastypieAuthorization):

    def is_authorized(self, request, obj=None):
        return super(Authorization).is_authorized(request, obj)


class AdminAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        authenticated = super(AdminAuthentication,
                              self).is_authenticated(request, **kwargs)
        return request.user.is_superuser


class AdminAuthorization(TastypieAuthorization):

    pass


class Resource(ModelResource):

    def debug(self, request, response, log=logger.debug):
        info = log if log == logger.exception else logger.info

        info('API (%s): %s %s %s' % (
             request.user,
             request.method, response.status_code,
             request.META.get('PATH_INFO')))

        if len(request.raw_post_data):
            log('API (%s): Data: %s' % (
                request.user, request.raw_post_data,))

        if len(response.content):
            log('API (%s): Content: %s' % (request.user,
                                           response.content,))

    def dispatch(self, request_type, request, **kwargs):

        response = super(Resource, self).dispatch(request_type,
                                                  request,
                                                  **kwargs)
        self.debug(request, response)
        return response

    def _handle_500(self, request, exception):
        response = super(Resource, self)._handle_500(request, exception)
        self.debug(request, response, logger.exception)
        return response

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(Resource, self).build_filters(filters)

        if('Q' in filters):
            if (not 'Q' in self._meta.filtering
                or self._meta.filtering['Q'] is not ALL):
                raise InvalidFilterError(
                          'Q filtering is not allowed for this resource.')

            q = re.sub('from|import|del|sleep|while|for',
                       '', filters['Q'])
            try:
                orm_filters.update({'Q': (eval(q)) })
            except:
                raise InvalidFilterError('Q has wrong syntax')

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        filtered = super(Resource, self).apply_filters(request,
                                                       applicable_filters)

        if applicable_filters and 'Q' in applicable_filters:
            return filtered.filter(applicable_filters.pop('Q'))

        return filtered


class Meta(object):

    allowed_methods = ('get',)
    authentication = Authentication()
    authorization = Authorization()
    excludes = ['utime',]


class AdminMeta(object):

    allowed_methods = ('get', 'post', 'put', 'patch', 'delete',)
    authentication = AdminAuthentication()
    authorization = AdminAuthorization()
    excludes = ['utime',]


class ServiceMeta(Meta):

    excludes = ['notification_url', 'hmac_key', 'token_key', 'token_iv',]
