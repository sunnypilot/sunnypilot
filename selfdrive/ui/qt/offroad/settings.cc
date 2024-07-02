#include <cassert>
#include <cmath>
#include <string>
#include <tuple>
#include <vector>

#include <QDebug>
#include <QFile>
#include <QFileInfo>
#include <QDateTime>

#include "common/watchdog.h"
#include "common/util.h"
#include "selfdrive/ui/qt/network/networking.h"
#include "selfdrive/ui/qt/offroad/settings.h"
#include "selfdrive/ui/qt/offroad/sunnypilot_main.h"
#include "selfdrive/ui/qt/qt_window.h"
#include "selfdrive/ui/qt/widgets/prime.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/widgets/ssh_keys.h"

TogglesPanel::TogglesPanel(SettingsWindow *parent) : ListWidget(parent) {
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "OpenpilotEnabledToggle",
      tr("Enable sunnypilot"),
      tr("Use the sunnypilot system for adaptive cruise control and lane keep driver assistance. Your attention is required at all times to use this feature. Changing this setting takes effect when the car is powered off."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "ExperimentalLongitudinalEnabled",
      tr("openpilot Longitudinal Control (Alpha)"),
      QString("<b>%1</b><br><br>%2")
      .arg(tr("WARNING: openpilot longitudinal control is in alpha for this car and will disable Automatic Emergency Braking (AEB)."))
      .arg(tr("On this car, openpilot defaults to the car's built-in ACC instead of openpilot's longitudinal control. "
              "Enable this to switch to openpilot longitudinal control. Enabling Experimental mode is recommended when enabling openpilot longitudinal control alpha.")),
      "../assets/offroad/icon_blank.png",
    },
    {
      "CustomStockLong",
      tr("Custom Stock Longitudinal Control"),
      tr("When enabled, sunnypilot will attempt to control stock longitudinal control with ACC button presses.\nThis feature must be used along with SLC, and/or V-TSC, and/or M-TSC."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "CustomStockLongPlanner",
      tr("Use Planner Speed"),
      "",
      "../assets/offroad/icon_blank.png",
    },
    {
      "ExperimentalMode",
      tr("Experimental Mode"),
      "",
      "../assets/offroad/icon_blank.png",
    },
    {
      "DynamicExperimentalControl",
      tr("Enable Dynamic Experimental Control"),
      tr("Enable toggle to allow the model to determine when to use openpilot ACC or openpilot End to End Longitudinal."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DynamicPersonality",
      tr("Enable Dynamic Personality"),
      tr("Enable this to allow sunnypilot to dynamically adjust following distance and reaction based on your \"Driving Personality\" setting. "
        "Instead of predefined settings for each personality, every personality now adapts dynamically according to your speed and the distance to the lead car."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DisengageOnAccelerator",
      tr("Disengage on Accelerator Pedal"),
      tr("When enabled, pressing the accelerator pedal will disengage openpilot."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "IsLdwEnabled",
      tr("Enable Lane Departure Warnings"),
      tr("Receive alerts to steer back into the lane when your vehicle drifts over a detected lane line without a turn signal activated while driving over 31 mph (50 km/h)."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "AlwaysOnDM",
      tr("Always-On Driver Monitoring"),
      tr("Enable driver monitoring even when openpilot is not engaged."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "RecordFront",
      tr("Record and Upload Driver Camera"),
      tr("Upload data from the driver facing camera and help improve the driver monitoring algorithm."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DisableOnroadUploads",
      tr("Disable Onroad Uploads"),
      tr("Disable uploads completely when onroad. Necessary to avoid high data usage when connected to Wi-Fi hotspot. Turn on this feature if you are looking to utilize map-based features, such as Speed Limit Control (SLC) and Map-based Turn Speed Control (MTSC)."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "IsMetric",
      tr("Use Metric System"),
      tr("Display speed in km/h instead of mph."),
      "../assets/offroad/icon_blank.png",
    },
#ifdef ENABLE_MAPS
    {
      "NavSettingTime24h",
      tr("Show ETA in 24h Format"),
      tr("Use 24h format instead of am/pm"),
      "../assets/offroad/icon_blank.png",
    },
    {
      "NavSettingLeftSide",
      tr("Show Map on Left Side of UI"),
      tr("Show map on left side when in split screen view."),
      "../assets/offroad/icon_blank.png",
    },
#endif
  };


  std::vector<QString> longi_button_texts{tr("Aggressive"), tr("Moderate"), tr("Standard"), tr("Relaxed")};
  long_personality_setting = new ButtonParamControl("LongitudinalPersonality", tr("Driving Personality"),
                                          tr("Standard is recommended. In moderate/aggressive mode, openpilot will follow lead cars closer and be more aggressive with the gas and brake. "
                                             "In relaxed mode openpilot will stay further away from lead cars. On supported cars, you can cycle through these personalities with "
                                             "your steering wheel distance button."),
                                          "../assets/offroad/icon_blank.png",
                                          longi_button_texts,
                                          380);
  long_personality_setting->showDescription();

  // accel controller
  std::vector<QString> accel_personality_texts{tr("Sport"), tr("Normal"), tr("Eco"), tr("Stock")};
  accel_personality_setting = new ButtonParamControl("AccelPersonality", tr("Acceleration Personality"),
                                          tr("Normal is recommended. In sport mode, sunnypilot will provide aggressive acceleration for a dynamic driving experience. "
                                             "In eco mode, sunnypilot will apply smoother and more relaxed acceleration. On supported cars, you can cycle through these "
                                             "acceleration personality within Onroad Settings on the driving screen."),
                                          "../assets/offroad/icon_blank.png",
                                          accel_personality_texts);
  accel_personality_setting->showDescription();

  // set up uiState update for personality setting
  QObject::connect(uiState(), &UIState::uiUpdate, this, &TogglesPanel::updateState);

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControl(param, title, desc, icon, this);

    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);

    addItem(toggle);
    toggles[param.toStdString()] = toggle;

    // insert longitudinal personality after NDOG toggle
    if (param == "DisengageOnAccelerator") {
      addItem(long_personality_setting);
      addItem(accel_personality_setting);
    }
  }

  // Toggles with confirmation dialogs
  //toggles["ExperimentalMode"]->setActiveIcon("../assets/img_experimental.svg");
  toggles["ExperimentalMode"]->setConfirmation(true, true);
  toggles["ExperimentalLongitudinalEnabled"]->setConfirmation(true, false);
  toggles["CustomStockLong"]->setConfirmation(true, false);

  connect(toggles["ExperimentalLongitudinalEnabled"], &ToggleControl::toggleFlipped, [=]() {
    updateToggles();
  });
  connect(toggles["CustomStockLong"], &ToggleControl::toggleFlipped, [=]() {
    updateToggles();
  });
  connect(toggles["CustomStockLongPlanner"], &ToggleControl::toggleFlipped, [=]() {
    updateToggles();
  });
  connect(toggles["ExperimentalMode"], &ToggleControl::toggleFlipped, [=]() {
    updateToggles();
  });

  param_watcher = new ParamWatcher(this);

  QObject::connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    updateToggles();
  });
}

void TogglesPanel::updateState(const UIState &s) {
  const SubMaster &sm = *(s.sm);

  if (sm.updated("controlsState")) {
    auto personality = sm["controlsState"].getControlsState().getPersonality();
    if (personality != s.scene.personality && s.scene.started && isVisible()) {
      long_personality_setting->setCheckedButton(static_cast<int>(personality));
    }
    uiState()->scene.personality = personality;
  }

  if (sm.updated("controlsStateSP")) {
    auto accel_personality = sm["controlsStateSP"].getControlsStateSP().getAccelPersonality();
    if (accel_personality != s.scene.accel_personality && s.scene.started && isVisible()) {
      accel_personality_setting->setCheckedButton(static_cast<int>(accel_personality));
    }
    uiState()->scene.accel_personality = accel_personality;
  }
}

void TogglesPanel::expandToggleDescription(const QString &param) {
  toggles[param.toStdString()]->showDescription();
}

void TogglesPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void TogglesPanel::updateToggles() {
  param_watcher->addParam("LongitudinalPersonality");

  if (!isVisible()) return;

  auto experimental_mode_toggle = toggles["ExperimentalMode"];
  auto op_long_toggle = toggles["ExperimentalLongitudinalEnabled"];
  auto custom_stock_long_toggle = toggles["CustomStockLong"];
  auto dec_toggle = toggles["DynamicExperimentalControl"];
  auto dynamic_personality_toggle = toggles["DynamicPersonality"];
  auto custom_stock_long_planner = toggles["CustomStockLongPlanner"];
  const QString e2e_description = QString("%1<br>"
                                          "<h4>%2</h4><br>"
                                          "%3<br>"
                                          "<h4>%4</h4><br>"
                                          "%5<br>")
                                  .arg(tr("openpilot defaults to driving in <b>chill mode</b>. Experimental mode enables <b>alpha-level features</b> that aren't ready for chill mode. Experimental features are listed below:"))
                                  .arg(tr("End-to-End Longitudinal Control"))
                                  .arg(tr("Let the driving model control the gas and brakes. openpilot will drive as it thinks a human would, including stopping for red lights and stop signs. "
                                          "Since the driving model decides the speed to drive, the set speed will only act as an upper bound. This is an alpha quality feature; "
                                          "mistakes should be expected."))
                                  .arg(tr("New Driving Visualization"))
                                  .arg(tr("The driving visualization will transition to the road-facing wide-angle camera at low speeds to better show some turns. The Experimental mode logo will also be shown in the top right corner."));

  const bool is_release = params.getBool("IsReleaseBranch");
  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    if (!CP.getExperimentalLongitudinalAvailable() || is_release) {
      params.remove("ExperimentalLongitudinalEnabled");
    }
    op_long_toggle->setVisible(CP.getExperimentalLongitudinalAvailable() && !is_release);

    if (!CP.getCustomStockLongAvailable()) {
      params.remove("CustomStockLong");
    }
    custom_stock_long_toggle->setVisible(CP.getCustomStockLongAvailable());

    if (hasLongitudinalControl(CP)) {
      // normal description and toggle
      experimental_mode_toggle->setEnabled(true);
      experimental_mode_toggle->setDescription(e2e_description);
      long_personality_setting->setEnabled(true);
      accel_personality_setting->setEnabled(true);
      op_long_toggle->setEnabled(true);
      custom_stock_long_toggle->setEnabled(false);
      custom_stock_long_planner->setEnabled(false);
      params.remove("CustomStockLong");
      dec_toggle->setEnabled(true);
      dynamic_personality_toggle->setEnabled(true);
    } else if (custom_stock_long_toggle->isToggled()) {
      op_long_toggle->setEnabled(false);
      experimental_mode_toggle->setEnabled(custom_stock_long_planner->isToggled());
      experimental_mode_toggle->setDescription(e2e_description);
      custom_stock_long_planner->setEnabled(true);
      long_personality_setting->setEnabled(custom_stock_long_planner->isToggled());
      accel_personality_setting->setEnabled(custom_stock_long_planner->isToggled());
      dec_toggle->setEnabled(experimental_mode_toggle->isToggled());
      if(!custom_stock_long_planner->isToggled()) {
        params.remove("ExperimentalMode");
      }
      params.remove("ExperimentalLongitudinalEnabled");
    } else {
      // no long for now
      experimental_mode_toggle->setEnabled(false);
      long_personality_setting->setEnabled(false);
      accel_personality_setting->setEnabled(false);
      params.remove("ExperimentalMode");

      const QString unavailable = tr("Experimental mode is currently unavailable on this car since the car's stock ACC is used for longitudinal control.");

      QString long_desc = unavailable + " " + \
                          tr("openpilot longitudinal control may come in a future update.");
      if (CP.getExperimentalLongitudinalAvailable()) {
        if (is_release) {
          long_desc = unavailable + " " + tr("An alpha version of openpilot longitudinal control can be tested, along with Experimental mode, on non-release branches.");
        } else {
          long_desc = tr("Enable the openpilot longitudinal control (alpha) toggle to allow Experimental mode.");
        }
      }
      experimental_mode_toggle->setDescription("<b>" + long_desc + "</b><br><br>" + e2e_description);

      op_long_toggle->setEnabled(CP.getExperimentalLongitudinalAvailable() && !is_release);
      custom_stock_long_toggle->setEnabled(CP.getCustomStockLongAvailable());
      dec_toggle->setEnabled(false);
      dynamic_personality_toggle->setEnabled(false);
      custom_stock_long_planner->setEnabled(false);
      params.remove("DynamicExperimentalControl");
      params.remove("DynamicPersonality");
    }

    experimental_mode_toggle->refresh();
    op_long_toggle->refresh();
    custom_stock_long_toggle->refresh();
    custom_stock_long_planner->refresh();
    dec_toggle->refresh();
    dynamic_personality_toggle->refresh();
  } else {
    experimental_mode_toggle->setDescription(e2e_description);
    op_long_toggle->setVisible(false);
    custom_stock_long_toggle->setVisible(false);
    dec_toggle->setVisible(false);
    dynamic_personality_toggle->setVisible(false);
    custom_stock_long_planner->setVisible(false);
  }
}

DevicePanel::DevicePanel(SettingsWindow *parent) : ListWidget(parent) {
  setSpacing(50);
  addItem(new LabelControl(tr("Dongle ID"), getDongleId().value_or(tr("N/A"))));
  addItem(new LabelControl(tr("Serial"), params.get("HardwareSerial").c_str()));

  fleetManagerPin = new ButtonControl(
    pin_title + pin, tr("TOGGLE"),
    tr("Enable or disable PIN requirement for Fleet Manager access."));
  connect(fleetManagerPin, &ButtonControl::clicked, [=]() {
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
  addItem(fleetManagerPin);

  fs_watch = new QFileSystemWatcher(this);
  connect(fs_watch, &QFileSystemWatcher::fileChanged, this, &DevicePanel::onPinFileChanged);

  QString pin_path = "/data/otp/otp.conf";
  QString pin_require = "/data/params/d/FleetManagerPin";
  fs_watch->addPath(pin_path);
  fs_watch->addPath(pin_require);
  refreshPin();

  // Error Troubleshoot
  auto errorBtn = new ButtonControl(
    tr("Error Troubleshoot"), tr("VIEW"),
    tr("Display error from the tmux session when an error has occurred from a system process."));
  QFileInfo file("/data/community/crashes/error.txt");
  QDateTime modifiedTime = file.lastModified();
  QString modified_time = modifiedTime.toString("yyyy-MM-dd hh:mm:ss ");
  connect(errorBtn, &ButtonControl::clicked, [=]() {
    const std::string txt = util::read_file("/data/community/crashes/error.txt");
    ConfirmationDialog::rich(modified_time + QString::fromStdString(txt), this);
  });
  addItem(errorBtn);

  pair_device = new ButtonControl(tr("Pair Device"), tr("PAIR"),
                                  tr("Pair your device with comma connect (connect.comma.ai) and claim your comma prime offer."));
  connect(pair_device, &ButtonControl::clicked, [=]() {
    PairingPopup popup(this);
    popup.exec();
  });
  addItem(pair_device);

  // offroad-only buttons

  auto dcamBtn = new ButtonControl(tr("Driver Camera"), tr("PREVIEW"),
                                   tr("Preview the driver facing camera to ensure that driver monitoring has good visibility. (vehicle must be off)"));
  connect(dcamBtn, &ButtonControl::clicked, [=]() { emit showDriverView(); });
  addItem(dcamBtn);

  auto resetCalibBtn = new ButtonControl(tr("Reset Calibration"), tr("RESET"), "");
  connect(resetCalibBtn, &ButtonControl::showDescriptionEvent, this, &DevicePanel::updateCalibDescription);
  connect(resetCalibBtn, &ButtonControl::clicked, [&]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to reset calibration?"), tr("Reset"), this)) {
      params.remove("CalibrationParams");
      params.remove("LiveTorqueParameters");
    }
  });
  addItem(resetCalibBtn);

  auto resetMapboxTokenBtn = new ButtonControl(tr("Reset Access Tokens for Map Services"), tr("RESET"), tr("Reset self-service access tokens for Mapbox, Amap, and Google Maps."));
  connect(resetMapboxTokenBtn, &ButtonControl::clicked, [=]() {
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
  addItem(resetMapboxTokenBtn);

  auto resetParamsBtn = new ButtonControl(tr("Reset sunnypilot Settings"), tr("RESET"), "");
  connect(resetParamsBtn, &ButtonControl::clicked, [=]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to reset all sunnypilot settings?"), tr("Reset"), this)) {
      std::system("sudo rm -rf /data/params/d/*");
      Hardware::reboot();
    }
  });
  addItem(resetParamsBtn);

  auto retrainingBtn = new ButtonControl(tr("Review Training Guide"), tr("REVIEW"), tr("Review the rules, features, and limitations of sunnypilot"));
  connect(retrainingBtn, &ButtonControl::clicked, [=]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to review the training guide?"), tr("Review"), this)) {
      emit reviewTrainingGuide();
    }
  });
  addItem(retrainingBtn);

  if (Hardware::TICI()) {
    auto regulatoryBtn = new ButtonControl(tr("Regulatory"), tr("VIEW"), "");
    connect(regulatoryBtn, &ButtonControl::clicked, [=]() {
      const std::string txt = util::read_file("../assets/offroad/fcc.html");
      ConfirmationDialog::rich(QString::fromStdString(txt), this);
    });
    addItem(regulatoryBtn);
  }

  auto translateBtn = new ButtonControl(tr("Change Language"), tr("CHANGE"), "");
  connect(translateBtn, &ButtonControl::clicked, [=]() {
    QMap<QString, QString> langs = getSupportedLanguages();
    QString selection = MultiOptionDialog::getSelection(tr("Select a language"), langs.keys(), langs.key(uiState()->language), this);
    if (!selection.isEmpty()) {
      // put language setting, exit Qt UI, and trigger fast restart
      params.put("LanguageSetting", langs[selection].toStdString());
      qApp->exit(18);
      watchdog_kick(0);
    }
  });
  addItem(translateBtn);

  QObject::connect(uiState(), &UIState::primeTypeChanged, [this] (PrimeType type) {
    pair_device->setVisible(type == PrimeType::UNPAIRED);
  });
  QObject::connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    for (auto btn : findChildren<ButtonControl *>()) {
      if ((btn != pair_device) && (btn != errorBtn)) {
        btn->setEnabled(offroad);
      }
    }
  });

  // power buttons
  QHBoxLayout *power_layout = new QHBoxLayout();
  power_layout->setSpacing(30);

  QPushButton *reboot_btn = new QPushButton(tr("Reboot"));
  reboot_btn->setObjectName("reboot_btn");
  power_layout->addWidget(reboot_btn);
  QObject::connect(reboot_btn, &QPushButton::clicked, this, &DevicePanel::reboot);

  QPushButton *poweroff_btn = new QPushButton(tr("Power Off"));
  poweroff_btn->setObjectName("poweroff_btn");
  power_layout->addWidget(poweroff_btn);
  QObject::connect(poweroff_btn, &QPushButton::clicked, this, &DevicePanel::poweroff);

  if (!Hardware::PC()) {
    connect(uiState(), &UIState::offroadTransition, poweroff_btn, &QPushButton::setVisible);
  }

  offroad_btn = new QPushButton(tr("Toggle Onroad/Offroad"));
  offroad_btn->setObjectName("offroad_btn");
  QObject::connect(offroad_btn, &QPushButton::clicked, this, &DevicePanel::forceoffroad);

  QVBoxLayout *buttons_layout = new QVBoxLayout();
  buttons_layout->setSpacing(24);
  buttons_layout->addLayout(power_layout);
  buttons_layout->addWidget(offroad_btn);

  setStyleSheet(R"(
    #reboot_btn { height: 120px; border-radius: 15px; background-color: #393939; }
    #reboot_btn:pressed { background-color: #4a4a4a; }
    #poweroff_btn { height: 120px; border-radius: 15px; background-color: #E22C2C; }
    #poweroff_btn:pressed { background-color: #FF2424; }
  )");
  addItem(buttons_layout);

  updateLabels();
}

