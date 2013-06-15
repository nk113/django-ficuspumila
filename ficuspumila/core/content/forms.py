# -*- encoding: utf-8 -*-
import logging

from django.utils.translation import ugettext as _

from ficuspumila.core import forms
from ficuspumila.core.content import models


logger = logging.getLogger(__name__)


class GenreModel(forms.ModelForm):

    class Meta:

        model = models.Genre


class SourceModel(forms.ModelForm):

    class Meta:

        model = models.Source


class SourceEventModel(forms.ModelForm):

    class Meta:

        model = models.SourceEvent


class OwnerModel(forms.ModelForm):

    class Meta:

        model = models.Owner


class FileTypeModel(forms.ModelForm):

    class Meta:

        model = models.Source


class FileSpecificationModel(forms.ModelForm):

    class Meta:

        model = models.FileSpecification


class ItemModel(forms.ModelForm):

    class Meta:

        model = models.Item
