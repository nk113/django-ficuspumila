# -*- coding: utf-8 -*-
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from ficuspumila.core.handlers import queue_collect_garbage
from ficuspumila.core.tasks import notify_event
from ficuspumila.core.utils import random

from .models import (
    SourceEvent, SourceNotification,
)


logger = logging.getLogger(__name__)


@receiver(post_save, sender=SourceEvent)
def post_save_SourceEvent(sender, instance, created, **kwargs):
    logger.debug(u'handling SourceEvent post save event...')

    # notify event if source has notification receivers
    if len(instance.source.notification_urls):
        notify_event.delay(instance.source, instance, SourceNotification)

    # garbage collection
    queue_collect_garbage(sender, days_before=14)
