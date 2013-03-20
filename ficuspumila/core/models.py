# -*- coding: utf-8 -*-
import inspect
import json
import logging
import time

from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.db import models
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
from urllib import urlencode

from .auth import SSOAuthenticator
from .crypto import Transcoder
from .exceptions import ModelException
from .utils import (
    generate_hmac_digest,
    get_default_language_code,
)


logger = logging.getLogger(__name__)
trans = Transcoder()


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


class CSVField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, basestring):
            try:
                return [element.strip() for element in value.split(',')]
            except:
                logger.exception(u'Failed to convert CSV field ' +
                                 u'to python: %s' % value)
                raise ModelException(_(u'Could not evaluate CSV field.'))
        else:
            return value

    def get_prep_value(self, value):
        try:
            return ', '.join(value)
        except:
            logger.exception(u'Failed to prep data for CSV field: ' +
                             u'%s' % value)
            raise ModelException(_(u'Invalid value detected for CSV field.'))


class JSONField(models.TextField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, basestring):
            if len(value) < 1:
                return None
            try:
                return json.loads(value)
            except:
                logger.exception(u'Failed to convert JSON field ' +
                                 u'to python: %s' % value)
                raise ModelException(_(u'Could not evaluate JSON field.'))
        else:
            return value

    def get_prep_value(self, value):
        try:
            return json.dumps(value)
        except:
            logger.exception(u'Failed to prep data for JSON field: ' +
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


class Subject(models.Model):

    class Meta:

        abstract = True

    class Attributes(Choice):

        NAME = 0
        DEFAULT = NAME

    attribute_model = None

    def __init__(self, *args, **kwargs):
        if self.attribute_model is None:
            self.attribute_model = getattr(import_module(self.__module__),
                                           '%sAttribute' % self.__class__.__name__)
        return super(Subject, self).__init__(*args, **kwargs)

    def getattr(self, name, default=None):
        try:
            return self.attributes.get(name=name).value
        except self.attribute_model.DoesNotExist:
            return default

    def setattr(self, name, value):
        try:
            attribute = self.attributes.get(name=name)
        except self.attribute_model.DoesNotExist:
            attribute = self.attribute_model(name=name, value=value)
            self.attributes.add(attribute)
        else:
            attribute.value = value
            attribute.save()

    def delattr(self, name):
        try:
            attribute = self.attributes.get(name=name)
        except self.attribute_model.DoesNotExist:
            raise KeyError(name)
        else:
            attribute.delete()


class Attribute(Model):

    class Meta:
        abstract = True
        ordering = ('name',)

    # name field must be specified as a choice field
    value = models.CharField(max_length=512)

    def __init__(self, *args, **kwargs):
        if logger_model is None:
            self.logger_model = getattr(import_module(self.__module__),
                                        self.__class__.__name__[:-9])
        return super(Attribute, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s: %s' % (self.get_name_display(),
                            self.value,)


class Localizable(models.Model):

    class Meta:

        abstract = True

    def localize(self, language_code=None):
        manager = getattr(self,
                          '%slocalization_set' % self.__class__.__name__.lower())
        if language_code:
            localizations = manager.filter(language_code=language_code.lower())
        if len(localizations) < 1:
            localizations = manager.filter(
                language_code=get_default_language_code())
        if len(localizations) < 1:
            return getattr(import_module(self.__module__),
                           '%sLocalization' % self.__class__.__name__)()
        return localizations[0]


class Localization(Model):

    class Meta:

        abstract = True

    language_code = models.CharField(max_length=2,
                         choices=settings.LANGUAGES,
                         blank=False,
                         null=False,
                         verbose_name=_(u'Language code'),
                         help_text=_(u'Language code'))


class Logger(models.Model):

    class Meta:

        abstract = True

    class Events(Choice):

        DEFAULT = 0

    auto_initial_event = True

    def __init__(self, *args, **kwargs):
        if getattr(self, 'event_model', None) is None:
            self.event_model = getattr(import_module(self.__module__),
                                       '%sEvent' % self.__class__.__name__)
        return super(Logger, self).__init__(*args, **kwargs)

    @property
    def latest(self):
        try:
            return self.events.all()[0]
        except:
            return None

    def track(self, event, **kwargs):
        self.events.create(event=event, **kwargs)

    def save(self, *args, **kwargs):
        super(Logger, self).save(*args, **kwargs)
        if self.event_model and self.auto_initial_event and self.latest is None:
            self.track(self.Events.DEFAULT)


class Event(Model):

    class Meta:

        abstract = True

    # event field must be specified as a choice field
    message = JSONField(blank=True,
                         null=False,
                         verbose_name=_(u'Message'))

    def __init__(self, *args, **kwargs):
        if getattr(self, 'logger_model', None) is None:
            self.logger_model = getattr(import_module(self.__module__),
                                        self.__class__.__name__[:-5])
        return super(Event, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s: %s' % (self.ctime,
                           self.get_event_display(),)

    def save(self, *args, **kwargs):
        if not self.id:
            try:
                self.id = self.__class__.objects.all()[0].id -1
            except:
                self.id = -1
        return super(Event, self).save(*args, **kwargs)


class Stateful(Logger):

    class Meta:

        abstract = True

    @property
    def state(self):

        return self.latest


class Notifier(Logger):

    class Meta:

        abstract = True

    auto_initial_event = False

    hmac_key = models.CharField(max_length=64,
                         default=generate_hmac_digest,
                         verbose_name=_(u'HMAC key'))
    notification_url = models.CharField(max_length=255,
                         blank=True,
                         null=True,
                         verbose_name=_(u'Notification URL'))

    def __init__(self, *args, **kwargs):
        if getattr(self, 'notification_model', None) is None:
            self.notification_model = getattr(import_module(self.__module__),
                                              '%sNotification' % self.__class__.__name__)
        return super(Notifier, self).__init__(*args, **kwargs)

    def track(self, event, **kwargs):
        event = super(Notifier, self).track(event, **kwargs)
        if self.notification_url and len(self.notification_url):
            from core.common.tasks import notify
            notify.delay(self, event, self.notification_model)
        return event


class Notification(Model):

    class Meta:

        abstract = True

    # foreign key to the event must be specified

    url = models.CharField(max_length=255,
                         blank=True,
                         null=True,
                         verbose_name=_(u'Notification URL'))
    status_code = models.IntegerField(default=200,
                         verbose_name=_(u'HTTP status code'))
    content = models.TextField(blank=True,
                         null=False,
                         verbose_name=_(u'Content of the response'))

    def __unicode__(self):
        return '%s: Event（%s）' % (self.ctime, self.event,)


class User(Model):

    class Meta:

        abstract = True

    user = models.OneToOneField(AuthUser,
                         primary_key=True,
                         verbose_name=_(u'Django auth user'))


class Service(User, Notifier, Subject):

    class Meta:

        abstract = True

    token_key = models.CharField(max_length=255,
                         default=trans.algorithm.generate_key,
                         verbose_name=_(u'Key for the SSO auth token'))
    token_iv = models.CharField(max_length=255,
                         default=trans.algorithm.generate_iv,
                         verbose_name=_(u'IV for the SSO auth token'))

    def generate_token(self, data={}):
        try:
            return Transcoder(
                       key=self.token_key,
                       iv=self.token_iv).algorithm.encrypt(
                           json.dumps((
                               time.time() + settings.TOKEN_TIMEOUT,
                               data,)))
        except:
            return None

    def update_token(self, token):
        try:
            return self.generate_token(json.dumps(
                       self.decrypt_token(token)[1]))
        except:
            return None

    def decrypt_token(self, token):
        try:
            return json.loads(Transcoder(
                       key=self.token_key,
                       iv=self.token_iv).algorithm.decrypt(token))
        except:
            return None

    def generate_sso_params(self, data={}):
        try:
            return urlencode({self.__class__.name__.lower(): self.user.id,
                              SSOAuthenticator.TOKEN_PARAM: self.generate_token(data),})
        except:
            return None
