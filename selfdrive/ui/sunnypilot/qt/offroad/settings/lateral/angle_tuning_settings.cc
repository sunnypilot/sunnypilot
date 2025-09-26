/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/angle_tuning_settings.h"

#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

AngleTunningSettings::AngleTunningSettings(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton *back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  auto *list = new ListWidgetSP(this, false);

  main_layout->addWidget(new QWidget());

  enableHkgAngleSmoothingFactor = new ExpandableToggleRow("EnableHkgTuningAngleSmoothingFactor", tr("HKG Angle Smoothing Factor"), tr("Applies EMA (Exponential Moving Average) to the desired angle steering and avoid overcorrections."), "../assets/offroad/icon_blank.png");
  list->addItem(enableHkgAngleSmoothingFactor);

  auto first_row = new QHBoxLayout();
  hkgTuningOverridingCycles = new OptionControlSP("HkgTuningOverridingCycles", tr("Override Ramp-Down Cycles"), tr("Number of cycles to ramp down the current amount of torque on the steering wheel.<br/>A smaller value means a faster override by the user (less effort)"), "../assets/offroad/icon_blank.png", {10, 30}, 1);
  connect(hkgTuningOverridingCycles, &OptionControlSP::updateLabels, hkgTuningOverridingCycles, [=]() {
    this->updateToggles(offroad);
  });
  first_row->addWidget(hkgTuningOverridingCycles);

  hkgAngleMinTorque = new OptionControlSP("HkgTuningAngleMinTorqueReductionGain", tr("Override Steering Effort"), tr("Sets the steering effort percentage used when the driver is overriding lateral control.<br/>Higher values increase resistance and make the wheel feel stiffer."), "../assets/offroad/icon_blank.png", {5, 60}, 1);
  connect(hkgAngleMinTorque, &OptionControlSP::updateLabels, hkgAngleMinTorque, [=]() {
    this->updateToggles(offroad);
  });
  first_row->addWidget(hkgAngleMinTorque);
  list->addItem(first_row);

  auto second_row = new QHBoxLayout();
  hkgAngleActiveTorque = new OptionControlSP("HkgTuningAngleActiveTorqueReductionGain", tr("Min Active Torque"), tr("Torque applied when lateral control is active but the vehicle is not turning.<br/>Used to maintain lane centering on straight paths when no user input is detected."), "../assets/offroad/icon_blank.png", {10, 100}, 1);
  connect(hkgAngleActiveTorque, &OptionControlSP::updateLabels, hkgAngleActiveTorque, [=]() {
    this->updateToggles(offroad);
  });
  second_row->addWidget(hkgAngleActiveTorque);

  hkgAngleMaxTorque = new OptionControlSP("HkgTuningAngleMaxTorqueReductionGain", tr("Max Torque Allowance"), tr("Sets the maximum torque reduction percentage the controller can apply during normal lateral control.<br/>"), "../assets/offroad/icon_blank.png", {10, 100}, 1);
  connect(hkgAngleMaxTorque, &OptionControlSP::updateLabels, hkgAngleMaxTorque, [=]() {
    this->updateToggles(offroad);
  });
  second_row->addWidget(hkgAngleMaxTorque);
  list->addItem(second_row);
  
  QObject::connect(uiState(), &UIState::offroadTransition, this, &AngleTunningSettings::updateToggles);

  main_layout->addWidget(new ScrollViewSP(list, this));

  auto *warning = new QLabel(tr("Reboot required for settings to apply; Tap on each setting to see more details."));
  warning->setStyleSheet("font-size: 30px; font-weight: 500; font-family: 'Noto Color Emoji'; color: orange;");
  main_layout->addWidget(warning, 0, Qt::AlignCenter);
}

void AngleTunningSettings::showEvent(QShowEvent *event) {
  updateToggles(offroad);
}

void AngleTunningSettings::updateToggles(bool _offroad) {
  auto HkgAngleSmoothingFactorValue = params.getBool("EnableHkgTuningAngleSmoothingFactor");
  enableHkgAngleSmoothingFactor->toggleFlipped(HkgAngleSmoothingFactorValue);

  auto HkgAngleMinTorqueValue = QString::fromStdString(params.get("HkgTuningAngleMinTorqueReductionGain")).toInt();
  hkgAngleMinTorque->setLabel(QString::number(HkgAngleMinTorqueValue)+"%");

  auto HkgAngleActiveTorqueValue = QString::fromStdString(params.get("HkgTuningAngleActiveTorqueReductionGain")).toInt();
  hkgAngleActiveTorque->setLabel(QString::number(HkgAngleActiveTorqueValue)+"%");

  auto HkgAngleMaxTorqueValue = QString::fromStdString(params.get("HkgTuningAngleMaxTorqueReductionGain")).toInt();
  hkgAngleMaxTorque->setLabel(QString::number(HkgAngleMaxTorqueValue)+"%");

  auto HkgTuningOverridingCyclesValue = QString::fromStdString(params.get("HkgTuningOverridingCycles")).toInt();
  hkgTuningOverridingCycles->setLabel(QString::number(HkgTuningOverridingCyclesValue));

  offroad = _offroad;
}