void DevicePanel::onPinFileChanged(const QString &file_path) {
  if (file_path == "/data/params/d/FleetManagerPin") {
    refreshPin();
  } else if (file_path == "/data/otp/otp.conf") {
    refreshPin();
  }
}

void DevicePanel::refreshPin() {
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

void DevicePanel::updateCalibDescription() {
  QString desc =
      tr("sunnypilot requires the device to be mounted within 4° left or right and "
         "within 5° up or 9° down. sunnypilot is continuously calibrating, resetting is rarely required.");
  std::string calib_bytes = params.get("CalibrationParams");
  if (!calib_bytes.empty()) {
    try {
      AlignedBuffer aligned_buf;
      capnp::FlatArrayMessageReader cmsg(aligned_buf.align(calib_bytes.data(), calib_bytes.size()));
      auto calib = cmsg.getRoot<cereal::Event>().getLiveCalibration();
      if (calib.getCalStatus() != cereal::LiveCalibrationData::Status::UNCALIBRATED) {
        double pitch = calib.getRpyCalib()[1] * (180 / M_PI);
        double yaw = calib.getRpyCalib()[2] * (180 / M_PI);
        desc += tr(" Your device is pointed %1° %2 and %3° %4.")
                    .arg(QString::number(std::abs(pitch), 'g', 1), pitch > 0 ? tr("down") : tr("up"),
                         QString::number(std::abs(yaw), 'g', 1), yaw > 0 ? tr("left") : tr("right"));
      }
    } catch (kj::Exception) {
      qInfo() << "invalid CalibrationParams";
    }
  }
  qobject_cast<ButtonControl *>(sender())->setDescription(desc);
}

void DevicePanel::reboot() {
  if (!uiState()->engaged()) {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to reboot?"), tr("Reboot"), this)) {
      // Check engaged again in case it changed while the dialog was open
      if (!uiState()->engaged()) {
        params.putBool("DoReboot", true);
      }
    }
  } else {
    ConfirmationDialog::alert(tr("Disengage to Reboot"), this);
  }
}

