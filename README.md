...earnestly developping!

===========
ficuspumila
===========

Ficuspumila (creeping fig or climbing fig, AKA pumila) is a species of flowering plant in the family Moraceae, native to East Asia... As the common name "creeping fig" indicates, the plant has a creeping / vining habit and is often used in gardens and landscapes... ([Wikipedia] [1])

  [1]: http://en.wikipedia.org/wiki/Ficus_pumila "Wikipedia"

Ficuspumila is a django application suite which helps you to build comprehensive media contents management and distribution service. It covers whole media lifecycle from metadata ingestion, media file encoding and encryption to payment transacsion, authorized distribution and usage tracking. It would be really great if Ficuspumika can empower your medias to grow and spread like the pumila creeps!

Structure
=========

Ficuspumila is designed to process media files in destributed environment. The more encoding or download session increase, the more encoder or donwload server will be required.

Requirements
============

Python Libraries
----------------

* python modules in [requirements.txt](src/requirements.txt "requirements.txt")

External Services
-----------------

* AMQP service, [RabbitMQ](http://www.rabbitmq.com/ "RabbitMQ") is recommended.

Media Tools
-----------

* [FFmpeg](http://www.ffmpeg.org/ "FFmpeg")
* [SoX](http://sox.sourceforge.net/ "SoX")
* [GPAC](http://gpac.wp.mines-telecom.fr/mp4box/ "GPAC")
* [m3u8-segmenter](https://github.com/johnf/m3u8-segmenter "m3u8-segmenter")

Accounts
--------

* [ipinfodb.com](http://ipinfodb.com/ "ipinfodb.com")

Modules
=======

core
----

core.content
------------

core.product
------------

core.playready
--------------

core.transaction
----------------

api
---

Getting Started with Ficuspumila
================================