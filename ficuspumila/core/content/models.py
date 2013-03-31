# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from ficuspumila.core.models import (
    Attribute, Choice, CSVField, Event,
    Localizable, Localization,
    Logger, Model, Notification, Notifier,
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

    class Attributes(Choice):

        DELETE_FROM_RESOURCE_ON_ITEM_READY = 0
        DEFAULT = DELETE_FROM_RESOURCE_ON_ITEM_READY

    class Events(Choice):

        ITEM_READY = 0
        RESOURCE_ACCESSED = 1
        DEFAULT = ITEM_READY

    def __init__(self, *args, **kwargs):
        if getattr(self, 'notification_model', None) is None:
            models = import_module('core.content.models')
            self.notification_model = getattr(models,
                                              'SourceNotification')
            self.event_model = getattr(models,
                                       'SourceEvent')
        return super(Notifier, self).__init__(*args, **kwargs)

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class SourceAttribute(Attribute):

    class Meta:
        db_table = '%s_sourceattribute' % MODULE
        unique_together = ('source', 'name',)

    source = models.ForeignKey(Source,
                         related_name='attributes',
                         verbose_name=_(u'Content source'))
    name = models.SmallIntegerField(choices=Source.Attributes,
                         default=Source.Attributes.DEFAULT)


class SourceEvent(Event):

    class Meta:

        db_table = '%s_sourceevent' % MODULE

    source = models.ForeignKey(Source,
                         related_name='events',
                         verbose_name=_(u'Content source'))
    event = models.SmallIntegerField(choices=Source.Events,
                         default=Source.Events.DEFAULT)


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
        unique_together = ('source', 'name',),

    class Attributes(Choice):

        WIDTH            = 0
        HEIGHT           = 1
        CANVAS_COLOR     = 2
        CLIP_POSITION    = 3
        LETTERBOX        = 4
        QUALITY          = 5
        FRAMERATE        = 6
        SAMPLERATE       = 7
        AUDIO_BITRATE    = 8
        AUDIO_CODEC      = 9
        AUDIO_PARAMS     = 10
        VIDEO_BITRATE    = 11
        VIDEO_CODEC      = 12
        VIDEO_PARAMS     = 13
        VIDEO_PRESET     = 14
        SEGMENT_DURATION = 15
        ASPECT           = 16
        ENCRYPTED        = 17
        TRIAL            = 18
        ITEM_FILE_TYPE   = 19
        DEFAULT          = WIDTH

    source = models.ForeignKey(Source,
                         blank=True,
                         null=True)
    name = models.CharField(max_length=128)
    type = models.ForeignKey(FileType)

    def __unicode__(self):
        return '%s: %s' % (self.source, self.name,)


class FileSpecificationAttribute(Attribute):

    class Meta:

        db_table = '%s_filespecificationatteibute' % MODULE
        ordering = ('name',)
        unique_together = ('spec', 'name',)

    spec = models.ForeignKey(FileSpecification)
    name = models.SmallIntegerField(choices=FileSpecification.Attributes,
                         default=FileSpecification.Attributes.DEFAULT)

    def __unicode__(self):
        return '%s: %s' % (self.name, self.value)


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
