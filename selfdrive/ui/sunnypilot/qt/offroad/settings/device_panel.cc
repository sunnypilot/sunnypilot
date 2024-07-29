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

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/device_panel.h"

#include <string>
#include <vector>
#include <QFileInfo>

#include "selfdrive/ui/qt/qt_window.h"
#include "selfdrive/ui/qt/widgets/prime.h"

DevicePanelSP::DevicePanelSP(SettingsWindow *parent) : DevicePanel(parent) {
  fleetManagerPin = new ButtonControlSP(
    pin_title + pin, tr("TOGGLE"),
    tr("Enable or disable PIN requirement for Fleet Manager access."));
  connect(fleetManagerPin, &ButtonControlSP::clicked, [=]() {
    if (params.getBool("FleetManagerPin")) {
      if (ConfirmationDialog::confirm(tr("Are you sure you want to turn off PIN requirement?"), tr("Turn Off"), this)) {
        params.remove("FleetManagerPin");
        refreshPin();
      }
    } else {
      params.putBool("FleetManagerPin", true);
      refreshPin();
    }
  });
  AddWidgetAt(2, fleetManagerPin);

  fs_watch = new QFileSystemWatcher(this);
  connect(fs_watch, &QFileSystemWatcher::fileChanged, this, &DevicePanelSP::onPinFileChanged);

  QString pin_path = "/data/otp/otp.conf";
  QString pin_require = "/data/params/d/FleetManagerPin";
  fs_watch->addPath(pin_path);
  fs_watch->addPath(pin_require);
  refreshPin();

  // Error Troubleshoot
  auto errorBtn = new ButtonControlSP(
    tr("Error Troubleshoot"), tr("VIEW"),
    tr("Display error from the tmux session when an error has occurred from a system process."));
  QFileInfo file("/data/community/crashes/error.txt");
  QDateTime modifiedTime = file.lastModified();
  QString modified_time = modifiedTime.toString("yyyy-MM-dd hh:mm:ss ");
  connect(errorBtn, &ButtonControlSP::clicked, [=]() {
    const std::string txt = util::read_file("/data/community/crashes/error.txt");
    ConfirmationDialog::rich(modified_time + QString::fromStdString(txt), this);
  });
  AddWidgetAt(3, errorBtn);


  auto resetMapboxTokenBtn = new ButtonControlSP(tr("Reset Access Tokens for Map Services"), tr("RESET"), tr("Reset self-service access tokens for Mapbox, Amap, and Google Maps."));
  connect(resetMapboxTokenBtn, &ButtonControlSP::clicked, [=]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to reset access tokens for all map services?"), tr("Reset"), this)) {
      std::vector<std::string> tokens = {
        "CustomMapboxTokenPk",
        "CustomMapboxTokenSk",
        "AmapKey1",
        "AmapKey2",
        "GmapKey"
      };
      for (const auto& token : tokens) {
        params.remove(token);
      }
    }
  });
  AddWidgetAt(6, resetMapboxTokenBtn);

  auto resetParamsBtn = new ButtonControlSP(tr("Reset sunnypilot Settings"), tr("RESET"), "");
  connect(resetParamsBtn, &ButtonControlSP::clicked, [=]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to reset all sunnypilot settings?"), tr("Reset"), this)) {
      std::system("sudo rm -rf /data/params/d/*");
      Hardware::reboot();
    }
  });
  AddWidgetAt(6, resetParamsBtn);
  
  QObject::connect(uiStateSP(), &UIStateSP::offroadTransition, [=](bool offroad) {
    for (auto btn : findChildren<ButtonControlSP *>()) {
      if (btn != pair_device && btn != errorBtn) { 
        btn->setEnabled(offroad);
      }
    }
  });

  offroad_btn = new QPushButton(tr("Toggle Onroad/Offroad"));
  offroad_btn->setObjectName("offroad_btn");
  QObject::connect(offroad_btn, &QPushButton::clicked, this, &DevicePanelSP::forceoffroad);

  QVBoxLayout *buttons_layout = new QVBoxLayout();
  buttons_layout->setSpacing(24);
  buttons_layout->addLayout(power_layout);
  buttons_layout->addWidget(offroad_btn);
  addItem(buttons_layout);

  updateLabels();
}

void DevicePanelSP::onPinFileChanged(const QString &file_path) {
  if (file_path == "/data/params/d/FleetManagerPin") {
    refreshPin();
  } else if (file_path == "/data/otp/otp.conf") {
    refreshPin();
  }
}

void DevicePanelSP::refreshPin() {
  QFile f("/data/otp/otp.conf");
  QFile require("/data/params/d/FleetManagerPin");
  if (!require.exists()) {
    setSpacing(50);
    fleetManagerPin->setTitle(pin_title + tr("OFF"));
  } else if (f.open(QIODevice::ReadOnly | QIODevice::Text)) {
    pin = f.readAll();
    f.close();
    setSpacing(50);
    fleetManagerPin->setTitle(pin_title + pin);
  }
}

void DevicePanelSP::forceoffroad() {
  if (!uiStateSP()->engaged()) {
    if (params.getBool("ForceOffroad")) {
      if (ConfirmationDialog::confirm(tr("Are you sure you want to unforce offroad?"), tr("Unforce"), this)) {
        // Check engaged again in case it changed while the dialog was open
        if (!uiStateSP()->engaged()) {
          params.remove("ForceOffroad");
        }
      }
    } else {
      if (ConfirmationDialog::confirm(tr("Are you sure you want to force offroad?"), tr("Force"), this)) {
        // Check engaged again in case it changed while the dialog was open
        if (!uiStateSP()->engaged()) {
          params.putBool("ForceOffroad", true);
        }
      }
    }
  } else {
    ConfirmationDialog::alert(tr("Disengage to Force Offroad"), this);
  }

  updateLabels();
}

void DevicePanelSP::showEvent(QShowEvent *event) {
  DevicePanel::showEvent(event);
  updateLabels();
}

void DevicePanelSP::updateLabels() {
  if (!isVisible()) {
    return;
  }

  bool force_offroad_param = params.getBool("ForceOffroad");
  QString offroad_btn_style = force_offroad_param ? "#393939" : "#E22C2C";
  QString offroad_btn_pressed_style = force_offroad_param ? "#4a4a4a" : "#FF2424";
  QString btn_common_style = QString("QPushButton { height: 120px; border-radius: 15px; background-color: %1; }"
                                     "QPushButton:pressed { background-color: %2; }")
                             .arg(offroad_btn_style,
                                  offroad_btn_pressed_style);

  offroad_btn->setText(force_offroad_param ? tr("Unforce Offroad") : tr("Force Offroad"));
  offroad_btn->setStyleSheet(btn_common_style + offroad_btn_style + offroad_btn_pressed_style);
}
