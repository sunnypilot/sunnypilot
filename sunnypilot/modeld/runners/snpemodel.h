#pragma once
#pragma clang diagnostic ignored "-Wdeprecated-declarations"

#include <memory>
#include <string>
#include <vector>
#include <cassert>

#ifdef __APPLE__
#include <OpenCL/cl.h>
#else
#include <CL/cl.h>
#endif

#include <DlContainer/IDlContainer.hpp>
#include <DlSystem/DlError.hpp>
#include <DlSystem/ITensor.hpp>
#include <DlSystem/ITensorFactory.hpp>
#include <DlSystem/IUserBuffer.hpp>
#include <DlSystem/IUserBufferFactory.hpp>
#include <SNPE/SNPE.hpp>
#include <SNPE/SNPEBuilder.hpp>
#include <SNPE/SNPEFactory.hpp>

#include "common/swaglog.h"

#define USE_CPU_RUNTIME 0
#define USE_GPU_RUNTIME 1
#define USE_DSP_RUNTIME 2

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

struct SNPEModelInput : public ModelInput {
  std::unique_ptr<zdl::DlSystem::IUserBuffer> snpe_buffer;

  SNPEModelInput(const std::string _name, float *_buffer, int _size, std::unique_ptr<zdl::DlSystem::IUserBuffer> _snpe_buffer) : ModelInput(_name, _buffer, _size), snpe_buffer(std::move(_snpe_buffer)) {}
  void setBuffer(float *_buffer, int _size) {
    ModelInput::setBuffer(_buffer, _size);
    assert(snpe_buffer->setBufferAddress(_buffer) == true);
  }
};

class SNPEModel : public RunModel {
public:
  SNPEModel(const std::string path, float *_output, size_t _output_size, int runtime, bool use_tf8 = false, cl_context context = NULL);
  void addInput(const std::string name, float *buffer, int size);
  void execute();

private:
  std::string model_data;

#ifdef QCOM2
  zdl::DlSystem::Runtime_t snpe_runtime;
#endif

  // snpe model stuff
  std::unique_ptr<zdl::SNPE::SNPE> snpe;
  zdl::DlSystem::UserBufferMap input_map;
  zdl::DlSystem::UserBufferMap output_map;
  std::unique_ptr<zdl::DlSystem::IUserBuffer> output_buffer;

  bool use_tf8;
  float *output;
  size_t output_size;
};
