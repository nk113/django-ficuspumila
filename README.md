...earnestly developping!

===========
Ficuspumila
===========

Ficuspumila (creeping fig or climbing fig, AKA pumila) is a species of flowering plant in the family Moraceae, native to East Asia... As the common name "creeping fig" indicates, the plant has a creeping / vining habit and is often used in gardens and landscapes... ([Wikipedia] [1])

  [1]: http://en.wikipedia.org/wiki/Ficus_pumila "Wikipedia"

Ficuspumila is a django application suite which helps you to build comprehensive media contents management and distribution service. It covers whole media lifecycle from metadata ingestion, media file encoding and encryption to payment transacsion, authorized distribution and usage tracking. It would be great if Ficuspumila can empower your medias to grow and spread like the pumila creeps!

Structure
---------

Ficuspumila is designed to process media files in destributed environment so you don't need to bother on thinking scaling storategy as encoding or download sessions grow, just add boxes.

Requirements
------------

### Python Libraries

* python modules in [requirements.txt](src/requirements.txt "requirements.txt")

### External Services

* AMQP service, [RabbitMQ](http://www.rabbitmq.com/ "RabbitMQ") is recommended

### Media Tools

* [FFmpeg](http://www.ffmpeg.org/ "FFmpeg")
* [SoX](http://sox.sourceforge.net/ "SoX")
* [GPAC](http://gpac.wp.mines-telecom.fr/mp4box/ "GPAC")
* [m3u8-segmenter](https://github.com/johnf/m3u8-segmenter "m3u8-segmenter")

### Accounts

* [ipinfodb.com](http://ipinfodb.com/ "ipinfodb.com")

Modules
-------

### core

Provides fundamental components including authentication, caching, api resources,  proxies and so on.

### core.content

Consists of encoder and storage.

### core.product


### core.playready


### core.transaction


### api

Each core application has its API endpoint and resources. Ficuspumila is fully integrated with [django-tastypie](https://github.com/toastdriven/django-tastypie) to implement internal RPC and to provide external interface so you can easily allow users to access there resources.

Getting Started with Ficuspumila
================================