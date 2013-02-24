# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.cache import cache
from core.models import (
    Attribute, Event,
    Localizable, Localization,
    Logger, Model,
    Notification, Notifier,
    Service, Subject, User,
)


MODULE = __name__.split('.')[-3].lower()

logger = logging.getLogger(__name__)


class Genre(Localizable):

    class Meta:
        db_table = '%s_genre' % MODULE

    GENRE_TYPES = (
        (0, 'AUDIO',),
        (1, 'VIDEO',),
        (2, 'PICTURE',),
        (3, 'TEXT',),
    )

    type = models.SmallIntegerField(choices=GENRE_TYPES,
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

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class SourceAttribute(Attribute):

    class Meta:
        db_table = '%s_sourceattribute' % MODULE

    DEFAULT = 0
    ATTRIBUTES = (
        (DEFAULT, 'DELETE_FROM_RESOURCE',)
    )

    source = models.ForeignKey(Source,
                               verbose_name=_(u'Content source'))


class SourceEvent(Event):

    class Meta:
        db_table = '%s_sourceevent' % MODULE

    ITEM_READY = 0
    RESOURCE_ACCESSED = 1
    DEFAULT = ITEM_READY
    EVENTS = (
        (DEFAULT, 'ITEM_READY',),
        (RESOURCE_ACCESSED, 'RESOURCE_ACCESSED',),
    )

    source = models.ForeignKey(Source,
                               verbose_name=_(u'Content source'))


class SourceNotification(Notification):

    class Meta:
        db_table = '%s_sourcenotification' % MODULE

    event = models.ForeignKey(SourceEvent)


class Owner(User):

    class Meta:
        db_table = '%s_owner' % MODULE
        unique_together = ('source', 'source_owner_id',)

    source = models.ForeignKey(Source)
    source_owner_id = models.CharField(max_length=255)

    def __unicode__(self):
        return '%s@%s' % (self.source_owner_id, self.source.name,)


# class Item(Model):

#     class Meta:
#         unique_together = ('owner', 'source_item_id',)

#     CATEGORIES = (
#         (0, 'DIGITAL',),
#         (1, 'PHYSICAL',),
#         (2, 'MEMBERSHIP',),
#     )

#     # types of metadata
#     TYPES = (
#         (0, 'TRACK',),
#         (1, 'ALBUM',),
#         (2, 'COLLECTION',),
#     )

#     owner = models.ForeignKey(Owner)
#     source_item_id = models.CharField(max_length=255)
#     category = models.SmallIntegerField(default=0,
#                          choices=CATEGORIES)
#     type = models.SmallIntegerField(default=0,
#                          choices=TYPES)
#     children = models.ManyToManyField('self',
#                          symmetrical=False,
#                          related_name='parents')
#     resources = models.ManyToManyField('content.Resource',
#                          related_name='items')
#     enabled = models.BooleanField(default=True)

#     @property
#     def metadata(self):
#         return getattr(self, self.get_type_display().replace('_', '').lower())
