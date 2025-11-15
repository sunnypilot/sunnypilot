#pragma once

#include <string>
#include <vector>
#include <memory>
#include <cassert>

#ifdef __APPLE__
#include <OpenCL/cl.h>
#else
#include <CL/cl.h>
#endif

#include "common/swaglog.h"
#include "sunnypilot/modeld/thneed/thneed.h"

struct ModelInput {
  const std::string name;
  float *buffer;
  int size;

  ModelInput(const std::string _name, float *_buffer, int _size) : name(_name), buffer(_buffer), size(_size) {}
  virtual void setBuffer(float *_buffer, int _size) {
    assert(size == _size || size == 0);
    buffer = _buffer;
    size = _size;
  }
};

class RunModel {
public:
  std::vector<std::unique_ptr<ModelInput>> inputs;

  virtual ~RunModel() {}
  virtual void execute() {}
  virtual void* getCLBuffer(const std::string name) { return nullptr; }

  virtual void addInput(const std::string name, float *buffer, int size) {
    inputs.push_back(std::unique_ptr<ModelInput>(new ModelInput(name, buffer, size)));
  }
  virtual void setInputBuffer(const std::string name, float *buffer, int size) {
    for (auto &input : inputs) {
      if (name == input->name) {
        input->setBuffer(buffer, size);
        return;
      }
    }
    LOGE("Tried to update input `%s` but no input with this name exists", name.c_str());
    assert(false);
  }
};

class ThneedModel : public RunModel {
public:
  ThneedModel(const std::string path, float *_output, size_t _output_size, int runtime, bool use_tf8 = false, cl_context context = NULL);
  void *getCLBuffer(const std::string name);
  void execute();
private:
  Thneed *thneed = NULL;
  bool recorded;
  float *output;
};
