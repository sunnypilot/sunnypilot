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

  std::vector<QString> radar_tuning_texts{ tr("Off"), tr("Lead Only"), tr("Full Radar") };
  radarToggle = new ButtonParamControl(
    "HyundaiRadar",
    tr("Radar Tracks"),
    "",
    "",
    radar_tuning_texts,
    500
  );
  QObject::connect(radarToggle, &ButtonParamControlSP::buttonClicked, this, &HyundaiSettings::updateSettings);
  list->addItem(radarToggle);
  radarToggle->showDescription();
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

  auto radar_param = std::atoi(params.get("HyundaiRadar").c_str());

  RadarOption radar_option;
  if (radar_param == int(RadarOption::LEAD_ONLY)) {
    radar_option = RadarOption::LEAD_ONLY;
  } else if (radar_param == int(RadarOption::FULL_RADAR)) {
    radar_option = RadarOption::FULL_RADAR;
  } else {
    radar_option = RadarOption::OFF;
  }

  bool radar_disabled = !offroad || !has_longitudinal_control;
  QString radar_description = radarDescription(radar_option);
  if (radar_disabled) {
    radar_description = toggleDisableMsg(offroad, has_longitudinal_control);
  }

  radarToggle->setEnabled(!radar_disabled);
  radarToggle->setDescription(radar_description);
  radarToggle->showDescription();
}
