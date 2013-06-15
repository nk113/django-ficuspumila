# -*- coding: utf-8 -*-
import logging

from django.db import models as djmodels
from django.utils.translation import ugettext_lazy as _

from ficuspumila.core import models
from ficuspumila.core.utils import get_default_language_code
from ficuspumila.settings import ficuspumila as settings


logger = logging.getLogger(__name__)


class ItemTypes(models.Choice):

    DIGITAL    = 0
    PHYSICAL   = 1
    MEMBERSHIP = 2
    DEFAULT    = DIGITAL


class MediaTypes(models.Choice):

    AUDIO   = 0
    VIDEO   = 1
    PICTURE = 2
    TEXT    = 3
    DEFAULT = AUDIO


class Genre(models.Localizable):

    media_type = djmodels.SmallIntegerField(choices=MediaTypes,
                         default=MediaTypes.DEFAULT)
    name = djmodels.CharField(max_length=128)

    def __unicode__(self):
        return '%s (%s)' % (self.name,
                            self.get_media_type_display())


class GenreLocalization(models.Localization):

    genre = djmodels.ForeignKey(Genre)
    name = djmodels.CharField(max_length=128)

    def __unicode__(self):
        return '(%s): %s' % (self.language_code,
                             self.name,)


class Source(models.Service):

    class Events(models.Choice):

        ITEM_READY = 0
        RESOURCE_ACCESSED = 1
        DEFAULT = ITEM_READY

    name = djmodels.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class SourceAttributeName(models.Name):

    pass


class SourceAttribute(models.Attribute):

    class Meta:

        ordering = ('name__name',)
        unique_together = ('source', 'name',)

    source = djmodels.ForeignKey(Source,
                         related_name='attributes')
    name = djmodels.ForeignKey(SourceAttributeName)

    def __unicode__(self):
        return '%s: %s' % (self.name, self.value,)


class SourceEventName(models.Name):

    pass


class SourceEvent(models.Event):

    source = djmodels.ForeignKey(Source,
                         related_name='events')
    name = djmodels.ForeignKey(SourceEventName)


class SourceNotification(models.Notification):

    event = djmodels.ForeignKey(SourceEvent,
                         related_name='notifications')


class Owner(models.User):

    class Meta:

        unique_together = ('source', 'source_owner_id',)

    source = djmodels.ForeignKey(Source)
    source_owner_id = djmodels.CharField(max_length=255)

    def __unicode__(self):
        return '%s@%s' % (self.source_owner_id, self.source.name,)


class FileType(models.Model):

    class Meta:

        ordering = ('name',)

    name = djmodels.CharField(max_length=128)
    mime_types = models.CsvField(max_length=128)
    extensions = models.CsvField(max_length=128)

    def __unicode__(self):
        return self.name


class FileSpecification(models.Model, models.Attributable):

    class Meta:

        unique_together = ('owner', 'name',),

    owner = djmodels.ForeignKey(Owner,
                         blank=True,
                         null=True)
    parent = djmodels.ForeignKey('FileSpecification',
                         related_name='children',
                         blank=True,
                         null=True)
    name = djmodels.CharField(max_length=128)
    type = djmodels.ForeignKey(FileType)

    def __unicode__(self):
        return self.name


class FileSpecificationAttributeName(models.Name):

    pass


class FileSpecificationAttribute(models.Attribute):

    class Meta:

        ordering = ('name__name',)
        unique_together = ('filespecification', 'name',)

    filespecification = djmodels.ForeignKey(FileSpecification,
                                          related_name='attributes')
    name = djmodels.ForeignKey(FileSpecificationAttributeName)


class Item(models.Model):

    class Meta:

        unique_together = ('owner', 'source_item_id',)

    owner = djmodels.ForeignKey(Owner)
    source_item_id = djmodels.CharField(max_length=255)
    item_type = djmodels.SmallIntegerField(choices=ItemTypes,
                         default=0)
    meta_type = djmodels.SmallIntegerField(choices=settings('META_TYPES',
                                                          ((0, 'Track'),)),
                         default=0)
    parents = djmodels.ManyToManyField('self',
                         symmetrical=False,
                         related_name='children',
                         blank=True, null=True)
    # resources = models.ManyToManyField('content.Resource',
    #                      related_name='items')
    enabled = djmodels.BooleanField(default=True)

    def __unicode__(self):
        return '%s@%s (%s)' % (self.source_item_id, self.owner.source, self.owner)


class ResourceType(models.Model):

    class Meta:

        ordering = ('name',)

    name = djmodels.CharField(max_length=128)
    media_type = djmodels.SmallIntegerField(choices=MediaTypes,
                         default=MediaTypes.DEFAULT)
    limited = djmodels.BooleanField(default=True)
    streamable = djmodels.BooleanField(default=False)

    def __unicode__(self):
        return self.name


# class Resource(Model):

#     class Events(Choice):

#         CREATED  = 0
#         UPLOADED = 1
#         PROCESSED = 2
#         CENDORED = 70
#         REVOKED  = 80
#         READY    = 99


class Metadata(djmodels.Model):

    class Meta:

        abstract = True

    item = djmodels.OneToOneField(Item,
                         primary_key=True)


class MetadataLocalizable(Metadata, models.Localizable):

    class Meta:

        abstract = True


class MetadataLocalization(models.Localization):

    class Meta:

        abstract = True
