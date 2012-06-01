#!/usr/bin/env python
# coding: utf8
#
# Part of scansave -- tools to manage incoming files from an MR scanner
#
# Copyright 2012 Board of Regents of the University of Wisconsin System
#
# Does a resource-leak test of the dicom series handlers. At least, hopefully.
# Well, anyhow, it shows you how to use them.

import math
import time
from optparse import OptionParser

from mocks import FakeDicom
import handler

import logging
logger = logging.getLogger(__name__)

class CountingDicomHandler(handler.BaseDicomSeriesHandler):

    def __init__(self, timeout, name, manager):
        super(CountingDicomHandler, self).__init__(timeout, name, manager)
        self._uses = 0

    def _handle(self, dcm):
        self._uses += 1
        logger.debug("Handling %s (%s)" % (self.name, self._uses))

    def _finish(self):
        logger.info("Finishing %s after %s uses" % (self.name, self._uses))


def main(out_iters=100, in_iters=30, timeout=1):
    logger.info(
        "leakdown start out_iters: %s in_iters %s timeout %s" %
        (out_iters, in_iters, timeout))

    def key_fx(dcm):
        return dcm.key

    def handler_factory(example_dicom, manager):
        return CountingDicomHandler(
            timeout, key_fx(example_dicom), manager)

    mgr = handler.DicomManager(timeout, key_fx, handler_factory)

    for i in range(out_iters):
        for j in range(in_iters):
            logger.debug("Iter: %s" % i)
            key = "%s" % (i)
            d = FakeDicom(key)
            logger.debug("%s" % d)
            mgr.handle_dicom(d)
            #time.sleep(timeout)
    mgr.wait_for_handlers()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    import sys
    out_iters = int(sys.argv[1])
    in_iters = int(sys.argv[2])
    timeout = float(sys.argv[3])
    main(out_iters, in_iters, timeout)
