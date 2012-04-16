# coding: utf8
# Part of scansave -- tools to manage incoming files from an MR scanner
#
# Copyright 2012 Board of Regents of the University of Wisconsin System
#
# A mock dicom class that'll let us exercise our series handlers without
# actually needing to read a bunch of dicoms

class FakeDicom(object):

    def __init__(self, key):
        self.key = key

    @property
    def series_unique_key(self):
        return self.key

    @property
    def InstanceNumber(self):
        return 0

    def __str__(self):
        return "FakeDicom(%s)" % (self.key)