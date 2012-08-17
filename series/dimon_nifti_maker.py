# coding: utf8
#
# Copyright 2012 Board of Regents of the University of Wisconsin System
#
# Part of the scansave package

from __future__ import print_function, with_statement, unicode_literals
import subprocess
from tempfile import mkdtemp
import shutil
import os
from StringIO import StringIO


class DimonNiftiMaker(object):
    """
    Takes a directory full of dicoms and uses afni's 'Dimon' to produce a
    shiny, delicious nifti file.
    """

    def __init__(self, in_prefix, out_filename, stdout=None, stderr=None):
        self.in_prefix = in_prefix
        self.out_filename = out_filename
        self.stdout = stdout or subprocess.PIPE
        self.stderr = stderr or subprocess.PIPE

    def make_nifti(self):
        self.tmp_dir = mkdtemp()
        self._run_dimon()
        self._store_file()
        shutil.rmtree(self.tmp_dir)

    def _run_dimon(self):
        cmd = ['Dimon',
            '-GERT_Reco', '-gert_create_dataset', '-gert_write_as_nifti',
            '-gert_to3d_prefix', 'out', '-infile_prefix', self.in_prefix]
        proc = subprocess.Popen(cmd, stdout=self.stdout, stderr=self.stderr,
            cwd=self.tmp_dir)
        (self.stdout_data, self.stderr_data) = proc.communicate()

    def _store_file(self):
        shutil.move(os.path.join(self.tmp_dir, "out.nii"), self.out_filename)