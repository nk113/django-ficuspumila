# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from core.cache import cache
from core.models import (
    Attribute, Choice, CSVField,
    Localizable, Localization,
    Logger, Model, Notifier,
    Service, Subject,
)


MODULE = __name__.split('.')[-3].lower()

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
            api_models = import_module('core.content.api.models')
            self.notification_model = getattr(api_models,
                                              'SourceNotification')
            self.event_model = getattr(api_models,
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


class FileType(Model):

    class Meta:

        db_table = '%s_filetype' % MODULE
        ordering = ('name',)

    name = models.CharField(max_length=128)
    mime = CSVField(max_length=128)
    extension = models.CharField(max_length=5)

    def __unicode__(self):
        return self.name


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