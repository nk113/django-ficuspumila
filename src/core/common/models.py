# -*- coding: utf-8 -*-
import logging
import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import date as localdate
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from .crypto import Transcoder
from .cache import cache
from .utils import (
    generate_hmac_digest,
    get_default_language_code,
)


logger = logging.getLogger(__name__)


class Model(models.Model):

    class Meta:
        abstract = True

    objects = import_module('settings.database.managers').Manager()


class Localization(Model):

    class Meta:
        abstract = True

    language_code = models.CharField(max_length=2,
                         choices=settings.LANGUAGES,
                         blank=False,
                         null=False,
                         verbose_name=_(u'Language code'),
                         help_text=_(u'Language code'))


class Localizable(Model):

    class Meta:
        abstract = True

    def localize(self, language_code=None):
        manager = getattr(self, '%slocalization_set' % self.__name__.lower())
        if language_code:
            localizations = manager.filter(language_code=language_code.lower())
        if len(localizations) < 1:
            localizations = manager.filter(
                language_code=get_default_language_code())
        if len(localizations) < 1:
            return getattr(import_module(self.__module__),
                           '%sLocalization' % self.__name__)()
        return localizations[0]


class Logger(Model):

    class Meta:
        abstract = True

    event_model = None
    auto_initial_event = True

    def __init__(self, *args, **kwargs):
        if self.event_model is None:
            self.event_model = getattr(import_module(self.__module__),
                                       '%sEvent' % self.__name__)
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

    logger_model = None

    DEFAULT = 0
    EVENTS = (
        (DEFAULT, 'DEFAULT',)
    )

    id = models.IntegerField(primary_key=True,
                         verbose_name=_(u'Id of the object'))
    event = models.SmallIntegerField(default=DEFAULT,
                         choices=EVENTS,
                         verbose_name=_(u'Event'))
    message = models.TextField(blank=True,
                         null=False,
                         verbose_name=_(u'Message'))
    created_at = models.DateTimeField(auto_now_add=True,
                         verbose_name=_(u'Created at'))

    def __init__(self, *args, **kwargs):
        if logger_model is None:
            self.logger_model = getattr(import_module(self.__module__),
                                        self.__name__[:-5])
        return super(Event, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return '%s: %s' % (self.created_at,
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

    notification_model = None
    auto_initial_event = False

    hmac_key = models.CharField(max_length=64,
                         default=generate_hmac_digest,
                         verbose_name=_(u'HMAC key'))
    notification_url = models.CharField(max_length=255,
                         blank=True,
                         null=True,
                         verbose_name=_(u'Notification URL'))

    def __init__(self, *args, **kwargs):
        if notification_model is None:
            self.notification_model = getattr(import_module(self.__module__),
                                              '%sNotifier' % self.__name__)
        return super(EventNotifier, self).__init__(*args, **kwargs)

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
    created_at = models.DateTimeField(auto_now_add=True,
                         verbose_name=_(u'Created at'))

    def __unicode__(self):
        return '%s: Event（%s）' % (self.created_at, self.event,)


class Service(Notifier):

    class Meta:
        abstract = True

    user = models.OneToOneField(User,
                         verbose_name=_(u'Django auth user'))
    auth_token_key = models.CharField(max_length=64,
                         verbose_name=_(u'Key for the auth token'))
    auth_token_iv = models.CharField(max_length=64,
                         verbose_name=_(u'IV for the auth token'))

    def save(self):
        trans = Transcoder()
        if not self.auth_token_key:
            self.auth_token_key = trans.algorithm.generate_key()
        if not self.auth_token_iv:
            self.auth_token_iv = trans.algorithm.generate_iv()
        super(Service, self).save()


class Country(Model):

    class Meta:
        verbose_name = _(u'Country')
        verbose_name_plural = _(u'Countries')

    name = models.CharField(max_length=80,
                         verbose_name=_(u'Name'))
    name_caps = models.CharField(max_length=80,
                         verbose_name=_(u'Name with capitals'))
    alpha2 = models.CharField(max_length=2,
                         unique=True,
                         verbose_name=_(u'ISO 3166-1 alpha-2 code'))
    alpha3 = models.CharField(max_length=3,
                         unique=True,
                         verbose_name=_(u'ISO 3166-1 alpha-3 code'))
    numeric = models.IntegerField(max_length=3,
                         unique=True,
                         verbose_name=_(u'ISO 3166-1 numeric code'))

    def __unicode__(self):
        return '(%s): %s' % (self.alpha2, self.name)

    @staticmethod
    @cache(keyarg='ip')
    def get_by_ip(**kwargs):
        ip = kwargs.get('ip', None)

        if not ip:
            return None

        result = requests.get(settings.IPINFODB_API_URL,
                              params={'key': settings.IPINFODB_API_KEY,
                                      'ip': ip,
                                      'format': 'json'})

        logger.debug('get_by_ip: %s: %s' % (ip, result.text,))

        try:
            return Country.objects.get(alpha2=result.json()['countryCode'])
        except:
            return None


class Currency(Model):

    class Meta:
        verbose_name = _(u'Currency')
        verbose_name_plural = _(u'Currencies')

    name = models.CharField(max_length=80,
                         verbose_name=_(u'Name'))
    code = models.CharField(max_length=3,
                         unique=True,
                         verbose_name=_(u'ISO 4217 code'))
    decimal_place = models.SmallIntegerField(default=0,
                         verbose_name=_(u'Decimal place'))
    price_format = models.CharField(max_length=16,
                         blank=True,
                         null=True,
                         verbose_name=_(u'Price format'))

    def __unicode__(self):
        return '(%s): %s' % (self.code, self.name)

    def get_formated_price(self, price, code=False):
        if self.price_format:
            return (self.price_format % price +
                    ' (%s)' % self.code if code else '')

        if self.decimal_place == 0:
            format = '%i' + (' %s' % self.code) 
        else:
            format = '%' + ('.%if %s' % (self.decimal_place, self.code))

        return format % price
