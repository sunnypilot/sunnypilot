/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle_settings.h"

#include "selfdrive/ui/sunnypilot/qt/util.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

VehiclePanel::VehiclePanel(QWidget *parent) : QWidget(parent) {
  main_layout = new QStackedLayout(this);
  home = new QWidget(this);
  QVBoxLayout* fcr_layout = new QVBoxLayout(home);
  fcr_layout->setContentsMargins(0, 20, 0, 20);

  set = QString::fromStdString(params.get("CarModelText"));
  setCarBtn = new QPushButton(((set == "=== Not Selected ===") || (set.length() == 0)) ? prompt_select : set);
  setCarBtn->setObjectName("setCarBtn");
  setCarBtn->setStyleSheet("margin-right: 30px;");
  connect(setCarBtn, &QPushButton::clicked, [=]() {
    QMap<QString, QString> cars = getCarNames();
    QString currentCar = QString::fromStdString(params.get("CarModel"));
    QString selection = MultiOptionDialog::getSelection(prompt_select, cars.keys(), cars.key(currentCar), this);
    if (!selection.isEmpty()) {
      params.put("CarModel", cars[selection].toStdString());
      params.put("CarModelText", selection.toStdString());
      ConfirmationDialog::alert(tr("Updating this setting takes effect when the car is powered off."), this);
    }
    updateToggles();
  });
  fcr_layout->addSpacing(10);
  fcr_layout->addWidget(setCarBtn, 0, Qt::AlignRight);
  fcr_layout->addSpacing(10);

  home_widget = new QWidget(this);
  QVBoxLayout* toggle_layout = new QVBoxLayout(home_widget);
  home_widget->setObjectName("homeWidget");

  ScrollViewSP *scroller = new ScrollViewSP(home_widget, this);
  scroller->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
  fcr_layout->addWidget(scroller, 1);

  main_layout->addWidget(home);

  setStyleSheet(R"(
    #setCarBtn {
      border-radius: 50px;
      font-size: 50px;
      font-weight: 500;
      height:100px;
      padding: 0 35 0 35;
      color: #E4E4E4;
      background-color: #393939;
    }
    #setCarBtn:pressed {
      background-color: #4a4a4a;
    }
  )");

  auto toggle_panel = new SPVehiclesTogglesPanel(this);
  toggle_layout->addWidget(toggle_panel);
}

void VehiclePanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void VehiclePanel::updateToggles() {
  if (!isVisible()) {
    return;
  }

  set = QString::fromStdString(params.get("CarModelText"));
  setCarBtn->setText(((set == "=== Not Selected ===") || (set.length() == 0)) ? prompt_select : set);
}

