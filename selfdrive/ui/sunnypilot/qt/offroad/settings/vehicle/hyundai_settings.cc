/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/hyundai_settings.h"

HyundaiSettings::HyundaiSettings(QWidget *parent) : BrandSettingsInterface(parent) {
  std::vector<QString> tuning_texts{ tr("Off"), tr("Dynamic"), tr("Predictive") };
  longitudinalTuningToggle = new ButtonParamControl(
    "HyundaiLongitudinalTuning",
    tr("Custom Longitudinal Tuning"),
    "",
    "",
    tuning_texts,
    500
  );
  QObject::connect(longitudinalTuningToggle, &ButtonParamControlSP::buttonClicked, this, &HyundaiSettings::updateSettings);
  list->addItem(longitudinalTuningToggle);
  longitudinalTuningToggle->showDescription();
}

void HyundaiSettings::updateSettings() {
  auto longitudinal_tuning_param = std::atoi(params.get("HyundaiLongitudinalTuning").c_str());
  uint32_t sp_flags = 0;

  auto cp_bytes = params.get("CarParamsPersistent");
  auto cp_sp_bytes = params.get("CarParamsSPPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    has_longitudinal_control = hasLongitudinalControl(CP);
  } else {
    has_longitudinal_control = false;
  }

  if (!cp_sp_bytes.empty()) {
    AlignedBuffer aligned_buf_sp;
    capnp::FlatArrayMessageReader cmsg_sp(aligned_buf_sp.align(cp_sp_bytes.data(), cp_sp_bytes.size()));
    cereal::CarParamsSP::Reader CP_SP = cmsg_sp.getRoot<cereal::CarParamsSP>();

    sp_flags = CP_SP.getFlags();
  }

  LongitudinalTuningOption longitudinal_tuning_option;
  if (longitudinal_tuning_param == int(LongitudinalTuningOption::PREDICTIVE)) {
    longitudinal_tuning_option = LongitudinalTuningOption::PREDICTIVE;
  } else if (longitudinal_tuning_param == int(LongitudinalTuningOption::DYNAMIC)) {
    longitudinal_tuning_option = LongitudinalTuningOption::DYNAMIC;
  } else {
    longitudinal_tuning_option = LongitudinalTuningOption::OFF;
  }

  bool longitudinal_tuning_disabled = !has_longitudinal_control;
  QString longitudinal_tuning_description = longitudinalTuningDescription(longitudinal_tuning_option);
  if (longitudinal_tuning_disabled) {
    longitudinal_tuning_description = toggleDisableMsg(offroad, has_longitudinal_control);
  }

  longitudinalTuningToggle->setDescription(longitudinal_tuning_description);
  longitudinalTuningToggle->showDescription();

  if (!offroad) {
    if (sp_flags & (16 | 32)) {  // HyundaiFlagsSP.LONG_TUNING_DYNAMIC | HyundaiFlagsSP.LONG_TUNING_PREDICTIVE
      longitudinalTuningToggle->setEnableSelectedButtons(!longitudinal_tuning_disabled, {1, 2});
    } else {
      longitudinalTuningToggle->setEnableSelectedButtons(!longitudinal_tuning_disabled);
    }
  } else {
    longitudinalTuningToggle->setEnabled(!longitudinal_tuning_disabled);
  }
}
