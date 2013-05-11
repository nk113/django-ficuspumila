# -*- coding: utf-8 -*-
import logging

from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
from functools import wraps
from tastypie import fields
from tastypie.api import Api
from tastypie.exceptions import (
    ImmediateHttpResponse,
    InvalidFilterError,
    NotFound
)
from tastypie.http import HttpForbidden
from tastypie.resources import ALL, ALL_WITH_RELATIONS

from ficuspumila.core.auth.resources import UserResource
from ficuspumila.core.resources import (
    ALL_METHODS,
    EXACT,
    EXACT_IN,
    EXACT_IN_CONTAINS,
    EXACT_IN_GTE_LTE,
    EXACT_IN_GET_LTE_DATE,
    EXACT_IN_STARTSWITH,
    JsonField, LimitedToManyField,
    Meta, ModelResource,
    ServiceMeta,
)
from ficuspumila.core.exceptions import ResourceException
from ficuspumila.settings import (
    get as settings_get,
    ficuspumila as settings,
)
from .models import (
    FileSpecification, FileSpecificationAttribute, FileSpecificationAttributeName,
    FileType, Genre, GenreLocalization,
    Owner, ResourceType, Source, SourceAttribute, SourceAttributeName,
    SourceEvent, SourceEventName, SourceNotification,
)


logger = logging.getLogger(__name__)


class ContentResource(ModelResource):

    def obj_create(self, bundle, **kwargs):
        if hasattr(bundle.request.user, 'owner'):
            if hasattr(self._meta.object_class, 'source'):
                kwargs['source'] = bundle.request.user.owner.source
            if hasattr(self._meta.object_class, 'owner'):
                kwargs['owner'] = bundle.request.user.owner
            if hasattr(self._meta.object_class, 'event'):
                kwargs['event__source'] = bundle.request.user.owner.source
            return super(ContentResource, self).obj_create(bundle,
                                                        **kwargs)

        raise ImmediateHttpResponse(response=HttpForbidden())

    def apply_authorization_limits(self, request, object_list):
        if hasattr(request.user, 'owner'):
            if hasattr(self._meta.object_class, 'source'):
                return object_list.filter(source=request.user.owner.source)
            if hasattr(self._meta.object_class, 'owner'):
                return object_list.filter(owner=request.user.owner)
            if hasattr(self._meta.object_class, 'event'):
                return object_list.filter(event__source=request.user.owner.source)
            return object_list

        raise ImmediateHttpResponse(response=HttpForbidden())


class GenreResource(ContentResource):

    class Meta(Meta):

        queryset = Genre.objects.all()
        resource_name = 'genre'
        filtering = {
            'name': EXACT_IN_STARTSWITH,
            'type': EXACT_IN,
        }


class GenreLocalizationResource(ContentResource):

    class Meta(Meta):

        queryset = GenreLocalization.objects.all()
        resource_name = 'genrelocalization'
        filtering = {
            'genre'   : ALL_WITH_RELATIONS,
            'language_code': EXACT_IN,
            'name'    : EXACT_IN_STARTSWITH,
        }

    genre = fields.ForeignKey(GenreResource, 'genre')


class SourceResource(ContentResource):

    class Meta(ServiceMeta):

        queryset = Source.objects.all()
        resource_name = 'source'
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'name': EXACT_IN_CONTAINS,
            'source_owener_id': EXACT_IN_STARTSWITH,
            'attributes': ALL_WITH_RELATIONS,
            'events': ALL_WITH_RELATIONS,
        }

    user = fields.ForeignKey(UserResource, 'user')
    attributes = fields.ToManyField(
                         'ficuspumila.core.content.resources.SourceAttributeResource',
                         'attributes')
    events = LimitedToManyField(
                         'ficuspumila.core.content.resources.SourceEventResource',
                         'events', order_by='-id',)
    notification_urls = fields.ListField('notification_urls')


class SourceAttributeNameResource(ContentResource):

    class Meta(Meta):

        queryset = SourceAttributeName.objects.all()
        resource_name = 'sourceattributename'
        filtering = {
            'name'  : EXACT_IN,
        }


class SourceAttributeResource(ContentResource):

    class Meta(Meta):

        queryset = SourceAttribute.objects.all()
        resource_name = 'sourceattribute'
        filtering = {
            'source': ALL_WITH_RELATIONS,
            'name'  : ALL_WITH_RELATIONS,
            'value' : EXACT_IN_STARTSWITH,
        }

    source = fields.ForeignKey(SourceResource, 'source')
    name = fields.ForeignKey(SourceAttributeNameResource, 'name')


class SourceEventNameResource(ContentResource):

    class Meta(Meta):

        queryset = SourceEventName.objects.all()
        resource_name = 'sourceeventname'
        filtering = {
            'name'  : EXACT_IN,
        }


