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

Ficuspumila is designed to process media files in destributed environment so you don't need to bother on scaling storategy as encoding or download sessions grow, just add boxes.

Requirements
============

Python Libraries
----------------

* python modules in `requirements.txt <requirements.txt>`_

External Services
-----------------

* Database like MySQL, mandatory
* AMQP service, `RabbitMQ <http://www.rabbitmq.com/>`_ is recommended, mandatory
* Setting up cache backend, such as memcache, would be strongly recommended
* `Red5 <http://www.red5.org/>`_ to stream FLV and MP3, optional
* `DSS <http://dss.macosforge.org/>`_ to stream MPEG-4 and 3GPP, optional
* `Microsoft PlayReady <http://www.microsoft.com/playready/>`_ to support DRM with PlayReady, optional

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

Each core application has its API endpoint and resources. Ficuspumila is fully integrated with `django-tastypie <https://github.com/toastdriven/django-tastypie>`_ to implement internal RPC and to provide external interfaces so you can easily allow users to access their resources.

Getting Started with Ficuspumila
================================
