# -*- encoding: utf-8 -*-
import logging

from django import forms
from django.utils.translation import ugettext as _

from .models import CsvField, JsonField


logger = logging.getLogger(__name__)


class ModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        if 'instance' in kwargs:
            initial = kwargs.setdefault('initial', {})
            instance = kwargs['instance']
            for field in instance._meta.fields:
                if field.__class__ in (CsvField, JsonField,):
                    initial[field.name] = field.get_prep_value(getattr(instance,
                                                                       field.name))
                    field.widget = forms.Textarea

        super(ModelForm, self).__init__(*args, **kwargs)