SPVehiclesTogglesPanel::SPVehiclesTogglesPanel(VehiclePanel *parent) : ListWidgetSP(parent, false) {
  setSpacing(50);

  // Hyundai/Kia/Genesis
  addItem(new LabelControlSP(tr("Hyundai/Kia/Genesis")));
  auto hkgSmoothStop = new ParamControlSP(
    "HkgSmoothStop",
    tr("HKG CAN: Smoother Stopping Performance (Beta)"),
    tr("Smoother stopping behind a stopped car or desired stopping event. This is only applicable to HKG CAN platforms using openpilot longitudinal control."),
    "../assets/offroad/icon_blank.png");
  hkgSmoothStop->setConfirmation(true, false);
  addItem(hkgSmoothStop);

  // Subaru
  addItem(new LabelControlSP(tr("Subaru")));
  auto subaruManualParkingBrakeSng = new ParamControlSP(
    "SubaruManualParkingBrakeSng",
    tr("Manual Parking Brake: Stop and Go (Beta)"),
    tr("Experimental feature to enable stop and go for Subaru Global models with manual handbrake. Models with electric parking brake should keep this disabled. Thanks to martinl for this implementation!"),
    "../assets/offroad/icon_blank.png");
  subaruManualParkingBrakeSng->setConfirmation(true, false);
  addItem(subaruManualParkingBrakeSng);

  // Tesla
  addItem(new LabelControlSP(tr("Tesla")));
  auto teslaVirtualTorqueBlending = new ParamControlSP(
    "TeslaVirtualTorqueBlending",
    tr("Virtual Torque Blending (Beta)"),
    tr("Experimental feature to allow influencing of the steering angle while ALC is active. Note: ALC/ACC will no longer disengage by applying force to the wheel."),
    "../assets/offroad/icon_blank.png");
  teslaVirtualTorqueBlending->setConfirmation(true, false);
  addItem(teslaVirtualTorqueBlending);

  // Toyota/Lexus
  addItem(new LabelControlSP(tr("Toyota/Lexus")));
  stockLongToyota = new ParamControlSP(
    "StockLongToyota",
    tr("Enable Stock Toyota Longitudinal Control"),
    tr("sunnypilot will <b>not</b> take over control of gas and brakes. Stock Toyota longitudinal control will be used."),
    "../assets/offroad/icon_blank.png");
  stockLongToyota->setConfirmation(true, false);
  addItem(stockLongToyota);

  auto lkasToggle = new ParamControlSP(
    "LkasToggle",
    tr("Allow M.A.D.S. toggling w/ LKAS Button (Beta)"),
    QString("%1<br>"
            "<h4>%2</h4><br>")
            .arg(tr("Allows M.A.D.S. engagement/disengagement with \"LKAS\" button from the steering wheel."))
            .arg(tr("Note: Enabling this toggle may have unexpected behavior with steering control. It is the driver's responsibility to observe their environment and make decisions accordingly.")),
    "../assets/offroad/icon_blank.png");
  lkasToggle->setConfirmation(true, false);
  addItem(lkasToggle);

  auto toyotaTss2LongTune = new ParamControlSP(
    "ToyotaTSS2Long",
    tr("Toyota TSS2 Longitudinal: Custom Tuning"),
    tr("Smoother longitudinal performance for Toyota/Lexus TSS2/LSS2 cars. Big thanks to dragonpilot-community for this implementation."),
    "../assets/offroad/icon_blank.png");
  toyotaTss2LongTune->setConfirmation(true, false);
  addItem(toyotaTss2LongTune);

  toyotaEnhancedBsm = new ParamControlSP(
    "ToyotaEnhancedBsm",
    tr("Enable Enhanced Blind Spot Monitor"),
    "",
    "../assets/offroad/icon_blank.png");
  toyotaEnhancedBsm->setConfirmation(true, false);
  addItem(toyotaEnhancedBsm);

  auto toyotaSngHack = new ParamControlSP(
    "ToyotaSnG",
    tr("Enable Toyota Stop and Go Hack"),
    tr("sunnypilot will allow some Toyota/Lexus cars to auto resume during stop and go traffic. This feature is only applicable to certain models. Use at your own risk."),
    "../assets/offroad/icon_blank.png");
  toyotaSngHack->setConfirmation(true, false);
  addItem(toyotaSngHack);

  auto toyotaAutoLock = new ParamControlSP(
    "ToyotaAutoLock",
    tr("Enable Toyota Door Auto Locking"),
    tr("sunnypilot will attempt to lock the doors when drive above 10 km/h (6.2 mph).\nReboot Required."),
    "../assets/offroad/icon_blank.png");
  toyotaAutoLock->setConfirmation(true, false);
  addItem(toyotaAutoLock);

  auto toyotaAutoUnlock = new ParamControlSP(
    "ToyotaAutoUnlockByShifter",
    tr("Enable Toyota Door Auto Unlocking"),
    tr("sunnypilot will attempt to unlock the doors when shift to gear P.\nReboot Required."),
    "../assets/offroad/icon_blank.png");
  toyotaAutoUnlock->setConfirmation(true, false);
  addItem(toyotaAutoUnlock);

  // Volkswagen
  addItem(new LabelControlSP(tr("Volkswagen")));
  auto volkswagenCCOnly = new ParamControlSP(
    "VwCCOnly",
    tr("Enable CC Only support"),
    tr("sunnypilot supports Volkswagen MQB CC only platforms with this toggle enabled. Only enable this toggle if your car does not have ACC from the factory."),
    "../assets/offroad/icon_blank.png");
  volkswagenCCOnly->setConfirmation(true, false);
  addItem(volkswagenCCOnly);

  // trigger offroadTransition when going onroad/offroad
  connect(uiStateSP(), &UIStateSP::offroadTransition, [=](bool offroad) {
    is_onroad = !offroad;
    hkgSmoothStop->setEnabled(offroad);
    toyotaTss2LongTune->setEnabled(offroad);
    toyotaEnhancedBsm->setEnabled(offroad);
    toyotaSngHack->setEnabled(offroad);
    volkswagenCCOnly->setEnabled(offroad);
    updateToggles();
  });
}

void SPVehiclesTogglesPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void SPVehiclesTogglesPanel::updateToggles() {
  if (!isVisible()) {
    return;
  }

  // Toyota: Enhanced Blind Spot Monitor
  QString ebsm_init = "<font color='yellow'>⚠️ " + tr("Start the car to check car compatibility") + "</font>";
  QString ebsm_not_required = "<font color=#00ff00>✅ " + tr("This platform is already supported, therefore no need to enable this toggle") + "</font>";
  QString ebsm_not_supported = "<font color='yellow'>⚠️ " + tr("This platform is not supported") + "</font>";
  QString ebsm_supported = "<font color=#00ff00>✅ " + tr("This platform can be supported") + "</font>";

  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    // Toyota: Enhanced Blind Spot Monitor
    {
      if (CP.getCarName() == "toyota") {
        if (CP.getEnableBsm() && !(CP.getSpFlags() & 4)) {  // 4 = ToyotaFlagsSP.SP_NEED_DEBUG_BSM
          toyotaEnhancedBsm->setDescription(toyotaEnhancedBsmDesciptionBuilder(ebsm_not_required));
          toyotaEnhancedBsm->showDescription();
          toyotaEnhancedBsm->setEnabled(false);
          params.remove("ToyotaEnhancedBsm");
        } else {
          toyotaEnhancedBsm->setDescription(toyotaEnhancedBsmDesciptionBuilder(ebsm_supported));
          toyotaEnhancedBsm->showDescription();
          toyotaEnhancedBsm->setEnabled(true);
        }
      } else {
        toyotaEnhancedBsm->setDescription(toyotaEnhancedBsmDesciptionBuilder(ebsm_not_supported));
        toyotaEnhancedBsm->showDescription();
        toyotaEnhancedBsm->setEnabled(false);
        params.remove("ToyotaEnhancedBsm");
      }
    }

    toyotaEnhancedBsm->refresh();
  } else {
    toyotaEnhancedBsm->setEnabled(false);
    params.remove("ToyotaEnhancedBsm");

    toyotaEnhancedBsm->setDescription(toyotaEnhancedBsmDesciptionBuilder(ebsm_init));
    toyotaEnhancedBsm->showDescription();
  }

  // override toggle state when onroad/offroad
  if (is_onroad) {
    toyotaEnhancedBsm->setEnabled(false);
  }
}
