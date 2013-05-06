# -*- encoding: utf-8 -*-
import logging

from django.utils.translation import ugettext as _

from ficuspumila.core.forms import ModelForm
from .models import (
    Genre, Source, SourceEvent,
)


logger = logging.getLogger(__name__)


class GenreModelForm(ModelForm):

    class Meta:

        model = Genre


class SourceModelForm(ModelForm):

    class Meta:

        model = Source


class SourceEventModelForm(ModelForm):

    class Meta:

        model = SourceEvent


class FileTypeModelForm(ModelForm):

    class Meta:

        model = Source
