# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist
from rpc_proxy import test
from queryset_client import client

from ficuspumila.core.exceptions import ProxyException
from ficuspumila.core.utils import parse_qs
from ficuspumila.settings import ficuspumila as settings


logger = logging.getLogger(__name__)


class GenreProxy(test.Proxy):

    def test_get(self):
        from ficuspumila.core.content.proxies import Genre

        g = Genre.objects.get(name='Pop')
        self.assertEqual(g.name, 'Pop')

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: Genre.objects.get(name='crazymonkey'))

        return g

    def test_localize(self):
        g = self.test_get()

        self.assertEqual(g.localize('ja').name, u'ポップ')
        self.assertEqual(g.localize('en').name, u'Pop')


class SourceProxy(test.Proxy):

    def test_get(self):
        from ficuspumila.core.content.proxies import Source

        s = Source.objects.get(user__username=settings('SUPERUSER_USERNAME'))
        self.assertEqual(s.user.username, settings('SUPERUSER_USERNAME'))
        self.assertEqual(s.name, settings('SUPERUSER_USERNAME'))

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: Source.objects.get(name='crazymonkey'))

        return s

    def test_get_csv_fields(self):
        s = self.test_get()

        self.assertEqual(type(s.notification_urls), list)

    def test_set_csv_fields(self):
        s = self.test_get()

        s.notification_urls.append('http://example.com')
        s.notification_urls.append('http://a.example.com')
        s.notification_urls.append('http://b.example.com')
        s.save()

        s = self.test_get()

        self.assertEqual(type(s.notification_urls), list)
        self.assertEqual(s.notification_urls[1], 'http://a.example.com')

    def test_getattr(self):
        s = self.test_get()
        self.assertEqual(s.getattr('DELETE_SOURCE_RESOURCE_ON_ITEM_READY'), None)
        return s

    def test_setattr(self):
        s = self.test_get()

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: s.setattr('SHITHEAD', 'blah'))

        s.setattr('DELETE_SOURCE_RESOURCE_ON_ITEM_READY', 'True')
        self.assertEqual(s.getattr('DELETE_SOURCE_RESOURCE_ON_ITEM_READY'), True)

        return s

    def test_delattr(self):
        s = self.test_setattr()

        s.delattr('DELETE_SOURCE_RESOURCE_ON_ITEM_READY')
        self.assertEqual(s.getattr('DELETE_SOURCE_RESOURCE_ON_ITEM_READY'),
                         None)
        self.assertRaises(KeyError, lambda: s.delattr('SHITHEAD'))

        return s

    def test_latest(self):
        s = self.test_get()

        s.fire('ITEM_READY', {'success': 1})
        self.assertEqual(s.latest.event, 'ITEM_READY')

        s.fire('ITEM_USED', {'source_item_id': 'ab3f8d'})
        self.assertEqual(s.latest.event, 'ITEM_USED')
        self.assertEqual(s.latest.message['source_item_id'], 'ab3f8d')

        return s, s.latest

    def test_fire(self):
        s, latest = self.test_latest()

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: s.fire('SHITHEAD', message='blah'))

        return s

    def test_generate_token(self):
        s = self.test_get()

        token = s.generate_token({'test': 'abc'})
        self.assertEqual(isinstance(token, str), True)

        self.assertRaises(ProxyException, lambda: s.generate_token({'test': 'abc'}, format='xml'))

        return s, token

    def test_update_token(self):
        s, token = self.test_generate_token()

        updated = s.update_token(token)
        decrypted = s.decrypt_token(updated)
        self.assertEqual(s.decrypt_token(token, expiration=True)[0] < s.decrypt_token(updated), True)

        self.assertRaises(ProxyException, lambda: s.update_token(token, format='xml'))

    def test_decrypt_token(self):
        s, token = self.test_generate_token()

        self.assertEqual(s.decrypt_token(token)['test'], 'abc')

        self.assertRaises(ProxyException, lambda: s.decrypt_token(token, format='xml'))

    def test_generate_sso_params(self):
        s = self.test_get()

        params = parse_qs(s.generate_sso_params({'test': 'def'}))

        self.assertEqual('source' in params.keys(), True)
        self.assertEqual(int(params['source']), 1)
        self.assertEqual(s.decrypt_token(params['token'])['test'], 'def')


class OwnerProxy(test.Proxy):

    def test_get(self):
        from ficuspumila.core.content.proxies import Owner

        o = Owner.objects.get(user__username=settings('SUPERUSER_USERNAME'))
        self.assertEqual(o.user.username, settings('SUPERUSER_USERNAME'))
        self.assertEqual(o.source_owner_id, settings('SUPERUSER_USERNAME'))

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: Owner.objects.get(source_owner_id='crazymonkey'))

        return o


class FileSpecificationProxy(test.Proxy):

    def test_get(self):
        from ficuspumila.core.content.proxies import FileSpecification, Owner

        o = Owner.objects.get(user__username=settings('SUPERUSER_USERNAME'))
        fs = FileSpecification.objects.get(owner=o,
                                           name='SCREENSHOT')
        self.assertEqual(fs.name, 'SCREENSHOT')
        self.assertEqual(fs.owner.user.username, settings('SUPERUSER_USERNAME'))

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: FileSpecification.objects.get(name='crazymonkey'))

        return fs

    def test_getattr(self):
        fs = self.test_get()
        self.assertEqual(fs.getattr('WIDTH'), '100')
        self.assertEqual(fs.getattr('HEIGHT'), '100')
        self.assertEqual(fs.getattr('LETTERBOX', True), True)
        self.assertEqual(fs.getattr('QUALITY', 75), 75)
        return fs

    def test_setattr(self):
        fs = self.test_get()

        self.assertRaises((client.ObjectDoesNotExist, ObjectDoesNotExist),
                          lambda: fs.setattr('SHITHEAD', 'blah'))

        fs.setattr('WIDTH', '120')
        self.assertEqual(fs.getattr('WIDTH'), '120')

        return fs

    def test_delattr(self):
        fs = self.test_setattr()

        fs.delattr('WIDTH')
        self.assertEqual(fs.getattr('WIDTH'), None)
        self.assertRaises(KeyError, lambda: fs.delattr('SHITHEAD'))

        return fs
