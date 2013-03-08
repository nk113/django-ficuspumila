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


# class FileType(Model):

#     class Meta:
#         db_table = '%s_filetype' % MODULE

#     name = models.CharField(max_length=128)
#     mime_type = CSVField(max_length=128)
#     extension = models.CharField(max_length=5)

#     def __unicode__(self):
#         return self.name


# class FileSpecification(Model, Subject):

#     class Meta:
#         unique_together = ('source', 'name',),

#     source = models.ForeignKey(Source,
#                          blank=True,
#                          null=True)
#     owner = models.ForeignKey('core.content.api.models.Owner',
#                          blank=True,
#                          null=True)
#     type = models.ForeignKey(FileType)
#     name = models.CharField(max_length=128)

#     def __unicode__(self):
#         return '%s: %s' % (self.source, self.name,)
