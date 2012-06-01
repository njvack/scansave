# coding: utf8
# Part of scansave -- tools to manage incoming files from an MR scanner
#
# Copyright 2012 Board of Regents of the University of Wisconsin System
#
# TODO LICENSE
#
# Subclasses of pydicom's dicom.Dataset, designed to let you unambiguously
# group dicoms together in a series.

import dicom

class FileDicom(dicom.dataset.Dataset):

    @classmethod
    def from_file(klass, filename):
        dcm = dicom.read_file(filename)
        dcm.filename = filename
        return klass(dcm)
