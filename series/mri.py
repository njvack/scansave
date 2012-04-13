# coding: utf8
# Part of scansave -- tools to manage incoming files from an MR scanner
#
# Copyright 2012 Board of Regents of the University of Wisconsin System
#
# TODO LICENSE
#
# Subclasses of pydicom's dicom.Dataset, designed to let you unambiguously
# group dicoms together in a series, or 

import dicom

class BaseMriDicom(dicom.dataset.Dataset):

    @classmethod
    def from_file(klass, *args, **kwargs):
        dcm = dicom.read_file(*args, **kwargs)
        return klass(dcm)

    @property
    def series_unique_key(self):
        return "%s-%s-%s" % (self.StudyID, self.SeriesNumber, self.StudyDate)
