#pragma once
#pragma clang diagnostic ignored "-Wdeprecated-declarations"

#include <memory>
#include <string>
#include <utility>

#include <DlContainer/IDlContainer.hpp>
#include <DlSystem/DlError.hpp>
#include <DlSystem/ITensor.hpp>
#include <DlSystem/ITensorFactory.hpp>
#include <DlSystem/IUserBuffer.hpp>
#include <DlSystem/IUserBufferFactory.hpp>
#include <SNPE/SNPE.hpp>
#include <SNPE/SNPEBuilder.hpp>
#include <SNPE/SNPEFactory.hpp>

#include "sunnypilot/modeld/runners/runmodel.h"

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
