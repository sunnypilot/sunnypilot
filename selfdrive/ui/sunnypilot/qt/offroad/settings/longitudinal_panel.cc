/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal_panel.h"

LongitudinalPanel::LongitudinalPanel(QWidget *parent) : QWidget(parent) {
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
  list->addItem(intelligentCruiseButtonManagement);

  customAccIncrement = new CustomAccIncrement("CustomAccIncrementsEnabled", tr("Custom ACC Speed Increments"), "", "", this);
  list->addItem(customAccIncrement);

  QObject::connect(uiState(), &UIState::offroadTransition, this, &LongitudinalPanel::refresh);

  main_layout->addWidget(cruisePanelScreen);
  main_layout->setCurrentWidget(cruisePanelScreen);
  refresh(offroad);
}

void LongitudinalPanel::showEvent(QShowEvent *event) {
  main_layout->setCurrentWidget(cruisePanelScreen);
  refresh(offroad);
}

void LongitudinalPanel::refresh(bool _offroad) {
  auto alpha_longitudinal = params.getBool("AlphaLongitudinalEnabled");
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
    intelligent_cruise_button_management_available = true;
  }

  QString accEnabledDescription = tr("Enable custom Short & Long press increments for cruise speed increase/decrease.");
  QString accNoLongDescription = tr("This feature can only be used with openpilot longitudinal control enabled.");
  QString accPcmCruiseDisabledDescription = tr("This feature is not supported on this platform due to vehicle limitations.");
  QString onroadOnlyDescription = tr("Start the vehicle to check vehicle compatibility.");

  if (offroad) {
    customAccIncrement->setDescription(onroadOnlyDescription);
    customAccIncrement->showDescription();
  } else {
    if (has_longitudinal_control) {
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
    }
  }

  intelligentCruiseButtonManagement->setEnabled(intelligent_cruise_button_management_available && !alpha_longitudinal && !offroad);

  // enable toggle when long is available and is not PCM cruise
  customAccIncrement->setEnabled(has_longitudinal_control && !is_pcm_cruise && !offroad);
  customAccIncrement->refresh();

  offroad = _offroad;
}
