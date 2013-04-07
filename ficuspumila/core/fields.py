# -*- coding: utf-8 -*-                                                
import logging

from django.conf import settings
from tastypie import fields


logger = logging.getLogger(__name__)


class ToManyField(fields.ToManyField):

    def __init__(self, to, attribute, related_name=None, default=fields.NOT_PROVIDED,
                 null=False, blank=False, readonly=False, full=False,
                 unique=False, help_text=None, use_in='all', full_list=True, full_detail=True, resource_name=None):
        super(ToManyField, self).__init__(
            to, attribute, related_name=related_name, default=default,
            null=null, blank=blank, readonly=readonly, full=full,
            unique=unique, help_text=help_text, use_in=use_in,
            full_list=full_list, full_detail=full_detail
        )

        self.resource_name = resource_name
