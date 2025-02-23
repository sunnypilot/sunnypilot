/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle_panel.h"
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include "common/util.h"

#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

VehiclePanel::VehiclePanel(QWidget *parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);
  ListWidget *list = new ListWidget(this);

  vehicleScreen = new QWidget(this);
  QVBoxLayout *vlayout = new QVBoxLayout(vehicleScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  platformSelector = new PlatformSelector();
  list->addItem(platformSelector);

  QObject::connect(uiState(), &UIState::offroadTransition, this, [=](bool offroad_transition) {
    updateToggles(offroad_transition);
    updatePanel(offroad_transition);
  });

  ScrollViewSP *scroller = new ScrollViewSP(list, this);
  vlayout->addWidget(scroller);

  QObject::connect(platformSelector, &PlatformSelector::clicked, [=]() {
    QTimer::singleShot(100, this, &VehiclePanel::updateCarToggles);
  });

  hkgtuningToggle = new ParamControlSP("HKGtuning",
                               tr("Chubbs Tune"),
                               tr("Enable to experience enhanced vehicle performance tuning"),
                               "../assets/offroad/icon_shell.png",
                               this);
  hkgtuningToggle->setObjectName("HKGtuning");
  list->addItem(hkgtuningToggle);
  connect(hkgtuningToggle, &ToggleControlSP::toggleFlipped, this, [=](bool checked) {
    handleToggleAction(hkgtuningToggle, checked);
  });
  if (!hkgtuningToggle->layout()) {
    QHBoxLayout *hlayout = new QHBoxLayout();
    hlayout->setContentsMargins(0, 0, 0, 0); // adjust margins if needed
    hkgtuningToggle->setLayout(hlayout);
  }
  QPushButton *brakingButton = new QPushButton(tr("Smoother Braking"), hkgtuningToggle);
  brakingButton->setObjectName("brakingButton");
  brakingButton->setSizePolicy(QSizePolicy::Maximum, QSizePolicy::Preferred);
  hkgtuningToggle->layout()->addWidget(brakingButton);
  connect(brakingButton, &QPushButton::clicked, this, [=]() {
    params.putBool("HKGBraking", true);
    brakingButton->setEnabled(false);
  });

  main_layout->addWidget(vehicleScreen);
  main_layout->setCurrentWidget(vehicleScreen);
}

void VehiclePanel::showEvent(QShowEvent *event) {
  updatePanel(offroad);
}

void VehiclePanel::updatePanel(bool _offroad) {
  platformSelector->refresh(_offroad);
  offroad = _offroad;
}

void VehiclePanel::updateToggles(bool offroad_transition) {
  updatePanel(offroad_transition);
  updateCarToggles();
}

VehiclePanel::ToggleState VehiclePanel::getToggleState(bool hasOpenpilotLong) const {
  if (!hasOpenpilotLong) {
    return ToggleState::DISABLED_LONGITUDINAL;
  }
  if (!uiState()->scene.started) {
    return ToggleState::DISABLED_DRIVING;
  }
  return ToggleState::ENABLED;
}

void VehiclePanel::updateToggleState(ParamControlSP* toggle, bool hasOpenpilotLong) {
  static const QString LONGITUDINAL_MSG = tr("Enable openpilot longitudinal control first.");
  static const QString DRIVING_MSG = tr("Cannot modify while driving. Please go offroad mode first.");

  ToggleState state = getToggleState(hasOpenpilotLong);

  switch (state) {
    case ToggleState::ENABLED:
      // Removed use of getTitle; leave description unchanged.
      // toggle->setDescription(toggle->getTitle() + ": " + toggle->getDescription());
      break;
    case ToggleState::DISABLED_LONGITUDINAL: {
      QString msg = "<font color='orange'>" + tr("Enable openpilot longitudinal control first to modify this setting.") + "</font>";
      toggle->setDescription(msg);
      toggle->showDescription();
      QTimer::singleShot(5000, toggle, &ParamControlSP::hideDescription);
      break;
    }
    case ToggleState::DISABLED_DRIVING: {
      QString msg = "<font color='orange'>" + tr("Cannot modify while driving. Please go offroad mode first.") + "</font>";
      toggle->setDescription(msg);
      toggle->showDescription();
      QTimer::singleShot(5000, toggle, &ParamControlSP::hideDescription);
      break;
    }
  }
}

void VehiclePanel::handleToggleAction(ParamControlSP* toggle, bool checked) {
  bool hasOpenpilotLong = params.getBool("ExperimentalLongitudinalEnabled");
  // Introduce a tuning key variable
  const std::string tuningKey = toggle->objectName().toStdString();

  // First check if we're allowed to make changes
  if (!offroad || !hasOpenpilotLong) {
    // Revert the toggle state
    toggle->setEnabled(false);
    toggle->setValue(QString::number(params.getBool(tuningKey)));
    if (!offroad) {
      QString msg = "<font color='orange'>" + tr("Cannot modify while driving. Please go offroad first.") + "</font>";
      toggle->setDescription(msg);
    } else if (!hasOpenpilotLong) {
      QString msg = "<font color='orange'>" + tr("Enable openpilot longitudinal control first.") + "</font>";
      toggle->setDescription(msg);
    }

    toggle->showDescription();
    QTimer::singleShot(5000, toggle, &ParamControlSP::hideDescription);
    return;
  }

  // Only apply changes if all conditions are met
  toggle->setEnabled(true);
  params.putBool(tuningKey, checked);
  updateToggleState(toggle, hasOpenpilotLong);
  updatePanel(offroad);
}

void VehiclePanel::updateCarToggles() {
  bool hasOpenpilotLong = params.getBool("ExperimentalLongitudinalEnabled");

  // Pre-stage vehicle information
  QString platform = platformSelector->getPlatformBundle("platform").toString();
  QString brand = platformSelector->getPlatformBundle("brand").toString();
  QString make = platformSelector->getPlatformBundle("make").toString();
  QString model = platformSelector->getPlatformBundle("model").toString();

  // Default state - no car selected
  hkgtuningToggle->setVisible(false);

  if (brand == "hyundai") {
    hkgtuningToggle->setVisible(true);
    hkgtuningToggle->setEnabled(offroad && hasOpenpilotLong);
    updateToggleState(hkgtuningToggle, hasOpenpilotLong);
    QPushButton *brakingButton = hkgtuningToggle->findChild<QPushButton*>("brakingButton");
    if (brakingButton) {
      brakingButton->setVisible(params.getBool("HKGtuning"));
    }
  } else {
    // Introduce the tuning key variable for clarity
    const std::string tuningKey = hkgtuningToggle->objectName().toStdString();
    if (params.getBool(tuningKey)) {
      params.putBool(tuningKey, false);
    }
  }
}