void DevicePanel::poweroff() {
  if (!uiState()->engaged()) {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to power off?"), tr("Power Off"), this)) {
      // Check engaged again in case it changed while the dialog was open
      if (!uiState()->engaged()) {
        params.putBool("DoShutdown", true);
      }
    }
  } else {
    ConfirmationDialog::alert(tr("Disengage to Power Off"), this);
  }
}

void DevicePanel::forceoffroad() {
  if (!uiState()->engaged()) {
    if (params.getBool("ForceOffroad")) {
      if (ConfirmationDialog::confirm(tr("Are you sure you want to unforce offroad?"), tr("Unforce"), this)) {
        // Check engaged again in case it changed while the dialog was open
        if (!uiState()->engaged()) {
          params.remove("ForceOffroad");
        }
      }
    } else {
      if (ConfirmationDialog::confirm(tr("Are you sure you want to force offroad?"), tr("Force"), this)) {
        // Check engaged again in case it changed while the dialog was open
        if (!uiState()->engaged()) {
          params.putBool("ForceOffroad", true);
        }
      }
    }
  } else {
    ConfirmationDialog::alert(tr("Disengage to Force Offroad"), this);
  }

  updateLabels();
}

void DevicePanel::showEvent(QShowEvent *event) {
  pair_device->setVisible(uiState()->primeType() == PrimeType::UNPAIRED);
  ListWidget::showEvent(event);
  updateLabels();
}

