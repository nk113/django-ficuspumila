# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.content.common.models import (\
    FileType, Source
)
from core.models import (
    Attribute, Choice, Localizable, Localization,
    Model, Subject, User
)


MODULE = __name__.split('.')[-3].lower()

logger = logging.getLogger(__name__)


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
