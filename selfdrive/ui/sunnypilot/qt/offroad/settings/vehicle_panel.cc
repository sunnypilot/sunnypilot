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

  std::vector<QString> tuning_buttons { tr("Off"), tr("Long Tune"), tr("Tune + Even Smoother Braking") };
  hkgtuningToggle = new ButtonParamControlSP(
    "HyundaiLongTune",
    tr("HKG Custom Longitudinal Tuning"),
    tr("Select a tuning mode. 'Off' means there is no custom tuning is currently applied. "
       "'Long Tune' is a dynamic acceleration/brake tune individualized to your specific car. "
       "'Tune + Smoother Braking' is the dynamic tuning but with even smoother braking applied."),
       "../assets/offroad/icon_shell.png",
    tuning_buttons
  );
  hkgtuningToggle->showDescription();
  hkgtuningToggle->setProperty("originalDesc", hkgtuningToggle->getDescription());

  connect(hkgtuningToggle, &ButtonParamControlSP::buttonToggled, this, [=](int index) {
    hkg_state = index;
    // Inline update of tuning and braking params
    params.put("HyundaiLongTune", QString::number(index).toStdString());
    params.put("HyundaiSmootherBraking", (index == 2) ? "1" : "0");
    updateCarToggles();
  });

  // Add the tuning toggle to the layout
  vlayout->addWidget(hkgtuningToggle);

  // Add the vehicle screen to the main layout
  main_layout->addWidget(vehicleScreen);
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
    return ToggleState::ENABLED;
  }
  return ToggleState::DISABLED_DRIVING;
}

void VehiclePanel::updateToggleState(AbstractControlSP* toggle, bool hasOpenpilotLong) {
  static const QString LONGITUDINAL_MSG = tr("Enable openpilot longitudinal control first.");
  static const QString DRIVING_MSG = tr("Cannot modify while driving. Please go offroad mode first.");

  ToggleState state = getToggleState(hasOpenpilotLong);

  switch (state) {
    case ToggleState::ENABLED:
      toggle->setDescription(toggle->property("originalDesc").toString());
      break;
    case ToggleState::DISABLED_LONGITUDINAL: {
      QString msg = "<font color='orange'>" + tr("Enable openpilot longitudinal control first to modify this setting.") + "</font>";
      toggle->setDescription(msg);
      toggle->showDescription();
      break;
    }
    case ToggleState::DISABLED_DRIVING: {
      QString msg = "<font color='orange'>" + tr("Cannot modify while driving. Please go offroad mode first.") + "</font>";
      toggle->setDescription(msg);
      toggle->showDescription();
      break;
    }
  }
}

void VehiclePanel::handleToggleAction(AbstractControlSP* toggle, bool checked) {
  bool hasOpenpilotLong = params.getBool("ExperimentalLongitudinalEnabled");

  // Only apply changes if all conditions are met
  toggle->setEnabled(true);
  params.putBool(toggle->objectName().toStdString(), checked);
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

  if (brand == "hyundai") {
    hkgtuningToggle->setVisible(true);
    hkgtuningToggle->setEnabled(true);
    QString tuning = QString::fromStdString(params.get("HyundaiLongTune"));
    QString braking = QString::fromStdString(params.get("HyundaiSmootherBraking"));
    hkg_state = (tuning == "2") ? 2 : ((tuning == "1") ? ((braking == "1") ? 2 : 1) : 0);
    updateToggleState(hkgtuningToggle, hasOpenpilotLong);
    hkgtuningToggle->setCheckedButton(hkg_state);
    hkgtuningToggle->setDescription(hkgtuningToggle->property("originalDesc").toString());
    hkgtuningToggle->showDescription();
  } else {
    // Reset if not Hyundai
    params.put("HyundaiLongTune", "0");
    params.put("HyundaiSmootherBraking", "0");
    hkgtuningToggle->setVisible(false);
  }
}
