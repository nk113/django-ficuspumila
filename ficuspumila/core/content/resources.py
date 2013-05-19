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

from ficuspumila.core import resources
from ficuspumila.core.content import models
from ficuspumila.core.auth import resources as auth_resources
from ficuspumila.core.exceptions import ResourceException
from ficuspumila.settings import (
    get as settings_get,
    ficuspumila as settings,
)


logger = logging.getLogger(__name__)


class Content(resources.ModelResource):

    def obj_create(self, bundle, **kwargs):
        if hasattr(bundle.request.user, 'owner'):
            if hasattr(self._meta.object_class, 'source'):
                kwargs['source'] = bundle.request.user.owner.source
            if hasattr(self._meta.object_class, 'owner'):
                kwargs['owner'] = bundle.request.user.owner
            if hasattr(self._meta.object_class, 'event'):
                kwargs['event__source'] = bundle.request.user.owner.source
            return super(Content, self).obj_create(bundle,
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


class Genre(Content):

    class Meta(resources.Meta):

        queryset = models.Genre.objects.all()
        resource_name = 'genre'
        filtering = {
            'name': resources.EXACT_IN_STARTSWITH,
            'type': resources.EXACT_IN,
        }


class GenreLocalization(Content):

    class Meta(resources.Meta):

        queryset = models.GenreLocalization.objects.all()
        resource_name = 'genrelocalization'
        filtering = {
            'genre'   : ALL_WITH_RELATIONS,
            'language_code': resources.EXACT_IN,
            'name'    : resources.EXACT_IN_STARTSWITH,
        }

    genre = fields.ForeignKey(Genre, 'genre')


class Source(Content):

    class Meta(resources.ServiceMeta):

        queryset = models.Source.objects.all()
        resource_name = 'source'
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'name': resources.EXACT_IN_CONTAINS,
            'source_owener_id': resources.EXACT_IN_STARTSWITH,
            'attributes': ALL_WITH_RELATIONS,
            'events': ALL_WITH_RELATIONS,
        }

    user = fields.ForeignKey(auth_resources.User, 'user')
    attributes = fields.ToManyField(
                         'ficuspumila.core.content.resources.SourceAttribute',
                         'attributes')
    events = resources.LimitedToManyField(
                         'ficuspumila.core.content.resources.SourceEvent',
                         'events', order_by='-id',)
    notification_urls = fields.ListField('notification_urls')


class SourceAttributeName(Content):

    class Meta(resources.Meta):

        queryset = models.SourceAttributeName.objects.all()
        resource_name = 'sourceattributename'
        filtering = {
            'name'  : resources.EXACT_IN,
        }


class SourceAttribute(Content):

    class Meta(resources.Meta):

        queryset = models.SourceAttribute.objects.all()
        resource_name = 'sourceattribute'
        filtering = {
            'source': ALL_WITH_RELATIONS,
            'name'  : ALL_WITH_RELATIONS,
            'value' : resources.EXACT_IN_STARTSWITH,
        }

    source = fields.ForeignKey(Source, 'source')
    name = fields.ForeignKey(SourceAttributeName, 'name')


class SourceEventName(Content):

    class Meta(resources.Meta):

        queryset = models.SourceEventName.objects.all()
        resource_name = 'sourceeventname'
        filtering = {
            'name'  : resources.EXACT_IN,
        }


class SourceEvent(Content):

    class Meta(resources.Meta):

        queryset = models.SourceEvent.objects.all()
        resource_name = 'sourceevent'
        filtering = {
            'source' : ALL_WITH_RELATIONS,
            'name'   : ALL_WITH_RELATIONS,
            'message': resources.EXACT_IN_CONTAINS,
            'ctime'  : resources.EXACT_IN_GET_LTE_DATE,
            'utime'  : resources.EXACT_IN_GET_LTE_DATE,
        }

    source = fields.ForeignKey(Source, 'source')
    name = fields.ForeignKey(SourceEventName, 'name')
    message = resources.JsonField('message', null=False, blank=True)
    notifications = resources.LimitedToManyField(
                         'ficuspumila.core.content.resources.SourceNotification',
                         'notifications', order_by='-id')


