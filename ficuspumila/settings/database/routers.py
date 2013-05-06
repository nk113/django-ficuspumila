# -*- coding: utf-8 -*-
import logging
import random

from ficuspumila.settings import ficuspumila as settings


DEFAULT = ('default',)

logger = logging.getLogger(__name__)


class Default(object):
    def db_for_read(self, model, **hints):
        destination = random.choice(settings('DATABASES_FOR_READ', DEFAULT))
        return destination

    def db_for_write(self, model, **hints):
        destination = random.choice(settings('DATABASES_FOR_WRITE', DEFAULT))
        return destination

    def allow_relation(self, obj1, obj2, **hints):
        if (obj1._state.db in settings('DATABASES_FOR_READ', DEFAULT) and
            obj2._state.db in settings('DATABASES_FOR_READ', DEFAULT)):
            return True
        return None

    def allow_syncdb(self, db, model):
        if model._meta.app_label not in settings('SYNCDB_DISABLED'):
            return True
        return False

