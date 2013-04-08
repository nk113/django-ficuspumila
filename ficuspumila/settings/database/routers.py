# -*- coding: utf-8 -*-
import logging
import random

from django.conf import settings


logger = logging.getLogger(__name__)


class Default(object):
    def db_for_read(self, model, **hints):
        destination = random.choice(settings.FICUSPUMILA['DATABASES_FOR_READ'])
        return destination

    def db_for_write(self, model, **hints):
        destination = random.choice(settings.FICUSPUMILA['DATABASES_FOR_WRITE'])
        return destination

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._state.db in settings.FICUSPUMILA['DATABASES_FOR_READ'] and
            obj2._state.db in settings.FICUSPUMILA['DATABASES_FOR_READ']):
            return True
        return None

    def allow_syncdb(self, db, model):
        if model._meta.app_label not in settings.FICUSPUMILA['SYNCDB_ALLOWED']:
            return True
        return False
