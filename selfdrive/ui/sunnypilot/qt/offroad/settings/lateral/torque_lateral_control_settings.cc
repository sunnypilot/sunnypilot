/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/torque_lateral_control_settings.h"

#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

TorqueLateralControlSettings::TorqueLateralControlSettings(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton *back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidget *list = new ListWidget(this, false);
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "LiveTorqueParamsToggle",
      tr("Self-Tune"),
      tr("Enables self-tune for Torque lateral control for platforms that do not use Torque lateral control by default."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "LiveTorqueParamsRelaxedToggle",
      tr("Less Restrict Settings for Self-Tune (Beta)"),
      tr("Less strict settings when using Self-Tune. This allows torqued to be more forgiving when learning values."),
      "../assets/offroad/icon_blank.png",
    }
  };

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);
    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  torqueLateralControlCustomParams = new TorqueLateralControlCustomParams(
    "CustomTorqueParams",
    tr("Enable Custom Tuning"),
    tr("Enables custom tuning for Torque lateral control. Modifying Lateral Acceleration Factor and Friction below will override the offline values indicated in the YAML files within \"opendbc/car/torque_data\". "
       "The values will also be used live when \"Manual Real-Time Tuning\" toggle is enabled."),
    "../assets/offroad/icon_blank.png",
    this);
  list->addItem(torqueLateralControlCustomParams);

  QObject::connect(uiState(), &UIState::offroadTransition, this, &TorqueLateralControlSettings::updateToggles);
  QObject::connect(toggles["LiveTorqueParamsToggle"], &ParamControlSP::toggleFlipped, [=](bool state) {
    if (!state) {
      params.remove("LiveTorqueParamsRelaxedToggle");
      toggles["LiveTorqueParamsRelaxedToggle"]->refresh();
    }

    updateToggles(offroad);
  });

  main_layout->addWidget(new ScrollViewSP(list, this));
}

void TorqueLateralControlSettings::showEvent(QShowEvent *event) {
  updateToggles(offroad);
}

void TorqueLateralControlSettings::updateToggles(bool _offroad) {
  bool live_toggle = toggles["LiveTorqueParamsToggle"]->isToggled();

  toggles["LiveTorqueParamsToggle"]->setEnabled(_offroad);
  toggles["LiveTorqueParamsRelaxedToggle"]->setEnabled(_offroad && live_toggle);

  torqueLateralControlCustomParams->setEnabled(_offroad);
  torqueLateralControlCustomParams->refresh();

  offroad = _offroad;
}
