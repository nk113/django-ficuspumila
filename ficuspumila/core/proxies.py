# -*- coding: utf-8 -*-
import json
import logging
import time

from django.core.exceptions import ObjectDoesNotExist
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from queryset_client import client
from rpc_proxy import proxies
from urllib import urlencode

from ficuspumila.settings import ficuspumila as settings
from ficuspumila.core import auth
from ficuspumila.core import crypto
from ficuspumila.core import exceptions
from ficuspumila.core import utils


logger = logging.getLogger(__name__)


class Attributable(proxies.Proxy):

    class Meta:

        abstract = True

    _attribute_names = ('attribute',)

    def __init_proxy__(self):
        super(Attributable, self).__init_proxy__()

        class_name = self.__class__.__name__
 
        for name in self._attribute_names:
            attribute_class_name = '%s%s' % (class_name, name.title(),)
            setattr(self, '%s' % name, getattr(import_module(self.__module__),
                                               attribute_class_name))
            # set the name proxy if the attribute has its name field as a foreign key
            try:
                setattr(self, '%s_name' % name, getattr(import_module(self.__module__),
                                                        '%sName' % attribute_class_name))
            except AttributeError, e:
                # could occur
                pass

    def get_attribute(self, name):
        kwargs = {
            self.model_name: proxies.get_pk(self),
            'name__name': name,
        }
        return self.attributes.get(**kwargs)

    def getattr(self, name, default=None):
        try:
            return utils.to_python(self.get_attribute(name).value)
        except (client.ObjectDoesNotExist,
                ObjectDoesNotExist) as e:
            return default

    def setattr(self, name, value):
        try:
            attribute = self.get_attribute(name)
        except (client.ObjectDoesNotExist,
                ObjectDoesNotExist) as e:
            try:
                attribute_name = self.attribute_name.objects.get(name=name)
            except (client.ObjectDoesNotExist,
                    ObjectDoesNotExist) as e:
                raise e
            kwargs = {
                self.model_name: self,
                'name': attribute_name,
                'value': utils.from_python(value),
            }
            attribute = self.attribute.objects.create(**kwargs)
            self.invalidate()
        else:
            attribute.value = utils.from_python(value)
            attribute.save()

    def delattr(self, name):
        try:
            attribute = self.get_attribute(name=name)
        except (client.ObjectDoesNotExist,
                ObjectDoesNotExist) as e:
            raise KeyError(name)
        else:
            attribute.delete()
            self.invalidate()


class Attribute(proxies.Proxy):

    class Meta:

        abstract = True

    @property
    def attribute(self):
        return self.name.name


class Logger(Attributable):

    class Meta:

        abstract = True

    _attribute_names = ('event',)

    @property
    def latest(self):
        try:
            return self.events.latest('id')
        except:
            return None

    def fire(self, name, message=''):
        try:
            event_name = self.event_name.objects.get(name=name)
        except (client.ObjectDoesNotExist,
                ObjectDoesNotExist) as e:
            raise e
        kwargs = {
            self.model_name: self,
            'name': event_name,
        }
        if message:
            kwargs['message'] = message
        event = self.event.objects.create(**kwargs)
        self.invalidate()
        return event


class Event(proxies.Proxy):

    class Meta:

        abstract = True

    @property
    def event(self):
        return self.name.name


class Stateful(Logger):

    class Meta:

        abstract = True

    @property
    def state(self):

        return self.latest


class Notifier(Logger):

    class Meta:

        abstract = True

    _attribute_names = ('event', 'notification',)


class Localizable(Attributable):

    class Meta:

        abstract = True

    _attribute_names = ('localization',)

    def localize(self, language_code=None):
        self.__init_proxy__()

        localizations = self.localization.objects.filter(**{
            self.__class__.__name__.lower(): self,
        })
        if len(localizations):
            localizations = localizations.filter(
                language_code=language_code if language_code else utils.get_default_language_code())
        if len(localizations) < 1:
            localizations = (self.localization(),)
        return localizations[0]


class Localization(proxies.Proxy):

    class Meta:

        abstract = True


class Service(Notifier):

    class Meta:

        abstract = True

    _attribute_names = ('attribute', 'event', 'notification',)

    def generate_token(self, data={}, format='json'):
        try:
            if format == 'json':
                data = json.dumps((
                           time.time() + settings('TOKEN_TIMEOUT'),
                           data,))
            else:
                raise exceptions.ProxyException(_('Format not supported: %s') % format)

            return crypto.Transcoder(
                       key=self.token_key,
                       iv=self.token_iv).algorithm.encrypt(data)

        except Exception, e:
            logger.exception('an error has occurred during generating token: %s' % e)
            raise e

    def decrypt_token(self, token, format='json', expiration=False):
        try:
            token = crypto.Transcoder(
                        key=self.token_key,
                        iv=self.token_iv).algorithm.decrypt(token)

            if format == 'json':
                token = json.loads(token)
            else:
                raise exceptions.ProxyException(_('Format not supported: %s') % format)

            if expiration:
                return token

            return token[1]

        except Exception, e:
            logger.exception('an error has occurred during decrypting token: %s' % e)
            raise e

    def update_token(self, token, format='json'):
        try:
            return self.generate_token(self.decrypt_token(token, format), format)
        except Exception, e:
            logger.exception('an error has occurred during updating token: %s' % e)
            raise e

    def generate_sso_params(self, data={}, format='json'):
        try:
            return urlencode({self.model_name: self.user.id,
                              auth.sso.Authenticator.TOKEN_PARAM: self.generate_token(data, format),})
        except Exception, e:
            logger.exception('an error has occurred during generating sso params: %s' % e)
            raise e
