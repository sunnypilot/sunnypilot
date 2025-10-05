/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral_panel.h"

#include "common/util.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

LateralPanel::LateralPanel(SettingsWindowSP *parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);
  ListWidget *list = new ListWidget(this, false);

  sunnypilotScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(sunnypilotScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  // MADS
  madsToggle = new ParamControl(
    "Mads",
    tr("Modular Assistive Driving System (MADS)"),
    tr("Enable the beloved MADS feature. Disable toggle to revert back to stock sunnypilot engagement/disengagement."),
    "");
  madsToggle->setConfirmation(true, false);
  list->addItem(madsToggle);

  madsSettingsButton = new PushButtonSP(tr("Customize MADS"));
  madsSettingsButton->setObjectName("mads_btn");
  connect(madsSettingsButton, &QPushButton::clicked, [=]() {
    sunnypilotScroller->setLastScrollPosition();
    main_layout->setCurrentWidget(madsWidget);
  });
  QObject::connect(madsToggle, &ToggleControl::toggleFlipped, madsSettingsButton, &PushButtonSP::setEnabled);

  madsWidget = new MadsSettings(this);
  connect(madsWidget, &MadsSettings::backPress, [=]() {
    sunnypilotScroller->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);
  });
  list->addItem(madsSettingsButton);

  list->addItem(vertical_space());
  list->addItem(horizontal_line());
  list->addItem(vertical_space());

  // Lane Change Settings
  laneChangeSettingsButton = new PushButtonSP(tr("Customize Lane Change"));
  laneChangeSettingsButton->setObjectName("lane_change_btn");
  connect(laneChangeSettingsButton, &QPushButton::clicked, [=]() {
    sunnypilotScroller->setLastScrollPosition();
    main_layout->setCurrentWidget(laneChangeWidget);
  });

  laneChangeWidget = new LaneChangeSettings(this);
  connect(laneChangeWidget, &LaneChangeSettings::backPress, [=]() {
    sunnypilotScroller->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);
  });
  list->addItem(laneChangeSettingsButton);

  list->addItem(vertical_space(0));
  list->addItem(horizontal_line());

  // Blinker Pause Lateral Control
  blinkerPauseLateralSettings = new BlinkerPauseLateralSettings(
    "BlinkerPauseLateralControl",
    tr("Pause Lateral Control with Blinker"),
    tr("Pause lateral control with blinker when traveling below the desired speed selected."),
    "",
    this);
  list->addItem(blinkerPauseLateralSettings);

  list->addItem(horizontal_line());

  // Customized Torque Lateral Control
  torqueLateralControlToggle = new ParamControl(
    "EnforceTorqueControl",
    tr("Enforce Torque Lateral Control"),
    tr("Enable this to enforce sunnypilot to steer with Torque lateral control."),
    "");
  list->addItem(torqueLateralControlToggle);

  torqueLateralControlSettingsButton = new PushButtonSP(tr("Customize Params"));
  torqueLateralControlSettingsButton->setObjectName("torque_btn");
  connect(torqueLateralControlSettingsButton, &QPushButton::clicked, [=]() {
    sunnypilotScroller->setLastScrollPosition();
    main_layout->setCurrentWidget(torqueLateralControlWidget);
  });
  QObject::connect(torqueLateralControlToggle, &ToggleControl::toggleFlipped, [=](bool state) {
    torqueLateralControlSettingsButton->setEnabled(state);
    nnlcToggle->updateToggle(offroad);
    updateToggles(offroad);
  });

  torqueLateralControlWidget = new TorqueLateralControlSettings(this);
  connect(torqueLateralControlWidget, &TorqueLateralControlSettings::backPress, [=]() {
    sunnypilotScroller->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);
  });
  list->addItem(torqueLateralControlSettingsButton);

  list->addItem(vertical_space(0));
  list->addItem(horizontal_line());

  // Neural Network Lateral Control
  nnlcToggle = new NeuralNetworkLateralControl();
  list->addItem(nnlcToggle);

  QObject::connect(nnlcToggle, &ParamControl::toggleFlipped, [=](bool state) {
    if (state) {
      nnlcToggle->showDescription();
    } else {
      nnlcToggle->hideDescription();
    }

    nnlcToggle->updateToggle(offroad);
    updateToggles(offroad);
  });

  QObject::connect(uiState(), &UIState::offroadTransition, this, &LateralPanel::updateToggles);

  sunnypilotScroller = new ScrollViewSP(list, this);
  vlayout->addWidget(sunnypilotScroller);

  main_layout->addWidget(sunnypilotScreen);
  main_layout->addWidget(madsWidget);
  main_layout->addWidget(laneChangeWidget);
  main_layout->addWidget(torqueLateralControlWidget);

  setStyleSheet(R"(
    #back_btn {
      font-size: 50px;
      margin: 0px;
      padding: 15px;
      border-width: 0;
      border-radius: 30px;
      color: #dddddd;
      background-color: #393939;
    }
    #back_btn:pressed {
      background-color:  #4a4a4a;
    }
  )");

  main_layout->setCurrentWidget(sunnypilotScreen);
}

void LateralPanel::showEvent(QShowEvent *event) {
  nnlcToggle->updateToggle(offroad);
  updateToggles(offroad);
}

void LateralPanel::hideEvent(QHideEvent *event) {
  main_layout->setCurrentWidget(sunnypilotScreen);
}

void LateralPanel::updateToggles(bool _offroad) {
  bool torque_allowed = true;
  auto cp_bytes = params.get("CarParamsPersistent");
  auto cp_sp_bytes = params.get("CarParamsSPPersistent");
  if (!cp_bytes.empty() && !cp_sp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    AlignedBuffer aligned_buf_sp;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    capnp::FlatArrayMessageReader cmsg_sp(aligned_buf_sp.align(cp_sp_bytes.data(), cp_sp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();
    cereal::CarParamsSP::Reader CP_SP = cmsg_sp.getRoot<cereal::CarParamsSP>();

    if (madsLimitedSettings(CP, CP_SP)) {
      madsToggle->setDescription(descriptionBuilder(STATUS_MADS_SETTINGS_LIMITED_COMPATIBILITY, MADS_BASE_DESC));
    } else {
      madsToggle->setDescription(descriptionBuilder(STATUS_MADS_SETTINGS_FULL_COMPATIBILITY, MADS_BASE_DESC));
    }

    if (CP.getSteerControlType() == cereal::CarParams::SteerControlType::ANGLE) {
      params.remove("EnforceTorqueControl");
      torque_allowed = false;
    }
  } else {
    madsToggle->setDescription(descriptionBuilder(STATUS_MADS_CHECK_COMPATIBILITY, MADS_BASE_DESC));

    params.remove("EnforceTorqueControl");
    torque_allowed = false;
  }

  madsToggle->setEnabled(_offroad);
  madsSettingsButton->setEnabled(madsToggle->isToggled());

  torqueLateralControlToggle->setEnabled(_offroad && torque_allowed && !nnlcToggle->isToggled());
  torqueLateralControlSettingsButton->setEnabled(torqueLateralControlToggle->isToggled());

  blinkerPauseLateralSettings->refresh();

  offroad = _offroad;
}
