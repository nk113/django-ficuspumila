# -*- coding: utf-8 -*-
import logging

from django import forms

from ficuspumila.apps.example import models


logger = logging.getLogger(__name__)


class TrackModel(forms.ModelForm):

    class Meta:

        model = models.Track


class TrackLocalizationModel(forms.ModelForm):

    class Meta:

        model = models.TrackLocalization


class AlbumModel(forms.ModelForm):

    class Meta:

        model = models.Album


class AlbumLocalizationModel(forms.ModelForm):

    class Meta:

        model = models.AlbumLocalization


class VideoModel(forms.ModelForm):

    class Meta:

        model = models.Video


class VideoLocalizationModel(forms.ModelForm):

    class Meta:

        model = models.VideoLocalization
