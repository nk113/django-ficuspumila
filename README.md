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

Provides fundamental core components including authentication, caching, api resources, proxies and so on. It's worth enough just only to employ them in your project.

#### cache

    > from ficuspumila.core import cache
    ...
    > @cache.cache(keyargs=[0, 1],
    >              breakson=lambda *args, **kwargs: kwargs.get('cachebreak'),
    >              timeout=60*60)
    > dif do_some_stuff(arg1, arg2, **kwargs):
    >     return arg1 + arg2
    ...
    > cache.get_or_set('key', lambda: 2 + 3)
    > cache.get('key')
    5

#### crypto

    > from ficuspumila.core import crypto
    > transcoder = crypto.Transcoder(algorithm='AES',
    ...                              key='f29c34dc6add7a1c7da53ad41b04974caa44d71ffb71c5d8ccedde7ed8a30fff',
    ...                              iv='98ef088fc3dd58a2077901b4d7b190a5',
    ...                              hex=True)
    > encrypted = transcoder.algorithm.encrypt('test text')
    > encrypted
    '967347ae0b937981f32a47d193ec41c7'
    > transcoder.algorithm.decrypt(encrypted)
    'test text'

#### proxies

    > from ficuspumila.core import proxy
    > Owner = proxy.Proxy(api_url='http://some.tastypie.api/',
    ...                   version='v1',
    ...                   namespace='core/content'
    ...                   resource_name='owner',
    ...                   auth=('dev', 'dev',))
    > owner = Owner.objects.all()[0]
    > owner.user.username
    u'dev'

### core.content

Consists of encoder and storage.

### core.product


### core.playready


### core.transaction


### api

Each core application has its API endpoint and resources. Ficuspumila is fully integrated with [django-tastypie](https://github.com/toastdriven/django-tastypie) to implement internal RPC and to provide external interface so you can easily allow users to access there resources.

Getting Started with Ficuspumila
================================