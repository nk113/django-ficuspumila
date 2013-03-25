# -*- coding: utf-8 -*-
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from ficuspumila.core.utils import random
from .models import (
    SourceEvent,
)


logger = logging.getLogger(__name__)


@receiver(post_save, sender=SourceEvent)
def post_save_SourceEvent(sender, instance, created, **kwargs):
    logger.debug(u'handling post save event...')

    if random(settings.GC_PROBABILITY):

        events = SourceEvent.objects.filter(source=instance.source,
                                            ctime__lte=date.today()-timedelta(
                                                days=settings.GC_DAYS_BEFORE))

        logger.debug(u'processing garbage collection (ctime < %s, %s events)' % (
                         date.today()-timedelta(days=settings.GC_DAYS_BEFORE),
                         len(events)))

        for event in events:
            event.delete()
