# -*- coding: utf-8 -*-
import fluent.handler
import logging


class NullHandler(logging.Handler):
    """
    This handler does nothing. It's intended to be used to avoid the
    "No handlers could be found for logger XXX" one-off warning. This is
    important for library code, which may contain code to log events. If a user
    of the library does not configure logging, the one-off warning might be
    produced; to avoid this, the library developer simply needs to instantiate
    a NullHandler and add it to the top-level logger of the library module or
    package.
    """
    def handle(self, record):
        pass

    def emit(self, record):
        pass

    def createLock(self):
        self.lock = None


class FluentLabelHandler(fluent.handler.FluentHandler):
    """
    FluentHandler Wrapper

    set proper label with considering normal logging name.
    """

    def emit(self, record):
        """
        emit fluent log
        """
        if record.levelno < self.level: return
        # set Label
        label = None
        if record.name:
            arr = record.name.split('.')
            if len(arr) > 0 and arr[0] == self.tag:
                # adjust normal logging name
                label = '.'.join(arr[1:])
            else:
                label = record.name
        # default formatter is 'fluent.handler.FluentRecordFormatter'
        data = self.fmt.format(record)
        self.sender.emit(label, data)
