# -*- coding: utf-8 -*-
import gc
import inspect
import json
import logging

from django.contrib.auth.models import User as AuthUser
from django.db import models
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from ficuspumila.settings import (
    get as settings_get,
    ficuspumila as settings,
)
from .auth.sso import Authenticator
from .crypto import Transcoder
from .exceptions import ModelException
from .utils import (
    generate_hmac_digest,
    get_default_language_code,
)


logger = logging.getLogger(__name__)
transcoder = Transcoder()


def iterator(queryset, chunksize=1000, reverse=False):
    """
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.
 
    Note that the implementation of the iterator does not support ordered query sets.
    """
    ordering = '-' if reverse else ''
    queryset = queryset.order_by(ordering + 'pk')
    last_pk = None
    new_items = True
    while new_items:
        new_items = False
        chunk = queryset
        if last_pk is not None:
            func = 'lt' if reverse else 'gt'
            chunk = chunk.filter(**{'pk__' + func: last_pk})
        chunk = chunk[:chunksize]
        row = None
        for row in chunk:
            yield row
        if row is not None:
            last_pk = row.pk
            new_items = True


class Choice(object):

    class __metaclass__(type):

        def __init__(self, *args, **kwargs):
            self._data = []
            for name, value in inspect.getmembers(self):
                if not name.startswith('_') and not inspect.ismethod(value):
                    if isinstance(value, tuple) and len(value) > 1:
                        data = value
                    else:
                        pieces = [x.capitalize() for x in name.split('_')]
                        data = (value, ' '.join(pieces))
                    self._data.append(data)
                    setattr(self, name, data[0])

            self._hash = dict(self._data)

        def __iter__(self):
            for value, data in self._data:
                yield (value, data)

    @classmethod
    def get_value(self, key):
        return self._hash[key]


class CsvField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, basestring):
            splited = value.split(',')
            if len(splited) == 1 and len(splited[0]) < 1:
                return []
            try:
                return [element.strip() for element in splited]
            except:
                logger.exception(u'failed to convert CSV field '
                                 u'to python: %s' % value)
                raise ModelException(_(u'Could not evaluate CSV field.'))
        else:
            return value

    def get_prep_value(self, value):
        try:
            if len(value) < 1:
                return ''
            return ', '.join(value)
        except:
            logger.exception(u'failed to prep data for CSV field: '
                             u'%s' % value)
            raise ModelException(_(u'Invalid value detected for CSV field.'))


class JsonField(models.TextField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, basestring):
            if len(value) < 1:
                return {}
            try:
                return json.loads(value)
            except:
                logger.exception(u'failed to convert JSON field '
                                 u'to python: %s' % value)
                raise ModelException(_(u'Could not evaluate JSON field.'))
        else:
            return value

    def get_prep_value(self, value):
        try:
            if len(value.keys()) < 1:
                return ''
            return json.dumps(value)
        except:
            logger.exception(u'failed to prep data for JSON field: '
                             u'%s' % value)
            raise ModelException(_(u'Invalid value detected for JSON field.'))


class Model(models.Model):

    class Meta:

        abstract = True

    objects = import_module('settings.database.managers').Manager()

    ctime = models.DateTimeField(auto_now_add=True)
    utime = models.DateTimeField(auto_now=True)

    def __iter__(self):
        for field in self._meta.get_all_field_names():
            yield(field, getattr(self, field))

    def __getitem__(self, field):
        if field in self._meta.get_all_field_names():
            return getattr(self, field)
        return super(Model, self).__getaitem__(field)

    def __setitem__(self, field):
        if field in self._meta.get_all_field_names():
            return setattr(self, field, value)
        return super(Model, self).__setitem__(field, value)


class Name(Model):

    class Meta:

        abstract = True
        ordering = ('name',)

    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class Attributable(models.Model):

    class Meta:

        abstract = True


class Attribute(Model):

    class Meta:
        abstract = True
        ordering = ('name__name',)

    # name field must be specified as a foreign key to the Name model
    # related name to the attributable must be "attributes"
    value = models.CharField(max_length=512,
                         blank=False,
                         null=False)

    def __unicode__(self):
        return u'%s: %s' % (self.name.name,
                            self.value,)


class Logger(Attributable):

    class Meta:

        abstract = True


class Event(Model):

    class Meta:

        abstract = True
        ordering = ('-id',)

    # name field must be specified as a foreign key to the Name model
    # related name to the logger must be "events"
    message = JsonField(blank=True,
                         null=False,
                         verbose_name=_(u'Message'))

    def __unicode__(self):
        return u'%s: %s' % (self.name.name,
                            self.utime,)


class Stateful(Logger):

    class Meta:

        abstract = True


class Notifier(Logger):

    class Meta:

        abstract = True

    hmac_key = models.CharField(max_length=64,
                         default=generate_hmac_digest)
    notification_urls = CsvField(max_length=1024,
                                 help_text=_('Urls can be specified as comma separated value.'))


class Notification(Model):

    class Meta:

        abstract = True

    # foreign key to the event must be specified
    url = models.CharField(max_length=255,
                         blank=True,
                         null=False)
    status_code = models.IntegerField(default=200)
    content = models.TextField(blank=True,
                         null=False)

    def __unicode__(self):
        return '%s: Event（%s）' % (self.ctime, self.event,)


class Localizable(Model):

    class Meta:

        abstract = True


class Localization(Model):

    class Meta:

        abstract = True

    language_code = models.CharField(max_length=2,
                         choices=settings_get('LANGUAGES'),
                         blank=False,
                         null=False)


class User(Model):

    class Meta:

        abstract = True

    user = models.OneToOneField(AuthUser,
                         primary_key=True)


class Service(User, Notifier, Attributable):

    class Meta:

        abstract = True

    token_key = models.CharField(max_length=255,
                         default=transcoder.algorithm.generate_key)
    token_iv = models.CharField(max_length=255,
                         default=transcoder.algorithm.generate_iv)
