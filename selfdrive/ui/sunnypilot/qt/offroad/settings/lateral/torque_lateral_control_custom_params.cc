/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/torque_lateral_control_custom_params.h"

TorqueLateralControlCustomParams::TorqueLateralControlCustomParams(const QString &param, const QString &title, const QString &description, const QString &icon, QWidget *parent)
    : ExpandableToggleRow(param, title, description, icon, parent) {

  QFrame *frame = new QFrame(this);
  QGridLayout *frame_layout = new QGridLayout();
  frame->setLayout(frame_layout);
  frame_layout->setSpacing(0);

  torqueLateralControlParamsOverride = new ParamControl(
    "TorqueParamsOverrideEnabled",
    tr("Manual Real-Time Tuning"),
    tr("Enforces the torque lateral controller to use the fixed values instead of the learned values from Self-Tune. Enabling this toggle overrides Self-Tune values."),
    "../assets/offroad/icon_blank.png",
    this
  );
  connect(torqueLateralControlParamsOverride, &ParamControl::toggleFlipped, this, &TorqueLateralControlCustomParams::refresh);
  addItem(torqueLateralControlParamsOverride);

  torqueParamsOverrideLatAccelFactor = new OptionControlSP("TorqueParamsOverrideLatAccelFactor", tr("Lateral Acceleration Factor"), "", "", {1, 500}, 1, false, nullptr, true, false);
  connect(torqueParamsOverrideLatAccelFactor, &OptionControlSP::updateLabels, this, &TorqueLateralControlCustomParams::refresh);
  addItem(torqueParamsOverrideLatAccelFactor);

  torqueParamsOverrideFriction = new OptionControlSP("TorqueParamsOverrideFriction", tr("Friction"), "", "", {1, 100}, 1, false, nullptr, true, false);
  connect(torqueParamsOverrideFriction, &OptionControlSP::updateLabels, this, &TorqueLateralControlCustomParams::refresh);
  addItem(torqueParamsOverrideFriction);

  frame_layout->addWidget(torqueLateralControlParamsOverride, 0, 0, Qt::AlignLeft);
  frame_layout->addWidget(torqueParamsOverrideLatAccelFactor, 1, 0, Qt::AlignLeft);
  frame_layout->addWidget(torqueParamsOverrideFriction, 2, 0, Qt::AlignLeft);

  addItem(frame);

  refresh();
}

void TorqueLateralControlCustomParams::refresh() {
  bool torque_override_param = params.getBool("TorqueParamsOverrideEnabled");
  float laf_param = QString::fromStdString(params.get("TorqueParamsOverrideLatAccelFactor")).toFloat();
  const QString laf_unit = "m/s²";

  float friction_param = QString::fromStdString(params.get("TorqueParamsOverrideFriction")).toFloat();

  torqueParamsOverrideLatAccelFactor->setTitle(tr("Lateral Acceleration Factor") + " - " + (torque_override_param ? tr("Real-time and Offline") : tr("Offline Only")));
  torqueParamsOverrideFriction->setTitle(tr("Friction") + " - " + (torque_override_param ? tr("Real-time and Offline") : tr("Offline Only")));

  torqueParamsOverrideLatAccelFactor->setLabel(QString::number(laf_param, 'f', 2) + " " + laf_unit);
  torqueParamsOverrideFriction->setLabel(QString::number(friction_param, 'f', 2));
}
