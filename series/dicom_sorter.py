#!/usr/bin/env python
# coding: utf8
#
# Copyright 2012 Board of Regents of the University of Wisconsin System
#
# A simple file sorter. Walks a directory tree, examines all of the files,
# and sorts them into their own directories -- the directory is:
# OUTPUT_DIR/StudyDate-StudyID/SeriesNumber

import sys
import os
import shutil

import handler
import file_dicom

import logging
logger = logging.getLogger(__name__)


class SortingDicomHandler(handler.ThreadedDicomSeriesHandler):
    """
    Moves dicoms into the folder specified at init time. Your factory
    function will compute target_dir
    """

    def __init__(self, target_dir, timeout, name, manager):
        super(SortingDicomHandler, self).__init__(timeout, name, manager)
        self.target_dir = target_dir

    def _handle(self, dcm):
        logger.info("Copying %s to %s" % (dcm.filename, self.target_dir))
        shutil.copy(dcm.filename, self.target_dir)

TIMEOUT = 3

def main(in_dir, out_dir):
    logger.info("Searching %s, writing to %s" % (out_dir, in_dir))

    def key_fx(dcm):
        return "%s-%s-%s" % (dcm.StudyDate, dcm.StudyID, dcm.SeriesNumber)

    def handler_factory(dcm, manager):
        exam_key = "%s-%s" % (dcm.StudyDate, dcm.StudyID)
        target_dir = os.path.join(out_dir, exam_key, str(dcm.SeriesNumber))
        logger.info("Computed target_dir: %s" % target_dir)
        try:
            os.makedirs(target_dir)
        except:
            pass

        return SortingDicomHandler(target_dir, TIMEOUT, key_fx(dcm), manager)

    mgr = handler.ThreadedDicomManager(TIMEOUT, key_fx, handler_factory)
    for root, dirs, files in os.walk(in_dir):
        for f in files:
            pathname = os.path.join(root, f)
            logger.debug("reading %s" % pathname)
            try:
                d = file_dicom.read_file(pathname)
                mgr.handle_dicom(d)
            except:
                logger.warn("Could not handle %s" % pathname)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    in_dir, out_dir = sys.argv[1:]
    main(in_dir, out_dir)