# coding: utf8
# Part of scansave -- tools to manage incoming files from an MR scanner
#
# Copyright 2012 Board of Regents of the University of Wisconsin System
#
# A system for accepting sets of dicom files, classifying them, putting them
# into a proper home, and executing some function wheh it's done seeing new
# files.

import threading
import logging
import os

from mri import BaseDicom

logger = logging.getLogger(__name__)


class IncomingDicomManager(object):
    """
    Generic wrapper for all incoming dicoms -- reads a dicom, gets its
    series_unique_key, and builds a DicomSeriesHandler for it.
    """

    def __init__(self, timeout, dicom_key_fx, handler_factory):
        """
        Build a new IncomingDicomManager.
        timeout: The time this manager should wait for handlers to finish.
        dicom_key_fx: Returns a string uniquely identifying a dicom's series,
        given a dicom object
        handler_factory: Creates a new dicom handler, is passed an example
        dicom, name, and self.
        """
        self.timeout = timeout
        self.dicom_key_fx = dicom_key_fx
        self.handler_factory = handler_factory
        self._series_handlers = {}
        self._mutex = threading.Condition()

    def handle_dicom(self, dcm):
        key = self.dicom_key_fx(dcm)
        with self._mutex:
            if key not in self._series_handlers:
                logger.debug("Setting up handler for key: %s" % (key))
                self._series_handlers[key] = self._setup_handler(dcm)
        handler = self._series_handlers[key]
        handler.handle_dicom(dcm)

    def _setup_handler(self, dcm):
        dsh = self.handler_factory(dcm, self)
        dsh.start()
        return dsh

    def remove_handler(self, handler):
        logger.debug("Removing handler %s" % (handler.name))
        with self._mutex:
            del self._series_handlers[handler.name]

    def wait_for_handlers(self):
        for handler in self._series_handlers.values():
            handler.join(self.timeout)


class BaseDicomSeriesHandler(threading.Thread):

    def __init__(self, timeout, name, manager):
        super(BaseDicomSeriesHandler, self).__init__(name=name)
        self.timeout = timeout
        self.manager = manager
        self.notifier = threading.Condition()

    def start(self):
        self._stop = False
        logger.info("%s: waiting for dicoms. Timeout: %s" %
            (self, self.timeout))
        super(BaseDicomSeriesHandler, self).start()

    def run(self):
        logger.debug("%s - running" % (self))
        with self.notifier:
            while not self._stop:
                self._stop = True
                self.notifier.wait(self.timeout)
            self._finish()
            self.manager.remove_handler(self)
        logger.debug("%s: successfully shut down" % (self))

    def _finish(self):
        """
        Actually finish handling dicoms. Override this method in subclasses.
        """
        logger.debug("%s - finishing" % (self))

    def handle_dicom(self, dcm):
        if not self.is_alive():
            raise RuntimeError("%s got handle_dicom before alive!" % (self))
        with self.notifier:
            self._stop = False
            self._handle(dcm)
            self.notifier.notify()

    def _handle(self, dcm):
        """
        Do the internal handling of the dicom. Override this method in
        subclasses.
        """
        logger.debug("%s - handling dicom" % (self))

    def __str__(self):
        return "%s" % (self.name)


if __name__ == '__main__':
    # Easy testing test!
    import sys
    import glob
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    timeout = int(sys.argv[1])
    in_dir = sys.argv[2]

    def key_fx(dcm):
        return "%s-%s-%s" % (dcm.StudyDate, dcm.StudyID, dcm.SeriesNumber)

    def handler_factory(example_dicom, manager):
        name = key_fx(example_dicom)
        return BaseDicomSeriesHandler(timeout, name, manager)

    mgr = IncomingDicomManager(timeout, key_fx, handler_factory)
    for f in glob.iglob("%s/*" % (in_dir)):
        dcm = BaseDicom.from_file(f)
        mgr.handle_dicom(dcm)
    mgr.wait_for_handlers()
