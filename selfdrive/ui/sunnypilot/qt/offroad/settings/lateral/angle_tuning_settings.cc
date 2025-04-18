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

  auto *list = new ListWidget(this, false);

  hkgAngleLiveTuning = new ParamControlSP("HkgAngleLiveTuning", tr("HKG Angle Live Tuning"), tr("Enable live tuning of the steering wheel angle."), "../assets/offroad/icon_blank.png");
  list->addItem(hkgAngleLiveTuning);

  auto first_row = new QHBoxLayout();
  hkgAngleSmoothingFactor = new OptionControlSP("HkgTuningAngleSmoothingFactor", tr("HKG Angle Smoothing Factor"), tr("Applies EMA (Exponential Moving Average) to the desired angle steering.<br/>A value closer to 1 means no smoothing.<br/>A value closer to 0 means very smooth (and thus likely too 'soft' steering).<br/>After 50mph/80km/h this setting is virtually always 1."), "../assets/offroad/icon_blank.png", {0, 10}, 1);
  connect(hkgAngleSmoothingFactor, &OptionControlSP::updateLabels, hkgAngleSmoothingFactor, [=]() {
    this->updateToggles(offroad);
  });
  first_row->addWidget(hkgAngleSmoothingFactor);

  hkgTuningOverridingCycles = new OptionControlSP("HkgTuningOverridingCycles", tr("HKG Tuning Overriding Cycles"), tr("Number of cycles to ramp down the current amount of torque on the steering wheel.<br/>A smaller value means a faster override by the user (less effort)"), "../assets/offroad/icon_blank.png", {10, 30}, 1);
  connect(hkgTuningOverridingCycles, &OptionControlSP::updateLabels, hkgTuningOverridingCycles, [=]() {
    this->updateToggles(offroad);
  });
  first_row->addWidget(hkgTuningOverridingCycles);
  list->addItem(first_row);

  auto second_row = new QHBoxLayout();
  hkgAngleMinTorque = new OptionControlSP("HkgTuningAngleMinTorque", tr("HKG Angle Min Torque"), tr("Minimum torque to apply to the steering wheel.<br/>Must be smaller than max."), "../assets/offroad/icon_blank.png", {0, 250}, 5);
  connect(hkgAngleMinTorque, &OptionControlSP::updateLabels, hkgAngleMinTorque, [=]() {
    this->updateToggles(offroad);
  });
  second_row->addWidget(hkgAngleMinTorque);

  hkgAngleMaxTorque = new OptionControlSP("HkgTuningAngleMaxTorque", tr("HKG Angle Max Torque"), tr("Maximum torque to apply to the steering wheel.<br/>Must be bigger than min."), "../assets/offroad/icon_blank.png", {25, 250}, 5);
  connect(hkgAngleMaxTorque, &OptionControlSP::updateLabels, hkgAngleMaxTorque, [=]() {
    this->updateToggles(offroad);
  });
  second_row->addWidget(hkgAngleMaxTorque);
  list->addItem(second_row);
  
  QObject::connect(uiState(), &UIState::offroadTransition, this, &AngleTunningSettings::updateToggles);

  main_layout->addWidget(new ScrollViewSP(list, this));
}

void AngleTunningSettings::showEvent(QShowEvent *event) {
  updateToggles(offroad);
}

void AngleTunningSettings::updateToggles(bool _offroad) {
  auto HkgAngleSmoothingFactorValue = QString::fromStdString(params.get("HkgTuningAngleSmoothingFactor")).toDouble();
  hkgAngleSmoothingFactor->setLabel(QString::number(HkgAngleSmoothingFactorValue / 10, 'f', 1));

  auto HkgAngleMinTorqueValue = QString::fromStdString(params.get("HkgTuningAngleMinTorque")).toInt();
  hkgAngleMinTorque->setLabel(QString::number(HkgAngleMinTorqueValue));

  auto HkgAngleMaxTorqueValue = QString::fromStdString(params.get("HkgTuningAngleMaxTorque")).toInt();
  hkgAngleMaxTorque->setLabel(QString::number(HkgAngleMaxTorqueValue));

  auto HkgTuningOverridingCyclesValue = QString::fromStdString(params.get("HkgTuningOverridingCycles")).toInt();
  hkgTuningOverridingCycles->setLabel(QString::number(HkgTuningOverridingCyclesValue));

  offroad = _offroad;
}
