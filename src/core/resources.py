# -*- coding: utf-8 -*-                                                
import logging

from django.conf import settings
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import ImmediateHttpResponse, InvalidFilterError
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource
from tastypie.throttle import CacheThrottle
from tastypie.validation import CleanedDataFormValidation

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

        logger.debug(u'authenticated as user (%s)' % request.user)

        return authenticated

    def get_identifier(self, request):
        return getattr(request, 'user', None).username


class Authorization(DjangoAuthorization):

    pass


class AdminAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        authenticated = super(AdminAuthentication,
                              self).is_authenticated(request, **kwargs)
        return request.user.is_superuser


class AdminAuthorization(Authorization):

    pass


class Throttle(CacheThrottle):

    def should_be_throttled(self, identifier, **kwargs):
        if identifier == settings.SYSTEM_USERNAME:
            return False
        return super(Throttele, self).should_be_throttled(self,
                                                          identifier,
                                                          **kwargs)

    def accessed(self, identifier, **kwargs):
        pass


class FormValidation(CleanedDataFormValidation):
    """
    An extension of FormValidation that allows to specify a list of fields
    should not be validated. This is useful for ForeignKey, as the
    validation would fail if passed by ID rather than URL, because their
    actual URL is built by alter_deserialized_detail_data AFTER validation
    has taken place.
    """
    def __init__(self, **kwargs):
        self.apply_cleaned_data = kwargs.get('apply_cleaned_data', False)
        self.exclude = kwargs.pop('exclude') if 'exclude' in kwargs else []
        super(FormValidation, self).__init__(**kwargs)

    def is_valid(self, bundle, request=None):
        if 'unit_id' in bundle.obj.__dict__ and hasattr(request, 'unit'):
            bundle.data['unit'] = request.unit.id

        errors = super(FormValidation if self.apply_cleaned_data
                       else FormValidation, self).is_valid(bundle, request)

        for field_not_to_validate in self.exclude:
            errors.pop(field_not_to_validate, None)
        return errors


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
    throttle = Throttle()
    excludes = ('utime',)
    ordering = ('id',)


class AdminMeta(Meta):

    allowed_methods = ('get', 'post', 'put', 'patch', 'delete',)
    authentication = AdminAuthentication()
    authorization = AdminAuthorization()


class ServiceMeta(Meta):

    excludes = ['notification_url', 'hmac_key', 'token_key', 'token_iv',]
