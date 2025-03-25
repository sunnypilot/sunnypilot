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

enum HyundaiLongTuneOption {
  Off = 0,
  LongTune = 1,
  EvenSmootherBraking = 2,
};

VehiclePanel::VehiclePanel(QWidget *parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);
  ListWidget *list = new ListWidget(this);

  vehicleScreen = new QWidget(this);
  QVBoxLayout *vlayout = new QVBoxLayout(vehicleScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  platformSelector = new PlatformSelector();
  list->addItem(platformSelector);

  QObject::connect(uiState(), &UIState::offroadTransition, this, [=](bool offroad_transition) {
    offroad = offroad_transition;
    updatePanel(offroad);
    updateCarToggles();
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
    tr("Select a tuning mode. 'Off' means no custom tuning is applied. "
       "'Long Tune' is a dynamic acceleration/brake tune individualized to your car. "
       "'Tune + Smoother Braking' is the dynamic tuning with even smoother braking."),
       "../assets/offroad/icon_shell.png",
    tuning_buttons
  );
  hkgtuningToggle->showDescription();
  hkgtuningToggle->setProperty("originalDesc", hkgtuningToggle->getDescription());

  connect(hkgtuningToggle, &ButtonParamControlSP::buttonToggled, this, [=](int index) {
    hkg_state = index;
    params.put("HyundaiLongTune", QString::number(index).toStdString());
    params.putBool("HyundaiSmootherBraking", index == EvenSmootherBraking);
    updateCarToggles();
  });

  // Add the tuning toggle to the layout
  vlayout->addWidget(hkgtuningToggle);

  // Add the vehicle screen to the main layout
  main_layout->addWidget(vehicleScreen);
}

void VehiclePanel::showEvent(QShowEvent *event) {
  QFrame::showEvent(event);
  updatePanel(offroad);
  updateCarToggles();
}

void VehiclePanel::updatePanel(bool _offroad) {
  platformSelector->refresh(_offroad);
  offroad = _offroad;
}

void VehiclePanel::updateCarToggles() {
  bool openpilotLong = params.getBool("ExperimentalLongitudinalEnabled");
  QString brand = platformSelector->getPlatformBundle("brand").toString();

  if (brand == "hyundai") {
    hkgtuningToggle->setVisible(true);
    // Set enabled state/description based on openpilotLong
    hkgtuningToggle->setEnabled(openpilotLong);
    hkgtuningToggle->setDescription(openpilotLong ?
      hkgtuningToggle->property("originalDesc").toString() :
      tr("Enable openpilot longitudinal control first."));
    // If not enabled, show disabled description.
    if (!openpilotLong) {
      hkgtuningToggle->showDescription();
      return;
    }
    int tuningOption = QString::fromStdString(params.get("HyundaiLongTune")).toInt();
    hkg_state = tuningOption;  // Off=0, LongTune=1, EvenSmootherBraking=2
    hkgtuningToggle->setCheckedButton(hkg_state);
    hkgtuningToggle->showDescription();
  } else {
    // Hide toggle if not hyundai.
    params.put("HyundaiLongTune", "0");
    params.putBool("HyundaiSmootherBraking", false);
    hkgtuningToggle->setVisible(false);
  }
}
