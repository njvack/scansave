#!/usr/bin/env python
# coding: utf8
#
# Part of scansave -- tools to manage incoming files from an MR scanner
#
# Copyright 2012 Board of Regents of the University of Wisconsin System
#
# Does a resource-leak test of the dicom series handlers. At least, hopefully.

import math
import time

from mock.fake_dicom import FakeDicom
from series import handler

import logging
logger = logging.getLogger("handler_leakdown")


def main(out_iters=1000, in_iters=30, timeout=1, key_max=1000):
    logger.info(
        "leakdown start out_iters: in_iters %s %s timeout %s key_max: %s" %
        (out_iters, in_iters, timeout, key_max))

    key_chars = int(math.ceil(math.log10(key_max)))
    mgr = handler.IncomingDicomManager(timeout, ".")

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
    main()