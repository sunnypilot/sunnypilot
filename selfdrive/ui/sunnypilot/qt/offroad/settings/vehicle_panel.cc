/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle_panel.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"
#include <QPushButton>
#include <QSizePolicy>

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

  std::vector<QString> tuning_buttons { tr("Off"), tr("Dynamic"), tr("Future Lookahead") };
  hkgtuningToggle = new ButtonParamControlSP(
    "HyundaiLongTune",
    tr("Custom Longitudinal Tuning"),
    tr("Select a tuning mode.\n"
       "'Off' means no custom tuning is applied. \n"
       "'Dynamic' Emphasizes on-the-spot adjustments using dynamic calculations. \n"
       "'Future Lookahead' Focuses on predicting and adjusting based on anticipated jerk."),
       "../assets/offroad/icon_shell.png",
    tuning_buttons
  );
  hkgtuningToggle->showDescription();
  hkgtuningToggle->setProperty("originalDesc", hkgtuningToggle->getDescription());

  for (auto btn : hkgtuningToggle->findChildren<QPushButton*>()) {
    btn->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
  }

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
  updatePanel(offroad);
  updateCarToggles();
}

void VehiclePanel::updatePanel(bool _offroad) {
  platformSelector->refresh(_offroad);
  offroad = _offroad;
}

QString VehiclePanel::toggleDisableMsg(bool openpilotLong) const {
  if (!offroad) {
    return tr("Enable 'Always Offroad' in device panel, or turn vehicle off to activate this toggle");
  }
  if (!openpilotLong) {
    return tr("Enable sunnypilot longitudinal control first.");
  }
  return QString();
}

void VehiclePanel::updateCarToggles() {
  bool openpilotLong = params.getBool("ExperimentalLongitudinalEnabled");
  QString brand = platformSelector->getPlatformBundle("brand").toString();

  if (brand == "hyundai") {
    hkgtuningToggle->setVisible(true);
    QString msg = toggleDisableMsg(openpilotLong);
    if (!msg.isEmpty()) {
      hkgtuningToggle->setEnabled(false);
      hkgtuningToggle->setDescription(msg);
      hkgtuningToggle->showDescription();
      return;
    }
    hkgtuningToggle->setEnabled(true);
    hkgtuningToggle->setDescription(hkgtuningToggle->property("originalDesc").toString());

    int tuningOption = QString::fromStdString(params.get("HyundaiLongTune")).toInt();
    hkg_state = tuningOption;
    hkgtuningToggle->setCheckedButton(hkg_state);
    hkgtuningToggle->showDescription();
  } else {
    // Hide toggle if not hyundai.
    params.put("HyundaiLongTune", "0");
    params.putBool("HyundaiSmootherBraking", false);
    hkgtuningToggle->setVisible(false);
  }
}