class SourceNotification(Content):

    class Meta(resources.Meta):

        queryset = models.SourceNotification.objects.all()
        resource_name = 'sourcenotification'
        filtering = {
            'event'      : ALL_WITH_RELATIONS,
            'url'        : resources.EXACT_IN_CONTAINS,
            'status_code': resources.EXACT_IN,
            'content'    : resources.EXACT_IN_CONTAINS,
            'ctime'      : resources.EXACT_IN_GET_LTE_DATE,
            'utime'      : resources.EXACT_IN_GET_LTE_DATE,
        }

    event = fields.ForeignKey(SourceEvent, 'event')


class Owner(Content):

    class Meta(resources.Meta):

        queryset = models.Owner.objects.all()
        resource_name = 'owner'
        filtering = {
            'user'  : ALL_WITH_RELATIONS,
            'source': ALL_WITH_RELATIONS,
            'source_owner_id': resources.EXACT_IN_STARTSWITH,
        }

    user = fields.ForeignKey(auth_resources.User, 'user')
    source = fields.ForeignKey(Source, 'source')


class FileType(Content):

    class Meta(resources.Meta):

        queryset = models.FileType.objects.all()
        resource_name = 'filetype'
        filtering = {
            'name'     : resources.EXACT_IN_STARTSWITH,
            'mimetype' : resources.EXACT_IN_CONTAINS,
            'extention': resources.EXACT_IN_STARTSWITH,
        }

    mime_types = fields.ListField('mime_types')
    extensions = fields.ListField('extensions')


class FileSpecification(Content):

    class Meta(resources.Meta):

        queryset = models.FileSpecification.objects.all()
        resource_name = 'filespecification'
        filtering = {
            'owner': ALL_WITH_RELATIONS,
            'name' : resources.EXACT_IN_STARTSWITH,
            'parent' : ALL_WITH_RELATIONS,
            'children' : ALL_WITH_RELATIONS,
            'type' : ALL_WITH_RELATIONS,
        }

    owner = fields.ForeignKey(Owner, 'owner')
    parent = fields.ForeignKey(
                         'ficuspumila.core.content.resources.FileSpecification',
                         'parent',
                         null=True)
    children = fields.ToManyField(
                         'ficuspumila.core.content.resources.FileSpecification',
                         'children')
    attributes = fields.ToManyField(
                         'ficuspumila.core.content.resources.FileSpecificationAttribute',
                         'attributes')
    type = fields.ForeignKey(FileType, 'type')


class FileSpecificationAttributeName(Content):

    class Meta(resources.Meta):

        queryset = models.FileSpecificationAttributeName.objects.all()
        resource_name = 'filespecificationattributename'
        filtering = {
            'name'  : resources.EXACT_IN,
        }


class FileSpecificationAttribute(Content):

    class Meta(resources.Meta):

        queryset = models.FileSpecificationAttribute.objects.all()
        resource_name = 'filespecificationattribute'
        filtering = {
            'filespecification' : ALL_WITH_RELATIONS,
            'name' : ALL_WITH_RELATIONS,
            'value': resources.EXACT_IN_STARTSWITH,
        }

    filespecification = fields.ForeignKey(FileSpecification, 'filespecification')
    name = fields.ForeignKey(FileSpecificationAttributeName, 'name')


class ResourceType(Content):

    class Meta(resources.Meta):

        queryset = models.ResourceType.objects.all()
        resource_name = 'resourcetype'
        filtering = {
            'name'      : resources.EXACT_IN_STARTSWITH,
            'category'  : resources.EXACT_IN,
            'limited'   : resources.EXACT,
            'streamable': resources.EXACT,
        }


def get_urls(version=1):
    api = Api(api_name='content')

    if version == 1:
        api.register(Genre())
        api.register(GenreLocalization())
        api.register(Source())
        api.register(SourceAttributeName())
        api.register(SourceAttribute())
        api.register(SourceEventName())
        api.register(SourceEvent())
        api.register(SourceNotification())
        api.register(FileType())
        api.register(FileSpecification())
        api.register(FileSpecificationAttributeName())
        api.register(FileSpecificationAttribute())
        api.register(ResourceType())

        api.register(Owner())

    return api.urls
