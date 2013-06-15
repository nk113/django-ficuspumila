# -*- coding: utf-8 -*-
import json
import logging
import os
import requests

from celery.decorators import task
from datetime import date, timedelta
from django.utils.importlib import import_module

from ficuspumila.core.models import iterator
from ficuspumila.settings import ficuspumila as settings

from .utils import (
    generate_hmac_digest,
    local_required,
)


RETRY_INTERVAL = 60
MAX_RETRIES = 2


logger = logging.getLogger(__name__)


@task
@local_required
def collect_garbages(model, **kwargs):

    days_before = kwargs.get('days_before', settings('GC_DAYS_BEFORE', 30))
    max_records = kwargs.get('max_records', settings('GC_MAX_RECORDS', 1000))
    timestamp_field = kwargs.get('timestamp_field', 'ctime')

    filters = {
        '%s__lte' % timestamp_field: date.today()-timedelta(days=days_before)
    }

    objects = model.objects.filter(**filters)
    count = objects.count()

    logger.debug(u'processing garbage collection (%s, %s < %s, %s objects)' % (
                     model.__name__,
                     timestamp_field,
                     date.today()-timedelta(days=days_before),
                     count))

    for obj in iterator(objects, max_records):
        logger.debug(u'deleting %s object (%s)' % (model.__name__, obj,))

        obj.delete()

    # chain the task
    if count > max_records:
        kwargs['countdown'] = RETRY_INTERVAL
        collect_garbages.delay(model, **kwargs)

    return True


@task(max_retries=MAX_RETRIES)
@local_required
def notify_event(notifier, event, notification_model, **kwargs):

    logger.debug(u'notification urls to proceed (%s)' % (
                     notifier.notification_urls,))

    success = True

    for notification_url in notifier.notification_urls:

        logger.debug(u'calling notification receiver (%s)' % (
                         notification_url,))

        data = {
            'event': event.name.name,
            'message': event.message,
            'ctime': '%s' % event.ctime,
            }

        data['hmac'] = generate_hmac_digest(notifier.hmac_key,
                                            '%s%s' % (data['event'],
                                                      data['ctime']))

        response = requests.post(notification_url, json.dumps(data))
        success = False if response.status_code != 200 else success

        notification = notification_model.objects.create(
                           event=event,
                           url=notification_url,
                           status_code=response.status_code,
                           content=response.text)

        logger.info(u'notified (HTTP %s: notification: %s)' % (
                        response.status_code,
                        notification.id))

    if success:
        return True
    else:
        notify_event.retry(countdown=RETRY_INTERVAL * notify_event.request.retries)
        return False
