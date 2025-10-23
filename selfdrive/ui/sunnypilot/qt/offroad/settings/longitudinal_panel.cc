/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal_panel.h"

#include "selfdrive/ui/sunnypilot/qt/util.h"

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
    "",
    "",
    this
  );
  QObject::connect(intelligentCruiseButtonManagement, &ParamControlSP::toggleFlipped, this, [=](bool) {
    refresh(offroad);
  });
  list->addItem(intelligentCruiseButtonManagement);

  dynamicExperimentalControl = new ParamControlSP(
    "DynamicExperimentalControl",
    tr("Dynamic Experimental Control (DEC)"),
    tr("Enable toggle to allow the model to determine when to use sunnypilot ACC or sunnypilot End to End Longitudinal."),
    "",
    this
  );
  list->addItem(dynamicExperimentalControl);

  SmartCruiseControlVision = new ParamControl(
    "SmartCruiseControlVision",
    tr("Smart Cruise Control - Vision"),
    tr("Use vision path predictions to estimate the appropriate speed to drive through turns ahead."),
    "");
  list->addItem(SmartCruiseControlVision);

  SmartCruiseControlMap = new ParamControl(
    "SmartCruiseControlMap",
    tr("Smart Cruise Control - Map"),
    tr("Use map data to estimate the appropriate speed to drive through turns ahead."),
    "");
  list->addItem(SmartCruiseControlMap);

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

void LongitudinalPanel::hideEvent(QHideEvent *event) {
  main_layout->setCurrentWidget(cruisePanelScreen);
}

void LongitudinalPanel::refresh(bool _offroad) {
  const QString icbm_description = tr("When enabled, sunnypilot will attempt to manage the built-in cruise control buttons by emulating button presses for limited longitudinal control.");

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
    has_icbm = hasIntelligentCruiseButtonManagement(CP_SP);

    if (CP_SP.getIntelligentCruiseButtonManagementAvailable() && !has_longitudinal_control) {
      intelligentCruiseButtonManagement->setEnabled(offroad);
      intelligentCruiseButtonManagement->setDescription(icbm_description);
    } else {
      params.remove("IntelligentCruiseButtonManagement");
      intelligentCruiseButtonManagement->setEnabled(false);

      const QString icbm_unavaialble = tr("Intelligent Cruise Button Management is currently unavailable on this platform.");

      QString long_desc = icbm_unavaialble;
      if (has_longitudinal_control) {
        if (CP.getAlphaLongitudinalAvailable()) {
          long_desc = icbm_unavaialble + " " + tr("Disable the openpilot Longitudinal Control (alpha) toggle to allow Intelligent Cruise Button Management.");
        } else {
          long_desc = icbm_unavaialble + " " + tr("openpilot Longitudinal Control is the default longitudinal control for this platform.");
        }
      }

      intelligentCruiseButtonManagement->setDescription("<b>" + long_desc + "</b><br><br>" + icbm_description);
      intelligentCruiseButtonManagement->showDescription();
    }

    if (has_longitudinal_control || has_icbm) {
      // enable Custom ACC Increments when long is available and is not PCM cruise
      customAccIncrement->setEnabled(((has_longitudinal_control && !is_pcm_cruise) || has_icbm) && offroad);
      dynamicExperimentalControl->setEnabled(has_longitudinal_control);
      SmartCruiseControlVision->setEnabled(true);
      SmartCruiseControlMap->setEnabled(true);
    } else {
      params.remove("CustomAccIncrementsEnabled");
      params.remove("DynamicExperimentalControl");
      params.remove("SmartCruiseControlVision");
      params.remove("SmartCruiseControlMap");
      customAccIncrement->setEnabled(false);
      dynamicExperimentalControl->setEnabled(false);
      SmartCruiseControlVision->setEnabled(false);
      SmartCruiseControlMap->setEnabled(false);
    }

    intelligentCruiseButtonManagement->refresh();
    customAccIncrement->refresh();
    dynamicExperimentalControl->refresh();
    SmartCruiseControlVision->refresh();
    SmartCruiseControlMap->refresh();
  } else {
    has_longitudinal_control = false;
    is_pcm_cruise = false;
    has_icbm = false;
    intelligentCruiseButtonManagement->setDescription("<b>" + tr("Start the vehicle to check vehicle compatibility.") + "</br><b><b>" + icbm_description);
  }

  QString accEnabledDescription = tr("Enable custom Short & Long press increments for cruise speed increase/decrease.");
  QString accNoLongDescription = tr("This feature can only be used with openpilot longitudinal control enabled.");
  QString accPcmCruiseDisabledDescription = tr("This feature is not supported on this platform due to vehicle limitations.");
  QString onroadOnlyDescription = tr("Start the vehicle to check vehicle compatibility.");

  if (offroad) {
    customAccIncrement->setDescription(onroadOnlyDescription);
    customAccIncrement->showDescription();
  } else {
    if (has_longitudinal_control || has_icbm) {
      if (has_longitudinal_control && is_pcm_cruise) {
        customAccIncrement->setDescription(accPcmCruiseDisabledDescription);
        customAccIncrement->showDescription();
      } else {
        customAccIncrement->setDescription(accEnabledDescription);
      }
    } else {
      customAccIncrement->toggleFlipped(false);
      customAccIncrement->setDescription(accNoLongDescription);
      customAccIncrement->showDescription();
    }
  }

  offroad = _offroad;
}
