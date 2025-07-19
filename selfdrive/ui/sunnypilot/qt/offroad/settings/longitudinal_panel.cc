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

  customAccIncrement = new CustomAccIncrement("CustomAccIncrementsEnabled", tr("Custom ACC Speed Increments"), "", "", this);
  list->addItem(customAccIncrement);

  QObject::connect(uiState(), &UIState::offroadTransition, this, &LongitudinalPanel::refresh);


  // Vibe Personality Controller
  vibePersonalityControl = new ParamControlSP("VibePersonalityEnabled",
    tr("Vibe Personality Controller"),
    tr("Advanced driving personality system with separate controls for acceleration behavior (Eco/Normal/Sport) and following distance/braking (Relaxed/Standard/Aggressive). "
      "Customize your driving experience with independent acceleration and distance personalities."),
    "../assets/offroad/icon_shell.png");
  list->addItem(vibePersonalityControl);

  connect(vibePersonalityControl, &ParamControlSP::toggleFlipped, [=]() {
    refresh(offroad);
  });

  // Vibe Acceleration Personality
  vibeAccelPersonalityControl = new ParamControlSP("VibeAccelPersonalityEnabled",
    tr("Acceleration Personality"),
    tr("Controls acceleration behavior: Eco (efficient), Normal (balanced), Sport (responsive). "
      "Adjust how aggressively the vehicle accelerates while maintaining smooth operation."),
    "../assets/offroad/icon_shell.png");
  list->addItem(vibeAccelPersonalityControl);

  // Vibe Following Distance Personality
  vibeFollowPersonalityControl = new ParamControlSP("VibeFollowPersonalityEnabled",
    tr("Following Distance Personality"),
    tr("Controls following distance and braking behavior: Relaxed (longer distance, gentler braking), Standard (balanced), Aggressive (shorter distance, firmer braking). "
      "Fine-tune your comfort level in traffic situations."),
    "../assets/offroad/icon_shell.png");
  list->addItem(vibeFollowPersonalityControl);

  main_layout->addWidget(cruisePanelScreen);
  main_layout->setCurrentWidget(cruisePanelScreen);
  refresh(offroad);
}

void LongitudinalPanel::showEvent(QShowEvent *event) {
  main_layout->setCurrentWidget(cruisePanelScreen);
  refresh(offroad);
}

void LongitudinalPanel::refresh(bool _offroad) {
  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    has_longitudinal_control = hasLongitudinalControl(CP);
    is_pcm_cruise = CP.getPcmCruise();
  } else {
    has_longitudinal_control = false;
    is_pcm_cruise = false;
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
  bool vibePersonalityEnabled = params.getBool("VibePersonalityEnabled");
  if (vibePersonalityEnabled) {
    vibeAccelPersonalityControl->setVisible(true);
    vibeFollowPersonalityControl->setVisible(true);
  } else {
    vibeAccelPersonalityControl->setVisible(false);
    vibeFollowPersonalityControl->setVisible(false);
  }

  // enable toggle when long is available and is not PCM cruise
  customAccIncrement->setEnabled(has_longitudinal_control && !is_pcm_cruise && !offroad);
  customAccIncrement->refresh();

  // Vibe Personality controls - always enabled for toggling
  vibePersonalityControl->setEnabled(true);
  vibeAccelPersonalityControl->setEnabled(true);
  vibeFollowPersonalityControl->setEnabled(true);
  vibePersonalityControl->refresh();
  vibeAccelPersonalityControl->refresh();
  vibeFollowPersonalityControl->refresh();

  offroad = _offroad;
}
