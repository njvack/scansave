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

from mocks import FakeDicom
import handler

import logging
logger = logging.getLogger("handler_leakdown")


def main(out_iters=100, in_iters=30, timeout=1):
    logger.info(
        "leakdown start out_iters: %s in_iters %s timeout %s" %
        (out_iters, in_iters, timeout))

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
    import sys
    out_iters = int(sys.argv[1])
    in_iters = int(sys.argv[2])
    timeout = float(sys.argv[3])
    main(out_iters, in_iters, timeout)
