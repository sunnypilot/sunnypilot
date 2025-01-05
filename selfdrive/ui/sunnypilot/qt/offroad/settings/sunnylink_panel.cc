/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnylink_panel.h"

#include "selfdrive/ui/sunnypilot/qt/util.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

SunnylinkPanel::SunnylinkPanel(QWidget *parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);
  auto *list = new ListWidget(this, false);

  sunnylinkScreen = new QWidget(this);
  auto vlayout = new QVBoxLayout(sunnylinkScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  QString sunnylinkEnabledBtnDesc = tr("This is the master switch, it will allow you to cutoff any sunnylink requests should you want to do that.");
  sunnylinkEnabledBtn = new ParamControl(
    "SunnylinkEnabled",
    tr("Enable sunnylink"),
    sunnylinkEnabledBtnDesc,
    "");
  list->addItem(sunnylinkEnabledBtn);

  status_popup = new SunnylinkSponsorPopup(false, this);
  sponsorBtn = new ButtonControlSP(
    tr("Sponsor Status"), tr("SPONSOR"),
    tr("Become a sponsor of sunnypilot to get early access to sunnylink features when they become available."));
  list->addItem(sponsorBtn);
  connect(sponsorBtn, &ButtonControlSP::clicked, [=]() {
    status_popup->exec();
  });
  list->addItem(horizontal_line());

  pair_popup = new SunnylinkSponsorPopup(true, this);
  pairSponsorBtn = new ButtonControlSP(
    tr("Pair GitHub Account"), tr("PAIR"),
    tr("Pair your GitHub account to grant your device sponsor benefits, including API access on sunnylink.") + "🌟");
  list->addItem(pairSponsorBtn);
  connect(pairSponsorBtn, &ButtonControlSP::clicked, [=]() {
    if (getSunnylinkDongleId().value_or(tr("N/A")) == "N/A") {
      ConfirmationDialog::alert(tr("sunnylink Dongle ID not found. This may be due to weak internet connection or sunnylink registration issue. Please reboot and try again."), this);
    } else {
      pair_popup->exec();
    }
  });
  list->addItem(horizontal_line());

  connect(sunnylinkEnabledBtn, &ParamControl::showDescriptionEvent, [=]() {
    // resets the description to the default one for the Easter egg
    sunnylinkEnabledBtn->setDescription(sunnylinkEnabledBtnDesc);
  });

  connect(sunnylinkEnabledBtn, &ParamControl::toggleFlipped, [=](bool enabled) {
    QString description;
    if (enabled) {
      description = "<font color='SeaGreen'>"+ tr("🎉Welcome back! We're excited to see you've enabled sunnylink again! 🚀")+ "</font>";
    } else {
      description = "<font color='orange'>"+ tr("👋Not going to lie, it's sad to see you disabled sunnylink 😢, but we'll be here when you're ready to come back 🎉.")+ "</font>";
     
    }
    sunnylinkEnabledBtn->showDescription();
    sunnylinkEnabledBtn->setDescription(description);

    updatePanel(offroad);
  });

  QObject::connect(uiState(), &UIState::offroadTransition, this, &SunnylinkPanel::updatePanel);

  sunnylinkScroller = new ScrollViewSP(list, this);
  vlayout->addWidget(sunnylinkScroller);

  main_layout->addWidget(sunnylinkScreen);
}

void SunnylinkPanel::showEvent(QShowEvent *event) {
  updatePanel(offroad);
}

void SunnylinkPanel::updatePanel(bool _offroad) {
  QString sunnylink_device_id = tr("Device ID") + "  " + getSunnylinkDongleId().value_or(tr("N/A"));

  sunnylinkEnabledBtn->setEnabled(_offroad);

  if (sunnylinkEnabledBtn->isToggled()) {
    sunnylinkEnabledBtn->setValue(sunnylink_device_id);
  } else {
    sunnylinkEnabledBtn->setValue("");
  }

  offroad = _offroad;
}
