# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.cache import cache
from core.models import (
    Attribute, Choice, CSVField, Event,
    Localizable, Localization,
    Logger, Model,
    Notification, Notifier,
    Service, Subject,
)


MODULE = __name__.split('.')[-3].lower()

logger = logging.getLogger(__name__)


class Genre(Localizable):

    class Meta:
        db_table = '%s_genre' % MODULE

    class Types(Choice):
        AUDIO   = 0
        VIDEO   = 1
        PICTURE = 2
        TEXT    = 3

    type = models.SmallIntegerField(default=Types.AUDIO,
                         choices=Types,
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
    name = models.SmallIntegerField(default=Source.Attributes.DEFAULT,
                         choices=Source.Attributes)


class SourceEvent(Event):

    class Meta:
        db_table = '%s_sourceevent' % MODULE

    source = models.ForeignKey(Source,
                         related_name='events',
                         verbose_name=_(u'Content source'))
    event = models.SmallIntegerField(default=Source.Events.DEFAULT,
                         choices=Source.Events)


class SourceNotification(Notification):

    class Meta:
        db_table = '%s_sourcenotification' % MODULE

    event = models.ForeignKey(SourceEvent,
                         related_name='notifications')


class FileType(Model):

    class Meta:
        db_table = '%s_filetype' % MODULE

    name = models.CharField(max_length=128)
    mime_type = CSVField(max_length=128)
    extension = models.CharField(max_length=5)

    def __unicode__(self):
        return self.name


class FileSpecification(Model, Subject):

    class Meta:
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
        TRIAL            = 17
        ITEM_FILE_TYPE   = 18
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
        ordering = ('name',)
        unique_together = ('spec', 'name',)

    spec = models.ForeignKey(FileSpecification)
    name = models.SmallIntegerField(default=FileSpecification.Attributes.DEFAULT,
                         choices=FileSpecification.Attributes)

    def __unicode__(self):
        return '%s: %s' % (self.name, self.value)
