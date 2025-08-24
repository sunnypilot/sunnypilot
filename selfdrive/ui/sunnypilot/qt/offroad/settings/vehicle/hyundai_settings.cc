/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/hyundai_settings.h"

HyundaiSettings::HyundaiSettings(QWidget *parent) : BrandSettingsInterface(parent) {

  std::vector<QString> custom_btn_texts{ tr("Off"), tr("Bookmark") };
  customButtonMapping = new ButtonParamControlSP(
    "SteeringCustomButtonMapping",
    tr("Steering Custom ☆ Button"),
    tr("Customize the steering wheel custom/star button for openpilot control.\n"
       "This will not disable OEM functionality."),
    "",
    custom_btn_texts,
    300
  );
  list->addItem(customButtonMapping);

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

  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    has_longitudinal_control = hasLongitudinalControl(CP);
  } else {
    has_longitudinal_control = false;
  }

  auto cp_sp_bytes = params.get("CarParamsSPPersistent");
  if (!cp_sp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_sp_bytes.data(), cp_sp_bytes.size()));
    cereal::CarParamsSP::Reader CP_SP = cmsg.getRoot<cereal::CarParamsSP>();

    // TODO-SP: Better way to get the flag value in qt?
    has_custom_button = CP_SP.getFlags() & 512; // 512 = HAS_CUSTOM_BUTTON (2 ** 9)
  } else {
    has_custom_button = false;
  }

  LongitudinalTuningOption longitudinal_tuning_option;
  if (longitudinal_tuning_param == int(LongitudinalTuningOption::PREDICTIVE)) {
    longitudinal_tuning_option = LongitudinalTuningOption::PREDICTIVE;
  } else if (longitudinal_tuning_param == int(LongitudinalTuningOption::DYNAMIC)) {
    longitudinal_tuning_option = LongitudinalTuningOption::DYNAMIC;
  } else {
    longitudinal_tuning_option = LongitudinalTuningOption::OFF;
  }

  bool longitudinal_tuning_disabled = !offroad || !has_longitudinal_control;
  QString longitudinal_tuning_description = longitudinalTuningDescription(longitudinal_tuning_option);
  if (longitudinal_tuning_disabled) {
    longitudinal_tuning_description = toggleDisableMsg(offroad, has_longitudinal_control);
  }

  longitudinalTuningToggle->setEnabled(!longitudinal_tuning_disabled);
  longitudinalTuningToggle->setDescription(longitudinal_tuning_description);
  longitudinalTuningToggle->showDescription();

  customButtonMapping->setVisible(has_custom_button);
}
