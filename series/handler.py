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

from mri import BaseMriDicom

logger = logging.getLogger(__name__)


class IncomingDicomManager(object):
    """
    Generic wrapper for all incoming dicoms -- reads a dicom, gets its
    series_unique_key, and builds a DicomSeriesHandler for it.
    """

    def __init__(self, timeout, output_base_dir):
        self.timeout = timeout
        self.output_base_dir = output_base_dir
        self._series_handlers = {}

    def handle_dicom(self, dcm):
        key = dcm.series_unique_key
        if key not in self._series_handlers:
            self._series_handlers[key] = self._setup_handler(dcm)
        handler = self._series_handlers[key]
        handler.handle_dicom(dcm)

    def _setup_handler(self, dcm):
        key = dcm.series_unique_key
        logger.debug("Setting up handler for %s" % (key))
        out_dir = os.path.join(self.output_base_dir, key)
        dsh = DicomSeriesHandler(self.timeout, key, out_dir, self)
        dsh.start()
        return dsh

    def remove_handler(self, handler):
        logger.debug("Removing handler %s" % (handler.series_key))
        del self._series_handlers[handler.series_key]

    def wait_for_handlers(self):
        timeout = self.timeout + 0.1 # Arbitrary?
        for handler in self._series_handlers.values():
            handler.join(timeout)


class DicomSeriesHandler(threading.Thread):

    def __init__(self, timeout, series_key, output_dir, manager):
        self.timeout = timeout
        self.series_key = series_key
        self.output_dir = output_dir
        self.manager = manager
        self.notifier = threading.Event()
        super(DicomSeriesHandler, self).__init__(name=series_key)

    def start(self):
        self.notifier.set()
        logger.debug("%s - starting" % (self))
        logger.info("%s: waiting for dicoms. Timeout: %s Output Dir: %s" %
            (self, self.timeout, self.output_dir))
        super(DicomSeriesHandler, self).start()

    def run(self):
        logger.debug("%s - running" % (self))
        while self.notifier.is_set():
            self.notifier.clear()
            self.notifier.wait(self.timeout)
        self._finish()
        logger.info("%s: successfully shut down" % (self))

    def _finish(self):
        logger.debug("%s - finishing" % (self))
        self.manager.remove_handler(self)

    def handle_dicom(self, dcm):
        if not self.is_alive():
            raise RuntimeError("%s got handle_dicom before alive!")
        logger.debug("%s - handling dicom %s" % (self, dcm.InstanceNumber))
        self.notifier.set()

    def __str__(self):
        return self.name


if __name__ == '__main__':
    # Easy testing test!
    import sys
    import glob
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    timeout = int(sys.argv[1])
    in_dir = sys.argv[2]
    out_dir = sys.argv[3]
    mgr = IncomingDicomManager(timeout, out_dir)
    for f in glob.iglob("%s/*" % (in_dir)):
        dcm = BaseMriDicom.from_file(f)
        mgr.handle_dicom(dcm)
    mgr.wait_for_handlers()