void DevicePanel::updateLabels() {
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

void SettingsWindow::showEvent(QShowEvent *event) {
  setCurrentPanel(0);
}

void SettingsWindow::setCurrentPanel(int index, const QString &param) {
  panel_widget->setCurrentIndex(index);
  nav_btns->buttons()[index]->setChecked(true);
  if (!param.isEmpty()) {
    emit expandToggleDescription(param);
  }
}

SettingsWindow::SettingsWindow(QWidget *parent) : QFrame(parent) {

  // setup two main layouts
  sidebar_widget = new QWidget;
  QVBoxLayout *sidebar_layout = new QVBoxLayout(sidebar_widget);
  panel_widget = new QStackedWidget();

  // setup layout for close button
  QVBoxLayout *close_btn_layout = new QVBoxLayout;
  close_btn_layout->setContentsMargins(0, 0, 0, 20);

  // close button
  QPushButton *close_btn = new QPushButton(tr("×"));
  close_btn->setStyleSheet(R"(
    QPushButton {
      font-size: 140px;
      padding-bottom: 20px;
      border-radius: 76px;
      background-color: #292929;
      font-weight: 400;
    }
    QPushButton:pressed {
      background-color: #3B3B3B;
    }
  )");
  close_btn->setFixedSize(152, 152);
  close_btn_layout->addWidget(close_btn, 0, Qt::AlignLeft);
  QObject::connect(close_btn, &QPushButton::clicked, this, &SettingsWindow::closeSettings);

  // setup buttons widget
  QWidget *buttons_widget = new QWidget;
  QVBoxLayout *buttons_layout = new QVBoxLayout(buttons_widget);
  buttons_layout->setMargin(0);
  buttons_layout->addSpacing(10);

  // setup panels
  DevicePanel *device = new DevicePanel(this);
  QObject::connect(device, &DevicePanel::reviewTrainingGuide, this, &SettingsWindow::reviewTrainingGuide);
  QObject::connect(device, &DevicePanel::showDriverView, this, &SettingsWindow::showDriverView);

  TogglesPanel *toggles = new TogglesPanel(this);
  QObject::connect(this, &SettingsWindow::expandToggleDescription, toggles, &TogglesPanel::expandToggleDescription);

  QList<PanelInfo> panels = {
    PanelInfo("   " + tr("Device"), device, "../assets/navigation/icon_home.svg"),
    PanelInfo("   " + tr("Network"), new Networking(this), "../assets/offroad/icon_network.png"),
    PanelInfo("   " + tr("sunnylink"), new SunnylinkPanel(this), "../assets/offroad/icon_wifi_strength_full.svg"),
    PanelInfo("   " + tr("Toggles"), toggles, "../assets/offroad/icon_toggle.png"),
    PanelInfo("   " + tr("Software"), new SoftwarePanelSP(this), "../assets/offroad/icon_software.png"),
    PanelInfo("   " + tr("sunnypilot"), new SunnypilotPanel(this), "../assets/offroad/icon_openpilot.png"),
    PanelInfo("   " + tr("OSM"), new OsmPanel(this), "../assets/offroad/icon_map.png"),
    PanelInfo("   " + tr("Monitoring"), new MonitoringPanel(this), "../assets/offroad/icon_monitoring.png"),
    PanelInfo("   " + tr("Visuals"), new VisualsPanel(this), "../assets/offroad/icon_visuals.png"),
    PanelInfo("   " + tr("Display"), new DisplayPanel(this), "../assets/offroad/icon_display.png"),
    PanelInfo("   " + tr("Trips"), new TripsPanel(this), "../assets/offroad/icon_trips.png"),
    PanelInfo("   " + tr("Vehicle"), new VehiclePanel(this), "../assets/offroad/icon_vehicle.png"),
  };

  nav_btns = new QButtonGroup(this);
  for (auto &[name, panel, icon] : panels) {
    QPushButton *btn = new QPushButton(name);
    btn->setCheckable(true);
    btn->setChecked(nav_btns->buttons().size() == 0);
    btn->setIcon(QIcon(QPixmap(icon)));
    btn->setIconSize(QSize(70, 70));
    btn->setStyleSheet(R"(
      QPushButton {
        border-radius: 20px;
        width: 400px;
        height: 98px;
        color: #bdbdbd;
        border: none;
        background: none;
        font-size: 50px;
        font-weight: 500;
        text-align: left;
        padding-left: 22px;
      }
      QPushButton:checked {
        background-color: #696868;
        color: white;
      }
      QPushButton:pressed {
        color: #ADADAD;
      }
    )");
    btn->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Expanding);
    nav_btns->addButton(btn);
    buttons_layout->addWidget(btn, 0, Qt::AlignLeft | Qt::AlignBottom);

    const int lr_margin = (name != ("   " + tr("Network")) || (name != ("   " + tr("sunnypilot")))) ? 50 : 0;  // Network and sunnypilot panel handles its own margins
    panel->setContentsMargins(lr_margin, 25, lr_margin, 25);

    ScrollView *panel_frame = new ScrollView(panel, this);
    panel_widget->addWidget(panel_frame);

    QObject::connect(btn, &QPushButton::clicked, [=, w = panel_frame]() {
      btn->setChecked(true);
      panel_widget->setCurrentWidget(w);
    });
  }
  sidebar_layout->setContentsMargins(50, 50, 25, 50);

  // main settings layout, sidebar + main panel
  QHBoxLayout *main_layout = new QHBoxLayout(this);

  // add layout for close button
  sidebar_layout->addLayout(close_btn_layout);

  // add layout for buttons scrolling
  ScrollView *buttons_scrollview  = new ScrollView(buttons_widget, this);
  sidebar_layout->addWidget(buttons_scrollview);

  sidebar_widget->setFixedWidth(500);
  main_layout->addWidget(sidebar_widget);
  main_layout->addWidget(panel_widget);

  setStyleSheet(R"(
    * {
      color: white;
      font-size: 50px;
    }
    SettingsWindow {
      background-color: black;
    }
    QStackedWidget, ScrollView {
      background-color: black;
      border-radius: 30px;
    }
  )");
}