class SourceEventResource(ContentResource):

    class Meta(Meta):

        queryset = SourceEvent.objects.all()
        resource_name = 'sourceevent'
        filtering = {
            'source' : ALL_WITH_RELATIONS,
            'name'   : ALL_WITH_RELATIONS,
            'message': EXACT_IN_CONTAINS,
            'ctime'  : EXACT_IN_GET_LTE_DATE,
            'utime'  : EXACT_IN_GET_LTE_DATE,
        }

    source = fields.ForeignKey(SourceResource, 'source')
    name = fields.ForeignKey(SourceEventNameResource, 'name')
    message = JsonField('message', null=False, blank=True)
    notifications = LimitedToManyField(
                         'ficuspumila.core.content.resources.SourceNotificationResource',
                         'notifications', order_by='-id')


class SourceNotificationResource(ContentResource):

    class Meta(Meta):

        queryset = SourceNotification.objects.all()
        resource_name = 'sourcenotification'
        filtering = {
            'event'      : ALL_WITH_RELATIONS,
            'url'        : EXACT_IN_CONTAINS,
            'status_code': EXACT_IN,
            'content'    : EXACT_IN_CONTAINS,
            'ctime'      : EXACT_IN_GET_LTE_DATE,
            'utime'      : EXACT_IN_GET_LTE_DATE,
        }

    event = fields.ForeignKey(SourceEventResource, 'event')


class OwnerResource(ContentResource):

    class Meta(Meta):

        queryset = Owner.objects.all()
        resource_name = 'owner'
        filtering = {
            'user'  : ALL_WITH_RELATIONS,
            'source': ALL_WITH_RELATIONS,
            'source_owner_id': EXACT_IN_STARTSWITH,
        }

    user = fields.ForeignKey(UserResource, 'user')
    source = fields.ForeignKey(SourceResource,
                               'source')


class FileTypeResource(ContentResource):

    class Meta(Meta):

        queryset = FileType.objects.all()
        resource_name = 'filetype'
        filtering = {
            'name'     : EXACT_IN_STARTSWITH,
            'mimetype' : EXACT_IN_CONTAINS,
            'extention': EXACT_IN_STARTSWITH,
        }

    mime_types = fields.ListField('mime_types')
    extensions = fields.ListField('extensions')


class FileSpecificationResource(ContentResource):

    class Meta(Meta):

        queryset = FileSpecification.objects.all()
        resource_name = 'filespecification'
        filtering = {
            'owner': ALL_WITH_RELATIONS,
            'name' : EXACT_IN_STARTSWITH,
            'parent' : ALL_WITH_RELATIONS,
            'children' : ALL_WITH_RELATIONS,
            'type' : ALL_WITH_RELATIONS,
        }

    owner = fields.ForeignKey(OwnerResource, 'owner')
    parent = fields.ForeignKey('ficuspumila.core.content.resources.FileSpecificationResource',
                               'parent',
                               null=True)
    children = fields.ToManyField('ficuspumila.core.content.resources.FileSpecificationResource',
                                  'children')
    attributes = fields.ToManyField(
                         'ficuspumila.core.content.resources.FileSpecificationAttributeResource',
                         'attributes')
    type = fields.ForeignKey(FileTypeResource, 'type')


class FileSpecificationAttributeNameResource(ContentResource):

    class Meta(Meta):

        queryset = FileSpecificationAttributeName.objects.all()
        resource_name = 'filespecificationattributename'
        filtering = {
            'name'  : EXACT_IN,
        }


class FileSpecificationAttributeResource(ContentResource):

    class Meta(Meta):

        queryset = FileSpecificationAttribute.objects.all()
        resource_name = 'filespecificationattribute'
        filtering = {
            'filespecification' : ALL_WITH_RELATIONS,
            'name' : ALL_WITH_RELATIONS,
            'value': EXACT_IN_STARTSWITH,
        }

    filespecification = fields.ForeignKey(FileSpecificationResource, 'filespecification')
    name = fields.ForeignKey(FileSpecificationAttributeNameResource, 'name')


class ResourceTypeResource(ContentResource):

    class Meta(Meta):

        queryset = ResourceType.objects.all()
        resource_name = 'resourcetype'
        filtering = {
            'name'      : EXACT_IN_STARTSWITH,
            'category'  : EXACT_IN,
            'limited'   : EXACT,
            'streamable': EXACT,
        }


def get_urls(version=1):
    api = Api(api_name='content')

    if version == 1:
        api.register(GenreResource())
        api.register(GenreLocalizationResource())
        api.register(SourceResource())
        api.register(SourceAttributeNameResource())
        api.register(SourceAttributeResource())
        api.register(SourceEventNameResource())
        api.register(SourceEventResource())
        api.register(SourceNotificationResource())
        api.register(FileTypeResource())
        api.register(FileSpecificationResource())
        api.register(FileSpecificationAttributeNameResource())
        api.register(FileSpecificationAttributeResource())
        api.register(ResourceTypeResource())

        api.register(OwnerResource())

    return api.urls
