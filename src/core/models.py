# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from .crypto import Transcoder
from .utils import (
    generate_hmac_digest,
    get_default_language_code,
)


logger = logging.getLogger(__name__)
trans = Transcoder()


class CSVField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, basestring):
            return value.split(',')
        return value

    def get_prep_value(self, value):
        if isinstance(value, list):
            return ','.join(value)
        return value


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


class Subject(Model):

    attribute_model = None

    def __init__(self, *args, **kwargs):
        if self.attribute_model is None:
            self.attribute_model = getattr(import_module(self.__module__),
                                           '%sAttribute' % self.__class__.__name__)
        return super(Attribute, self).__init__(*args, **kwargs)

    @property
    def attribute_set(self):
        return getattr(self, '%s_set' % self.attribute_model.__name__.lower())

    def set_attribute(self, name, value):
        return self.attribute_set.add(self.attirbute_model(name=name, value=value))

    def get_attribute(self, name, default=None):
        try:
            return self.attribute_set.get(name=name).value
        except self.attribute_model.MultipleObjectReturned, e:
            return self.attribute_set.all()[0]
        else:
            return default


class Attribute(Model):

    class Meta:
        abstract = True
        ordering = 'name'

    DEFAULT = 0
    ATTRIBUTES = (
        (DEFAULT, 'NAME',)
    )

    name = models.SmallIntegerField(default=DEFAULT,
                         choices=ATTRIBUTES)
    value = models.CharField(max_length=512)

    def __init__(self, *args, **kwargs):
        if logger_model is None:
            self.logger_model = getattr(import_module(self.__module__),
                                        self.__class__.__name__[:-9])
        return super(Attribute, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s: %s' % (self.get_name_display(),
                            self.value,)


class Localizable(Model):

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


class Logger(Model):

    class Meta:
        abstract = True

    auto_initial_event = True

    def __init__(self, *args, **kwargs):
        if getattr(self, 'event_model', None) is None:
            self.event_model = getattr(import_module(self.__module__),
                                       '%sEvent' % self.__class__.__name__)
        return super(Logger, self).__init__(*args, **kwargs)

    @property
    def latest(self):
        try:
            return self.event_set.all()[0]
        except:
            return None

    @property
    def event_set(self):
        return getattr(self, '%s_set' % self.event_model.__name__.lower())

    def track(self, event, **kwargs):
        event = self.event_model(event=event, **kwargs)
        self.event_set.add(event)
        return event

    def save(self, *args, **kwargs):
        super(Logger, self).save(*args, **kwargs)
        if self.event_model and self.auto_initial_event and not self.latest:
            self.track_event(self.event_model.DEFAULT_EVENT)


class Event(Model):

    class Meta:
        abstract = True

    DEFAULT = 0
    EVENTS = (
        (DEFAULT, 'DEFAULT',),
    )

    name = models.SmallIntegerField(default=DEFAULT,
                         choices=EVENTS)
    message = models.TextField(blank=True,
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
                self.id = self.__class__.objects.all()[0].id - 1
            except:
                self.id = -1
        return super(Event, self).save(*args, **kwargs)
        

class Stateful(Logger):

    class Meta:
        abstract = True

    @property
    def state(self):
        return self.latest_event


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


class Service(Notifier):

    class Meta:
        abstract = True

    user = models.OneToOneField(User,
                         primary_key=True,
                         verbose_name=_(u'Django auth user'))
    token_key = models.CharField(max_length=255,
                         default=trans.algorithm.generate_key,
                         verbose_name=_(u'Key for the SSO auth token'))
    token_iv = models.CharField(max_length=255,
                         default=trans.algorithm.generate_iv,
                         verbose_name=_(u'IV for the SSO auth token'))
