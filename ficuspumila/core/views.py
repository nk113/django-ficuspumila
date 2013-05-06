# -*- coding: utf-8 -*-
import json
import logging

from django.http import HttpResponse 
from django.views.decorators.csrf import csrf_exempt
from tastypie.http import HttpBadRequest, HttpMethodNotAllowed

from ficuspumila.settings import ficuspumila as settings

from .utils import generate_hmac_digest, get_raw_post_data


DEV_HMAC_KEY = 'a34ae9c337ac6f68933b76bdee3840f50b2fba79ec72b29bed9f5cb48b3660e0'

logger = logging.getLogger(__name__)


@csrf_exempt
def event_receiver(request):
    """
    This actually does nothing, called for testing purpose only
    """
    if request.method == 'POST':
        data = json.loads(get_raw_post_data(request))

        logger.debug(u'got event notification (%s)' % data)

        digest = generate_hmac_digest(settings('HMAC_KEY', DEV_HMAC_KEY),
                                      '%s%s' % (data['event'],
                                                data['ctime'],))

        logger.debug(u'hmac digest (%s)' % digest)

        if digest == data['hmac']:
            logger.debug(u'the notification has been processed normally.')

            return HttpResponse(u'OK')
        else:
            logger.exception(u'invalid notifcation detected.')

            return HttpBadRequest(u'Invalid notification detected')

    return HttpMethodNotAllowed()
