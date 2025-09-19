/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal_panel.h"

LongitudinalPanel::LongitudinalPanel(QWidget *parent) : QWidget(parent) {
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

  main_layout = new QStackedLayout(this);
  ListWidget *list = new ListWidget(this, false);

  cruisePanelScreen = new QWidget(this);
  QVBoxLayout *vlayout = new QVBoxLayout(cruisePanelScreen);
  vlayout->setContentsMargins(0, 0, 0, 0);

  cruisePanelScroller = new ScrollViewSP(list, this);
  vlayout->addWidget(cruisePanelScroller);

  intelligentCruiseButtonManagement = new ParamControlSP(
    "IntelligentCruiseButtonManagement",
    tr("Intelligent Cruise Button Management (ICBM) (Alpha)"),
    tr("When enabled, sunnypilot will attempt to manage the built-in cruise control buttons by emulating button presses for limited longitudinal control."),
    "",
    this
  );
  intelligentCruiseButtonManagement->setConfirmation(true, false);
  list->addItem(intelligentCruiseButtonManagement);

  SmartCruiseControlVision = new ParamControl(
    "SmartCruiseControlVision",
    tr("Smart Cruise Control - Vision"),
    tr("Use vision path predictions to estimate the appropriate speed to drive through turns ahead."),
    "");
  list->addItem(SmartCruiseControlVision);

  customAccIncrement = new CustomAccIncrement("CustomAccIncrementsEnabled", tr("Custom ACC Speed Increments"), "", "", this);
  list->addItem(customAccIncrement);

  QObject::connect(uiState(), &UIState::offroadTransition, this, &LongitudinalPanel::refresh);

  speedLimitSettings = new PushButtonSP(tr("Speed Limit"), 750, this);
  connect(speedLimitSettings, &QPushButton::clicked, [&]() {
    cruisePanelScroller->setLastScrollPosition();
    main_layout->setCurrentWidget(speedLimitScreen);
  });
  list->addItem(speedLimitSettings);

  speedLimitScreen = new SpeedLimitSettings(this);
  connect(speedLimitScreen, &SpeedLimitSettings::backPress, [=]() {
    cruisePanelScroller->restoreScrollPosition();
    main_layout->setCurrentWidget(cruisePanelScreen);
  });

  main_layout->addWidget(cruisePanelScreen);
  main_layout->addWidget(speedLimitScreen);
  main_layout->setCurrentWidget(cruisePanelScreen);
  refresh(offroad);
}

void LongitudinalPanel::showEvent(QShowEvent *event) {
  main_layout->setCurrentWidget(cruisePanelScreen);
  refresh(offroad);
}

void LongitudinalPanel::refresh(bool _offroad) {
  auto cp_bytes = params.get("CarParamsPersistent");
  auto cp_sp_bytes = params.get("CarParamsSPPersistent");
  if (!cp_bytes.empty() && !cp_sp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    AlignedBuffer aligned_buf_sp;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    capnp::FlatArrayMessageReader cmsg_sp(aligned_buf_sp.align(cp_sp_bytes.data(), cp_sp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();
    cereal::CarParamsSP::Reader CP_SP = cmsg_sp.getRoot<cereal::CarParamsSP>();

    has_longitudinal_control = hasLongitudinalControl(CP);
    is_pcm_cruise = CP.getPcmCruise();
    intelligent_cruise_button_management_available = CP_SP.getIntelligentCruiseButtonManagementAvailable();
  } else {
    has_longitudinal_control = false;
    is_pcm_cruise = false;
    intelligent_cruise_button_management_available = false;
  }

  QString accEnabledDescription = tr("Enable custom Short & Long press increments for cruise speed increase/decrease.");
  QString accNoLongDescription = tr("This feature can only be used with openpilot longitudinal control enabled.");
  QString accPcmCruiseDisabledDescription = tr("This feature is not supported on this platform due to vehicle limitations.");
  QString onroadOnlyDescription = tr("Start the vehicle to check vehicle compatibility.");

  if (offroad) {
    customAccIncrement->setDescription(onroadOnlyDescription);
    customAccIncrement->showDescription();
  } else {
    if (has_longitudinal_control || intelligent_cruise_button_management_available) {
      if (is_pcm_cruise) {
        customAccIncrement->setDescription(accPcmCruiseDisabledDescription);
        customAccIncrement->showDescription();
      } else {
        customAccIncrement->setDescription(accEnabledDescription);
      }
    } else {
      params.remove("CustomAccIncrementsEnabled");
      customAccIncrement->toggleFlipped(false);
      customAccIncrement->setDescription(accNoLongDescription);
      customAccIncrement->showDescription();
      params.remove("IntelligentCruiseButtonManagement");
      intelligentCruiseButtonManagement->toggleFlipped(false);
    }
  }

  bool icbm_allowed = intelligent_cruise_button_management_available && !has_longitudinal_control;
  intelligentCruiseButtonManagement->setEnabled(icbm_allowed && offroad);

  // enable toggle when long is available and is not PCM cruise
  bool cai_allowed = (has_longitudinal_control && !is_pcm_cruise) || icbm_allowed;
  customAccIncrement->setEnabled(cai_allowed && !offroad);
  customAccIncrement->refresh();

  SmartCruiseControlVision->setEnabled(has_longitudinal_control || icbm_allowed);

  offroad = _offroad;
}
