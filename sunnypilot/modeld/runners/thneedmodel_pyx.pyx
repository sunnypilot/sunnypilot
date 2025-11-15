# distutils: language = c++
# cython: c_string_encoding=ascii, language_level=3

from libcpp cimport bool
from libcpp.string cimport string

from .thneedmodel cimport ThneedModel as cppThneedModel
from openpilot.sunnypilot.modeld.models.commonmodel_pyx cimport CLContext

cdef class ThneedModel:
  cdef cppThneedModel *model

  def __cinit__(self, string path, float[:] output, int runtime, bool use_tf8, CLContext context):
    self.model = new cppThneedModel(path, &output[0], len(output), runtime, use_tf8, context.context)

  def __dealloc__(self):
    del self.model

  def addInput(self, string name, float[:] buffer):
    self.model.addInput(name, &buffer[0], len(buffer))

  def execute(self):
    self.model.execute()

  def getCLBuffer(self, string name):
    return <size_t>self.model.getCLBuffer(name)
