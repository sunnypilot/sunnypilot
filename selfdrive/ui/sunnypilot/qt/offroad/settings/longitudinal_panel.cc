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
  QVBoxLayout* vlayout = new QVBoxLayout(cruisePanelScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  cruisePanelScroller = new ScrollViewSP(list, this);
  vlayout->addWidget(cruisePanelScroller);

  slcControl = new SpeedLimitControl(
    "SpeedLimitControl",
    tr("Speed Limit Control (SLC)"),
    tr("When you engage ACC, you will be prompted to set the cruising speed to the speed limit of the road adjusted by the Offset and Source Policy specified, or the current driving speed. "
      "The maximum cruising speed will always be the MAX set speed."),
    "",
    this);
  list->addItem(slcControl);
  connect(slcControl, &SpeedLimitControl::toggleFlipped, this, &LongitudinalPanel::refresh);
  connect(slcControl, &SpeedLimitControl::slcWarningButtonClicked, this, &LongitudinalPanel::handleSlcWarningButtonClick);
  connect(slcControl, &SpeedLimitControl::slcSourceButtonClicked, this, &LongitudinalPanel::handleSLCSourceButtonClick);

  slcWarningScreen = new SpeedLimitControlWarning(this);
  connect(slcWarningScreen, &SpeedLimitControlWarning::backPress, this, &LongitudinalPanel::handleSLCBackButtonClick);
  slcSourceScreen = new SpeedLimitControlSource(this);
  connect(slcSourceScreen, &SpeedLimitControlSource::backPress, this, &LongitudinalPanel::handleSLCBackButtonClick);


  main_layout->addWidget(cruisePanelScreen);
  main_layout->addWidget(slcWarningScreen);
  main_layout->addWidget(slcSourceScreen);
  main_layout->setCurrentWidget(cruisePanelScreen);
}

void LongitudinalPanel::handleSlcWarningButtonClick() {
  main_layout->setCurrentWidget(slcWarningScreen);
}

void LongitudinalPanel::handleSLCSourceButtonClick() {
  main_layout->setCurrentWidget(slcSourceScreen);
}

void LongitudinalPanel::handleSLCBackButtonClick() {
  main_layout->setCurrentWidget(cruisePanelScreen);
}

void LongitudinalPanel::showEvent(QShowEvent *event) {
  main_layout->setCurrentWidget(cruisePanelScreen);
  refresh();
}

void LongitudinalPanel::refresh() {
  slcControl->refresh();
}
