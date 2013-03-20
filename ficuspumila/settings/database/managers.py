# -*- coding: utf-8 -*-                                                                             

from django.db import models


class Manager(models.Manager):
    def get_query_set(self):
        return super(Manager, self).get_query_set().using('default')


class EnabledManager(Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(EnabledManager, self).get_query_set().filter(enabled=True)
