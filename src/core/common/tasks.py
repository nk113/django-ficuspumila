# -*- coding: utf-8 -*-
import json
import logging
import os
import requests

from celery.decorators import task
from django.conf import settings

from .utils import (
    generate_hmac_digest,
)


RETRY_INTERVAL = 60
MAX_RETRIES = 2

logger = logging.getLogger(__name__)


@task(mandatory=True, max_retries=MAX_RETRIES)
def notify(notifier, event, notification_model):
    logger.debug(u'notification urls to proceed: %s' % notifier.notification_url)

    success = True

    for notification_url in notifier.notification_url.split(';'):
        notification_url = notification_url.strip()

        logger.debug(u'calling notification receiver: %s' % notification_url)

        try:
            message = json.loads(event.message)
        except:
            message = event.message

        data = {
            'event': event.get_event_display(),
            'message': message,
            'created_at': '%s' % event.created_at,
            }
        data['mac'] = generate_hmac_digest(notifier.hmac_key,
                                           '%s%s' % (data['event'],
                                                     data['created_at']))

        response = requests.post(notification_url, json.dumps(data))
        success = False if response.status_code != 200 else success

        notification = notification_model(event=event,
                                          url=notification_url,
                                          status_code=response.status_code,
                                          content=response.text)
        notification.save()

        logger.debug(u'notified: HTTP %s: notification: %s' % (response.status_code,
                                                              notification.id))

    if success:
        return True
    else:
        notify_event.retry(exc=e,
                           countdown=RETRY_INTERVAL + RETRY_INTERVAL *
                                     notify.request.retries)
