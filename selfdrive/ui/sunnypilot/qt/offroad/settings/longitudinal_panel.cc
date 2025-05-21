/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal_panel.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/dab_settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

LongitudinalPanel::LongitudinalPanel(QWidget *parent) : QWidget(parent) {
  // Use QStackedLayout for better transitions
  main_layout = new QStackedLayout(this);
  main_layout->setContentsMargins(0, 0, 0, 0);

  // Create main screen
  mainScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(mainScreen);
  vlayout->setContentsMargins(0, 0, 0, 0);

  ListWidgetSP *list = new ListWidgetSP(this);
  list->setContentsMargins(0, 0, 0, 0);
  list->setSpacing(0);

  // Custom ACC Increment
  customAccIncrement = new CustomAccIncrement("CustomAccIncrementsEnabled", "Custom ACC Speed Increments", "Enable custom Short & Long press increments for cruise speed increase/decrease.", "", this);
  list->addItem(customAccIncrement);

  // Add vertical spacing
  list->addItem(vertical_space());
  list->addItem(horizontal_line());
  list->addItem(vertical_space());

  // DAB toggle
  dabToggle = new ParamControl(
    "DynamicAcceleration",
    tr("Dynamic Acceleration Boost (DAB)"),
    tr("Enable acceleration boost based on driving conditions."),
    "");
  dabToggle->setConfirmation(true, false);
  list->addItem(dabToggle);

  // DAB Settings button
  dabSettingsButton = new PushButtonSP(tr("Customize DAB"));
  dabSettingsButton->setObjectName("dab_btn");
  connect(dabSettingsButton, &QPushButton::clicked, [=]() {
    mainScroller->setLastScrollPosition();
    main_layout->setCurrentWidget(dabWidget);
  });
  QObject::connect(dabToggle, &ToggleControl::toggleFlipped, dabSettingsButton, &PushButtonSP::setEnabled);
  list->addItem(dabSettingsButton);

  // Set up main screen scrolling
  mainScroller = new ScrollViewSP(list, this);
  vlayout->addWidget(mainScroller);

  // Create DAB settings widget
  dabWidget = new DabSettings(this);
  connect(dabWidget, &DabSettings::backPress, [=]() {
    mainScroller->restoreScrollPosition();
    main_layout->setCurrentWidget(mainScreen);
  });

  // Add both widgets to the stacked layout
  main_layout->addWidget(mainScreen);
  main_layout->addWidget(dabWidget);

  // Set default to main screen
  main_layout->setCurrentWidget(mainScreen);

  // Initialize button state
  dabSettingsButton->setEnabled(dabToggle->isToggled());
}
