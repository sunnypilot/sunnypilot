# distutils: language = c++
# cython: c_string_encoding=ascii, language_level=3

import os
from libcpp cimport bool
from libcpp.string cimport string

from .snpemodel cimport SNPEModel as cppSNPEModel
from openpilot.sunnypilot.modeld.models.commonmodel_pyx cimport CLContext

os.environ['ADSP_LIBRARY_PATH'] = "/data/pythonpath/third_party/snpe/dsp/"

cdef class SNPEModel:
  cdef cppSNPEModel *model

  def __cinit__(self, string path, float[:] output, int runtime, bool use_tf8, CLContext context):
    self.model = new cppSNPEModel(path, &output[0], len(output), runtime, use_tf8, context.context)

  def __dealloc__(self):
    del self.model

  def addInput(self, string name, float[:] buffer):
    self.model.addInput(name, &buffer[0], len(buffer))

  def execute(self):
    self.model.execute()
