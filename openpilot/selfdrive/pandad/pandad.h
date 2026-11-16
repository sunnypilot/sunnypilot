#pragma once

#include <string>

#include "common/params.h"
#include "selfdrive/pandad/panda.h"

constexpr int TSS3_ORACLE_HANDOFF_EXIT_CODE = 42;

// The startup catcher owns the Panda safety policy while it is active, but an
// offroad transition must still invalidate PandaSafety's cached onroad state.
// Otherwise a later failed catch can leave the hardware in ELM327 while
// PandaSafety incorrectly believes the previous route's Toyota policy is
// still installed.
constexpr bool should_configure_panda_safety(bool is_onroad, bool startup_catcher_active) {
  return !is_onroad || !startup_catcher_active;
}

int pandad_main_thread(std::string serial);

// deprecated devices
static const std::vector<cereal::PandaState::PandaType> SUPPORTED_PANDA_TYPES = {
  cereal::PandaState::PandaType::RED_PANDA,
  cereal::PandaState::PandaType::TRES,
  cereal::PandaState::PandaType::CUATRO,
};


class PandaSafety {
public:
  PandaSafety(Panda *panda) : panda_(panda) {}
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
  Panda *panda_;
  Params params_;
};
