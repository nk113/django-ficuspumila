# -*- coding: utf-8 -*-
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from djcelery.models import TaskState

from ficuspumila.settings import ficuspumila as settings

from .tasks import collect_garbages
from .utils import random


logger = logging.getLogger(__name__)


def queue_collect_garbage(sender, **kwargs):
    if random(settings('GC_PROBABILITY', 0.05)):
        collect_garbages.delay(sender, **kwargs)

@receiver(post_save, sender=TaskState)
def post_save_TaskState(sender, instance, created, **kwargs):
    logger.debug(u'handling TaskStage post save event...')

    # garbage collection
    queue_collect_garbage(sender, timestamp_field='tstamp')
