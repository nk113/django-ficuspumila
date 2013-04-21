# -*- coding: utf-8 -*-                                                
import logging

from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.cache import SimpleCache
from tastypie.exceptions import ImmediateHttpResponse, InvalidFilterError
from tastypie import fields
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource as TastypieModelResource
from tastypie.throttle import CacheThrottle
from tastypie.validation import CleanedDataFormValidation

from .auth.sso import Authenticator as SsoAuthenticator


ALL_METHODS = ('get', 'post', 'put', 'patch', 'delete',)
EXACT = ('exact',)
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
            authenticated = SsoAuthenticator.from_request(
                                request).is_authenticated()

        logger.debug(u'authenticated as (%s%s)' % (
                         request.user,
                         ' - superuser' if request.user.is_superuser else '',))

        return authenticated

    def get_identifier(self, request):
        return getattr(request, 'user', None).username


class Authorization(DjangoAuthorization):

    pass


class SuperuserAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        authenticated = super(SuperuserAuthentication,
                              self).is_authenticated(request, **kwargs)
        return request.user.is_superuser


class SuperuserAuthorization(Authorization):

    pass


class Throttle(CacheThrottle):

    def should_be_throttled(self, identifier, **kwargs):
        try:
            user = AuthUser.objects.get(username=identifier)
            if user.is_superuser:
                return False
        except AuthUser.DoesNotExist, e:
            pass

        return super(Throttle, self).should_be_throttled(identifier,
                                                         **kwargs)


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


class ModelResource(TastypieModelResource):

    def __init__(self):
        # to support to_many related field filtering
        self._meta.filtering.update({
            'id': EXACT_IN,
        })
        super(ModelResource, self).__init__()

    def debug(self, request, response, log=logger.debug):
        info = log if log == logger.exception else logger.info

        info(u'API (%s): %s %s %s' % (
             request.user,
             request.method, response.status_code,
             request.META.get('PATH_INFO')))

        if len(request.raw_post_data):
            log(u'API (%s): Data: %s' % (
                request.user, request.raw_post_data,))

        if len(response.content):
            log(u'API (%s): Content: %s' % (request.user,
                                           response.content,))

    def dispatch(self, request_type, request, **kwargs):
        response = super(ModelResource, self).dispatch(request_type,
                                                  request,
                                                  **kwargs)

        self.debug(request, response)

        return response

    def is_authenticated(self, request):
        super(ModelResource, self).is_authenticated(request)

        # allow superuser all operations dynamically
        if request.user.is_superuser:

            logger.debug(u'hello superuser you can do anything with this resource...')

            self._meta.list_allowed_methods = ALL_METHODS
            self._meta.detail_allowed_methods = ALL_METHODS

            for field in self._meta.excludes:
                self.fields[field] = fields.CharField(attribute=field,
                                                      blank=True,
                                                      null=True)

    def _handle_500(self, request, exception):
        response = super(ModelResource, self)._handle_500(request, exception)
        self.debug(request, response, logger.exception)
        return response

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(ModelResource, self).build_filters(filters)

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

    def build_schema(self):
        schema = super(ModelResource, self).build_schema()

        # add schema url of to_class to the field schema
        for field_name, field_object in self.fields.items():
            if isinstance(field_object, fields.RelatedField):
                schema['fields'][field_name]['schema'] = field_object.to_class().get_resource_uri(url_name='api_get_schema')

        return schema

    def apply_filters(self, request, applicable_filters):
        filtered = super(ModelResource, self).apply_filters(request,
                                                       applicable_filters)

        if applicable_filters and 'Q' in applicable_filters:
            return filtered.filter(applicable_filters.pop('Q'))

        return filtered


class Meta(object):

    allowed_methods = ('get',)
    authentication = Authentication()
    authorization = Authorization()
    cache = SimpleCache()
    throttle = Throttle()


class SuperuserMeta(Meta):

    allowed_methods = ALL_METHODS
    authentication = SuperuserAuthentication()
    authorization = SuperuserAuthorization()


class ServiceMeta(Meta):

    excludes = ['notification_url', 'hmac_key', 'token_key', 'token_iv',]
