#pragma once

#include <string>
#include <vector>

#include "common/params.h"
#include "selfdrive/pandad/panda.h"

void pandad_main_thread(std::vector<std::string> serials);

// deprecated devices
static const std::vector<cereal::PandaState::PandaType> DEPRECATED_PANDA_TYPES = {
  cereal::PandaState::PandaType::WHITE_PANDA,
  cereal::PandaState::PandaType::GREY_PANDA,
  cereal::PandaState::PandaType::BLACK_PANDA,
  cereal::PandaState::PandaType::PEDAL,
  cereal::PandaState::PandaType::UNO,
  cereal::PandaState::PandaType::RED_PANDA_V2
};


class PandaSafety {
public:
  PandaSafety(const std::vector<Panda *> &pandas) : pandas_(pandas) {}
  void configureSafetyMode(bool is_onroad);
  bool getOffroadMode();

private:
  void updateMultiplexingMode();
  std::vector<std::string> fetchCarParams();
  void setSafetyMode(const std::vector<std::string> &params_string);

  bool initialized_ = false;
  bool log_once_ = false;
  bool safety_configured_ = false;
  bool prev_obd_multiplexing_ = false;
  std::vector<Panda *> pandas_;
  Params params_;
};
