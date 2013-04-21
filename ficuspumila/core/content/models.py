# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from ficuspumila.core.models import (
    Attribute, Choice, CSVField, Event,
    Localizable, Localization,
    Logger, Model, Name, Notification, Notifier,
    Service, Subject, User,
)


MODULE = __name__.split('.')[-2].lower()

logger = logging.getLogger(__name__)


class Categories(Choice):

    AUDIO   = 0
    VIDEO   = 1
    PICTURE = 2
    TEXT    = 3
    DEFAULT = AUDIO


class Genre(Localizable):

    class Meta:

        db_table = '%s_genre' % MODULE

    type = models.SmallIntegerField(default=Categories.AUDIO,
                         choices=Categories,
                         verbose_name=_(u'Genre type'))

    def __unicode__(self):
        localization = self.localize()
        return '%s (%s): %s' % (self.get_type_display(),
                                localization.language_code,
                                localization.name,)


class GenreLocalization(Localization):

    class Meta:
        db_table = '%s_genrelocalization' % MODULE

    genre = models.ForeignKey(Genre)
    name = models.CharField(max_length=128,
                            verbose_name=_(u'Genre name'))

    def __unicode__(self):
        return '(%s): %s' % (self.language_code,
                             self.name,)


class Source(Service):

    class Meta:

        db_table = '%s_source' % MODULE

    class Events(Choice):

        ITEM_READY = 0
        RESOURCE_ACCESSED = 1
        DEFAULT = ITEM_READY

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class SourceAttributeName(Name):

    class Meta:
        db_table = '%s_sourceattributename' % MODULE


class SourceAttribute(Attribute):

    class Meta:
        db_table = '%s_sourceattribute' % MODULE
        ordering = ('name__name',)
        unique_together = ('source', 'name',)

    source = models.ForeignKey(Source,
                         related_name='attributes',
                         verbose_name=_(u'Content source'))
    name = models.ForeignKey(SourceAttributeName)


class SourceEventName(Name):

    class Meta:
        db_table = '%s_sourceeventname' % MODULE


class SourceEvent(Event):

    class Meta:

        db_table = '%s_sourceevent' % MODULE

    source = models.ForeignKey(Source,
                         related_name='events',
                         verbose_name=_(u'Content source'))
    name = models.ForeignKey(SourceEventName)


class SourceNotification(Notification):

    class Meta:

        db_table = '%s_sourcenotification' % MODULE

    event = models.ForeignKey(SourceEvent,
                         related_name='notifications')


class Owner(User):

    class Meta:

        db_table = '%s_owner' % MODULE
        unique_together = ('source', 'source_owner_id',)

    source = models.ForeignKey(Source)
    source_owner_id = models.CharField(max_length=255)

    def __unicode__(self):
        return '%s@%s' % (self.source_owner_id, self.source.name,)


class FileType(Model):

    class Meta:

        db_table = '%s_filetype' % MODULE
        ordering = ('name',)

    name = models.CharField(max_length=128)
    mime = CSVField(max_length=128)
    extension = models.CharField(max_length=5)

    def __unicode__(self):
        return self.name


class FileSpecification(Model, Subject):

    class Meta:

        db_table = '%s_filespecification' % MODULE
        unique_together = ('owner', 'name',),

    owner = models.ForeignKey(Owner,
                         blank=True,
                         null=True)
    name = models.CharField(max_length=128)
    type = models.ForeignKey(FileType)

    def __unicode__(self):
        return '%s: %s' % (self.source, self.name,)


class FileSpecificationAttributeName(Name):

    class Meta:
        db_table = '%s_filespecificationatteibutename' % MODULE


class FileSpecificationAttribute(Attribute):

    class Meta:

        db_table = '%s_filespecificationatteibute' % MODULE
        ordering = ('name__name',)
        unique_together = ('spec', 'name',)

    spec = models.ForeignKey(FileSpecification)
    name = models.ForeignKey(FileSpecificationAttributeName)


# class Item(Model):

#     class Meta:

#         db_table = '%s_genre' % MODULE
#         unique_together = ('owner', 'source_item_id',)

#     class Types(Choice):

#        TRACK      = 0
#        ALBUM      = 1
#        COLLECTION = 2

#     class Categories(Choice):

#        DIGITAL    = 0
#        PHYSICAL   = 1
#        MEMBERSHIP = 2

#     owner = models.ForeignKey(Owner)
#     source_item_id = models.CharField(max_length=255)
#     category = models.SmallIntegerField(default=0,
#                          choices=Categories)
#     type = models.SmallIntegerField(default=0,
#                          choices=Types)
#     children = models.ManyToManyField('self',
#                          symmetrical=False,
#                          related_name='parents')
#     resources = models.ManyToManyField('content.Resource',
#                          related_name='items')
#     enabled = models.BooleanField(default=True)

#     def __unicode__(self):
#         title = self.metadata.localize().title
#         return '%s@%s' % (self.metadata.self.source_owner_id,)

#     @property
#     def metadata(self):
#         return getattr(self,
#                        'metadata%s' % self.get_type_display().replace(' ',
#                                                                       '').lower(),
#                        None)


class ResourceType(Model):

    class Meta:

        db_table = '%s_resourcetype' % MODULE
        ordering = ('name',)

    name = models.CharField(max_length=128)
    category = models.SmallIntegerField(choices=Categories,
                                        default=Categories.DEFAULT)
    limited = models.BooleanField(default=True)
    streamable = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


# class Resource(Model):

#     class Categories:

#         AUDIO    = 0
#         VIDEO    = 1
#         IMAGE    = 2
#         DOCUMENT = 3


# class Metadata(Localizable):

#     class Meta:

#         abstract = True

#     @property
#     def title(self):
#         return self.localize().title

#     @property
#     def description(self):
#         return self.localize().description

#     item  = models.OneToOneField(Item,
#                          primary_key=True,
#                          verbose_name=_(u'Item'))


# class MetadataLocalization(Localization):

#     class Meta:

#         abstract = True

#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True, null=False)

#     def __unicode__(self):
#         return '（%s）: %s' % (self.language, self.title,)


# class MetadataTrack(Metadata):

#     pass


# class MetadataTrackLocalization(MetadataLocalization):

#     pass


# class MetadataAlbum(Metadata):

#     pass


# class MetadataAlbumLocalization(MetadataLocalization):

#     pass


# class MetadataCollection(Metadata):

#     pass


# class MetadataCoolectionLocalization(MetadataLocalization):

#     pass
