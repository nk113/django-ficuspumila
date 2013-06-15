# -*- coding: utf-8 -*-
import logging

from datetime import date
from django.db import models as djmodels
from django.utils.translation import ugettext_lazy as _

from ficuspumila.core.content import models


logger = logging.getLogger(__name__)


class BasicLocalizable(models.MetadataLocalizable):

    class Meta:

        abstract = True

    genre = djmodels.ForeignKey(models.Genre, blank=True, null=True)
    release_date = djmodels.DateField(default=date.today)


class RecordingLocalizable(djmodels.Model):

    class Meta:

        abstract = True

    isrc = djmodels.CharField(max_length=20, blank=True, null=False)
    length = djmodels.IntegerField(default=0)
    trial_start_position = djmodels.IntegerField(default=0, blank=True, null=False)
    trial_duration = djmodels.IntegerField(default=45, blank=True, null=False)


class BasicLocalization(models.MetadataLocalization):

    class Meta:

        abstract = True

    title = djmodels.CharField(max_length=255, blank=True, null=False)
    description = djmodels.TextField(blank=True, null=False)

    def __unicode__(self):
        return '(%s): %s' % (self.language_code,
                             self.title,)


class MusicLocalization(djmodels.Model):

    class Meta:

        abstract = True

    artist = djmodels.CharField(max_length=255, blank=True, null=False)
    label = djmodels.CharField(max_length=255, blank=True, null=False)


class Track(BasicLocalizable, RecordingLocalizable):

    pass


class TrackLocalization(BasicLocalization, MusicLocalization):

    track = djmodels.ForeignKey(Track)


class Album(BasicLocalizable):

    pass


class AlbumLocalization(BasicLocalization, MusicLocalization):

    album = djmodels.ForeignKey(Album)


class Video(BasicLocalizable, RecordingLocalizable):

    pass


class VideoLocalization(BasicLocalization):

    video = djmodels.ForeignKey(Video)
