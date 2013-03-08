# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.content.common.models import Source
from core.models import (
    Choice, Localizable, Localization,
    Model, User
)


MODULE = __name__.split('.')[-3].lower()

logger = logging.getLogger(__name__)


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


# class Metadata(Localizable):

#     class Meta:
#         abstract = True

#     @property
#     def title(self):
#         return self.localize().title

#     @property
#     def description(self):
#         return self.localize().description


# class MetadataLocalization(Localization):

#     class Meta:
#         abstract = True

#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True, null=False)

#     def __unicode__(self):
#         return '（%s）: %s' % (self.language, self.title,)
