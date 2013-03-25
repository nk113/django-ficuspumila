...earnestly developping!

===========
django-ficuspumila
===========

.. image:: https://travis-ci.org/nk113/django-ficuspumila.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/nk113/django-ficuspumila

Ficuspumila (creeping fig or climbing fig, AKA pumila) is a species of flowering plant in the family Moraceae, native to East Asia... As the common name "creeping fig" indicates, the plant has a creeping / vining habit and is often used in gardens and landscapes... (`Wikipedia <http://en.wikipedia.org/wiki/Ficus_pumila>`_)

Ficuspumila is a django application suite which helps you to build comprehensive media contents management and distribution service. It covers whole media lifecycle from metadata ingestion, media file encoding and encryption to payment transacsion, authorized distribution and usage tracking. It would be great if Ficuspumila can empower your medias to grow and spread like the pumila creeps!

Structure
=========

Ficuspumila is designed to process media files in destributed environment so you don't need to bother on thinking scaling storategy as encoding or download sessions grow, just add boxes.

Requirements
============

Python Libraries
----------------

* python modules in `requirements.txt <requirements.txt>`_

External Services
-----------------

* AMQP service, `RabbitMQ <http://www.rabbitmq.com/>`_ is recommended
* optional, `Red5 <http://www.red5.org/>`_ to stream FLV and MP3
* optional, `DSS <http://dss.macosforge.org/>`_ to stream MPEG-4 and 3GPP
* optional, `Microsoft PlayReady <http://www.microsoft.com/playready/>`_ to support DRM with PlayReady

Media Tools
-----------

* `FFmpeg <http://www.ffmpeg.org/>`_
* `SoX <http://sox.sourceforge.net/>`_
* `GPAC <http://gpac.wp.mines-telecom.fr/mp4box/>`_
* `m3u8-segmenter <https://github.com/johnf/m3u8-segmenter>`_

Accounts
--------

* `ipinfodb.com <http://ipinfodb.com/>`_ to translate some IP address into a country

Modules
=======

core
----

Provides fundamental core components including authentication, caching, api resources, proxies and so on. It's worth enough just only to employ them in your project.

**cache**

::

    >>> from ficuspumila.core import cache
    ...
    >>> @cache.cache(keyargs=[0, 1],
    >>>              breakson=lambda *args, **kwargs: kwargs.get('cachebreak'),
    >>>              timeout=60*60)
    >>> dif do_some_stuff(arg1, arg2, **kwargs):
    >>>     return arg1 + arg2
    ...
    >>> cache.get_or_set('key', lambda: 2 + 3)
    5
    >>> cache.get('key')
    5

**crypto**

::

    >>> from ficuspumila.core import crypto
    >>> transcoder = crypto.Transcoder()
    >>> print transcoder.algorithm
    AES
    >>> encrypted = transcoder.algorithm.encrypt('test text')
    >>> encrypted
    '8a514d9f4d907102ba9657cd1098fd04'
    >>> transcoder.algorithm.decrypt(encrypted)
    'test text'
    >>> transcoder.key
    'dfbaa4a01bc2b80458df045f4c973f390d516bbc564cee5d0baee807c2726137'
    >>> transcoder.iv
    '8a514d9f4d907102ba9657cd1098fd04'

**proxy**

::

    >>> from ficuspumila.core import proxy
    >>> Owner = proxy.Proxy(api_url='http://some.tastypie.api/',
    ...                     version='v1',
    ...                     namespace='core/content'
    ...                     resource_name='owner',
    ...                     auth=('dev', 'dev',))
    >>> owner = Owner.objects.all()[0]
    >>> owner.user.source.name
    u'dev'

core.content
------------

Consists of encoder and storage.

core.product
------------

core.playready
--------------

core.transaction
----------------

api
---

Each core application has its API endpoint and resources. Ficuspumila is fully integrated with `django-tastypie <https://github.com/toastdriven/django-tastypie>`_ to implement internal RPC and to provide external interface so you can easily allow users to access there resources.

Getting Started with Ficuspumila
================================
