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

  std::vector<QString> tuning_buttons { tr("Off"), tr("Dynamic"), tr("Predictive") };
  hyundaiLongitudinalTuningToggle = new ButtonParamControlSP(
    "HyundaiLongitudinalTuning",
    tr("Custom Longitudinal Tuning"),
    tr("Select a tuning mode.\n"
       "Off: no custom tuning applied.\n"
       "Dynamic: on-the-spot adjustments using dynamic calculations.\n"
       "Predictive: adjusts based on anticipated ACC variation."),
       "../assets/offroad/icon_shell.png",
    tuning_buttons
  );
  hyundaiLongitudinalTuningToggle->showDescription();
  hyundaiLongitudinalTuningToggle->setProperty("originalDesc", hyundaiLongitudinalTuningToggle->getDescription());

  for (auto btn : hyundaiLongitudinalTuningToggle->findChildren<QPushButton*>()) {
    btn->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
  }

  connect(hyundaiLongitudinalTuningToggle, &ButtonParamControlSP::buttonToggled, this, [=](int index) {
    hkg_state = index;
    params.put("HyundaiLongitudinalTuning", QString::number(index).toStdString());
    updateCarToggles();
  });
  // Add the tuning toggle to the layout
  vlayout->addWidget(hyundaiLongitudinalTuningToggle);

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
    return tr("Enable openpilot longitudinal control first.");
  }
  return QString();
}

void VehiclePanel::updateCarToggles() {
  bool openpilotLong = params.getBool("AlphaLongitudinalEnabled");
  QString brand = platformSelector->getPlatformBundle("brand").toString();

  if (brand == "hyundai") {
    hyundaiLongitudinalTuningToggle->setVisible(true);
    QString msg = toggleDisableMsg(openpilotLong);
    if (!msg.isEmpty()) {
      hyundaiLongitudinalTuningToggle->setEnabled(false);
      hyundaiLongitudinalTuningToggle->setDescription(msg);
      hyundaiLongitudinalTuningToggle->showDescription();
      return;
    }
    hyundaiLongitudinalTuningToggle->setEnabled(true);
    hyundaiLongitudinalTuningToggle->setDescription(hyundaiLongitudinalTuningToggle->property("originalDesc").toString());

    int tuningOption = QString::fromStdString(params.get("HyundaiLongitudinalTuning")).toInt();
    hkg_state = tuningOption;
    hyundaiLongitudinalTuningToggle->setCheckedButton(hkg_state);
    hyundaiLongitudinalTuningToggle->showDescription();
  } else {
    // Hide toggle if not hyundai.
    params.put("HyundaiLongitudinalTuning", "0");
    hyundaiLongitudinalTuningToggle->setVisible(false);
  }
}
