#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <thread>
#include <chrono>

#include "common/watchdog.h"
#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/qt/offroad/sunnypilot_settings.h"
#include "selfdrive/ui/qt/widgets/input.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/util.h"

#include "selfdrive/ui/ui.h"

SPGeneralPanel::SPGeneralPanel(QWidget *parent) : ListWidget(parent) {
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "QuietDrive",
      tr("Quiet Drive 🤫"),
      tr("sunnypilot will display alerts but only play the most important warning sounds. This feature can be toggled while the car is on."),
      "../assets/offroad/icon_mute.png",
    },
    {
      "EndToEndLongAlertLight",
      tr("Green Traffic Light Chime (Beta)"),
      QString("%1<br>"
              "<h4>%2</h4><br>")
              .arg(tr("A chime will play when the traffic light you are waiting for turns green and you have no vehicle in front of you. If you are waiting behind another vehicle, the chime will play once the vehicle advances unless ACC is engaged."))
              .arg(tr("Note: This chime is only designed as a notification. It is the driver's responsibility to observe their environment and make decisions accordingly.")),
      "../assets/offroad/icon_road.png",
    },
    {
      "EndToEndLongAlertLead",
      tr("Lead Vehicle Departure Alert"),
      QString("%1<br>"
              "<h4>%2</h4><br>")
              .arg(tr("Enable this will notify when the leading vehicle drives away."))
              .arg(tr("Note: This chime is only designed as a notification. It is the driver's responsibility to observe their environment and make decisions accordingly.")),
      "../assets/offroad/icon_road.png",
    },
    {
      "HotspotOnBoot",
      tr("Retain hotspot/tethering state"),
      tr("Enabling this toggle will retain the hotspot/tethering toggle state across reboots."),
      "../assets/offroad/icon_network.png",
    },
    {
      "OnroadScreenOffEvent",
      tr("Driving Screen Off: Non-Critical Events"),
      QString("%1<br>"
              "<h4>%2</h4><br>"
              "<h4>%3</h4><br>")
      .arg(tr("When <b>Driving Screen Off Timer</b> is not set to <b>\"Always On\"</b>:"))
      .arg(tr("Enabled: Wake the brightness of the screen to display all events."))
      .arg(tr("Disabled: Wake the brightness of the screen to display critical events.")),
      "../assets/offroad/icon_blank.png",
    },
    {
      "ScreenRecorder",
      tr("Enable Screen Recorder"),
      tr("Enable this will display a button on the onroad screen to toggle on or off real-time screen recording with UI elements."),
      "../assets/offroad/icon_calibration.png"
    },
    {
      "DisableOnroadUploads",
      tr("Disable Onroad Uploads"),
      tr("Disable uploads completely when onroad. Necessary to avoid high data usage when connected to Wi-Fi hotspot. Turn on this feature if you are looking to utilize map-based features, such as Speed Limit Control (SLC) and Map-based Turn Speed Control (MTSC)."),
      "../assets/offroad/icon_network.png",
    },
    {
      "EnableDebugSnapshot",
      tr("Debug snapshot on screen center tap"),
      tr("Stores snapshot file with current state of some modules."),
      "../assets/offroad/icon_calibration.png"
    }
  };

  // General: Onroad Screen Off (Auto Onroad Screen Timer)
  onroad_screen_off = new OnroadScreenOff();
  // General: Onroad Screen Off Brightness
  onroad_screen_off_brightness = new OnroadScreenOffBrightness();

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControl(param, title, desc, icon, this);

    addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "HotspotOnBoot") {
      // General: Max Time Offroad (Shutdown timer)
      addItem(new MaxTimeOffroad());

      addItem(onroad_screen_off);

      addItem(onroad_screen_off_brightness);
    }

    if (param == "OnroadScreenOffEvent") {
      // General: Brightness Control (Global)
      addItem(new BrightnessControl());
    }
  }

  connect(onroad_screen_off, &OnroadScreenOff::toggleUpdated, this, &SPGeneralPanel::updateToggles);

  toggles["EndToEndLongAlertLight"]->setConfirmation(true, false);
}

void SPGeneralPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void SPGeneralPanel::updateToggles() {
  // toggle names to update when OnroadScreenOff is toggled
  onroad_screen_off_brightness->setVisible(QString::fromStdString(params.get("OnroadScreenOff")) != "-2");
  toggles["OnroadScreenOffEvent"]->setVisible(QString::fromStdString(params.get("OnroadScreenOff")) != "-2");
}

SPControlsPanel::SPControlsPanel(QWidget *parent) : ListWidget(parent) {
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "EnableMads",
      tr("Enable M.A.D.S."),
      tr("Enable the beloved M.A.D.S. feature. Disable toggle to revert back to stock openpilot engagement/disengagement."),
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "DisengageLateralOnBrake",
      tr("Disengage ALC On Brake Pedal ℹ"),
      QString("%1<br>"
              "<h4>%2</h4><br>"
              "<h4>%3</h4><br>")
      .arg(tr("Define brake pedal interactions with sunnypilot when M.A.D.S. is enabled."))
      .arg(tr("Enabled: Pressing the brake pedal will disengage Automatic Lane Centering (ALC) on sunnypilot."))
      .arg(tr("Disabled: Pressing the brake pedal will <b>NOT</b> disengage Automatic Lane Centering (ALC) on sunnypilot.")),
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "AccMadsCombo",
      tr("Enable ACC+MADS with RES+/SET-"),
      QString("%1<br>"
              "<h4>%2</h4><br>")
      .arg(tr("Engage both M.A.D.S. and ACC with a single press of RES+ or SET- button."))
      .arg(tr("Note: Once M.A.D.S. is engaged via this mode, it will remain engaged until it is manually disabled via the M.A.D.S. button or car shut off.")),
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "MadsCruiseMain",
      tr("Toggle M.A.D.S. with Cruise Main"),
      tr("Allows M.A.D.S. engagement/disengagement with \"Cruise Main\" cruise control button from the steering wheel."),
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "BelowSpeedPause",
      tr("Pause Lateral Below Speed w/ Blinker"),
      tr("Enable this toggle to pause lateral actuation with blinker when traveling below 30 MPH or 50 KM/H."),
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "RoadEdge",
      tr("Block Lane Change: Road Edge Detection"),
      tr("Enable this toggle to block lane change when road edge is detected on the stalk actuated side."),
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "DynamicLaneProfileToggle",
      tr("Enable Dynamic Lane Profile"),
      tr("Enable toggle to use Dynamic Lane Profile. Disable toggle to use Laneless only."),
      "../assets/offroad/icon_road.png",
    },
    {
      "VisionCurveLaneless",
      tr("Laneless for Curves in \"Auto lane\""),
      tr("While in Auto Lane, switch to Laneless for current/future curves."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "CustomOffsets",
      tr("Custom Offsets"),
      tr("Add custom offsets to Camera and Path in sunnypilot."),
      "../assets/offroad/icon_metric.png",
    },
    {
      "AutoLaneChangeBsmDelay",
      tr("Auto Lane Change: Delay with Blind Spot"),
      tr("Toggle to enable a delay timer for seamless lane changes when blind spot monitoring (BSM) detects a obstructing vehicle, ensuring safe maneuvering."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "GapAdjustCruise",
      tr("Enable Gap Adjust Cruise ℹ"),
      QString("%1<br>"
              "<h4>%2</h4>")
      .arg(tr("Enable the Interval button on the steering wheel to adjust the cruise gap."))
      .arg(tr("Only available to cars with openpilot Longitudinal Control")),
      "../assets/offroad/icon_dynamic_gac.png",
    },
    {
      "EnforceTorqueLateral",
      tr("Enforce Torque Lateral Control"),
      tr("Enable this to enforce sunnypilot to steer with Torque lateral control."),
      "../assets/offroad/icon_calibration.png",
    },
    {
      "CustomTorqueLateral",
      tr("Torque Lateral Control Live Tune"),
      tr("Enables live tune for Torque lateral control."),
      "../assets/offroad/icon_calibration.png",
    },
    {
      "LiveTorque",
      tr("Torque Lateral Controller Self-Tune"),
      tr("Enables self-tune for Torque lateral control."),
      "../assets/offroad/icon_calibration.png",
    },
    {
      "HandsOnWheelMonitoring",
      tr("Enable Hands on Wheel Monitoring"),
      tr("Monitor and alert when driver is not keeping the hands on the steering wheel."),
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "TurnVisionControl",
      tr("Enable Vision Based Turn Speed Control (V-TSC)"),
      tr("Use vision path predictions to estimate the appropriate speed to drive through turns ahead."),
      "../assets/offroad/icon_road.png",
    },
    {
      "SpeedLimitControl",
      tr("Enable Speed Limit Control (SLC)"),
      tr("Use speed limit signs information from map data and car interface (if applicable) to automatically adapt cruise speed to road limits."),
      "../assets/offroad/icon_speed_limit.png",
    },
    {
      "SpeedLimitPercOffset",
      tr("Enable Speed Limit Offset"),
      tr("Set speed limit slightly higher than actual speed limit for a more natural drive."),
      "../assets/offroad/icon_speed_limit.png",
    },
    {
      "TurnSpeedControl",
      tr("Enable Map Data Turn Speed Control (M-TSC)"),
      tr("Use curvature information from map data to define speed limits to take turns ahead."),
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "ReverseAccChange",
      tr("ACC +/-: Long Press Reverse"),
      QString("%1<br>"
              "<h4>%2</h4><br>"
              "<h4>%3</h4><br>")
      .arg(tr("Change the ACC +/- buttons behavior with cruise speed change in sunnypilot."))
      .arg(tr("Disabled (Stock): Short=1, Long = 5 (imperial) / 10 (metric)"))
      .arg(tr("Enabled: Short = 5 (imperial) / 10 (metric), Long=1")),
      "../assets/offroad/icon_acc_change.png",
    },
    {
      "OsmLocalDb",
      tr("OSM: Use Offline Database"),
      "",
      "../assets/img_map.png",
    },
  };

  // toggle names to trigger updateToggles() when toggleFlipped
  std::vector<std::string> updateTogglesNames{
    "EnableMads", "DynamicLaneProfileToggle", "CustomOffsets", "GapAdjustCruise", "EnforceTorqueLateral",
    "SpeedLimitPercOffset", "SpeedLimitControl"
  };
  // toggle names to trigger updateToggles() when toggleFlipped and display ConfirmationDialog::alert
  std::vector<std::string> updateTogglesNamesAlert{
    "CustomTorqueLateral", "LiveTorque"
  };
  // toggle names to trigger updateToggles() when toggleFlipped and display ConfirmationDialog::alert
  std::vector<std::string> toggleOffroad{
    "EnableMads", "DisengageLateralOnBrake", "AccMadsCombo", "MadsCruiseMain", "BelowSpeedPause", "EnforceTorqueLateral",
    "CustomTorqueLateral", "LiveTorque", "GapAdjustCruise"
  };

  // Controls: Camera Offset (cm)
  camera_offset = new CameraOffset();
  // Controls: Path Offset (cm)
  path_offset = new PathOffset();
  // Controls: Auto Lane Change Timer
  auto_lane_change_timer = new AutoLaneChangeTimer();
  // Controls: Speed Limit Offset Type
  slo_type = new SpeedLimitOffsetType();
  // Controls: Speed Limit Offset Values (% or actual value)
  slvo = new SpeedLimitValueOffset();
  // Controls: GAC Mode
  gac_mode = new GapAdjustCruiseMode();
  // Controls: Torque - FRICTION
  friction = new TorqueFriction();
  // Controls: Torque - LAT_ACCEL_FACTOR
  lat_accel_factor = new TorqueMaxLatAccel();
  // Controls: MUTCD: US/Canada\nVienna: Europe/Asia/etc.
  speed_limit_style = new SpeedLimitStyle();

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControl(param, title, desc, icon, this);

    addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "CustomOffsets") {
      // Controls: Camera Offset (cm)
      addItem(camera_offset);

      // Controls: Path Offset (cm)
      addItem(path_offset);

      // Controls: Auto Lane Change Timer
      addItem(auto_lane_change_timer);
    }

    if (param == "GapAdjustCruise") {
      // Controls: Mode
      addItem(gac_mode);
    }

    if (param == "CustomTorqueLateral") {
      // Control: FRICTION
      addItem(friction);

      // Controls: LAT_ACCEL_FACTOR
      addItem(lat_accel_factor);
    }

    if (param == "SpeedLimitControl") {
      // Controls: MUTCD: US/Canada\nVienna: Europe/Asia/etc.
      addItem(speed_limit_style);
    }

    if (param == "SpeedLimitPercOffset") {
      // Controls: Speed Limit Offset Type
      addItem(slo_type);

      // Controls: Speed Limit Offset Values (% or actual value)
      addItem(slvo);
    }

    // trigger updateToggles() when toggleFlipped
    if (std::find(updateTogglesNames.begin(), updateTogglesNames.end(), param.toStdString()) != updateTogglesNames.end()) {
      connect(toggle, &ToggleControl:: toggleFlipped, [=](bool state) {
        updateToggles();
      });
    }

    // trigger updateToggles() and display ConfirmationDialog::alert when toggleFlipped
    if (std::find(updateTogglesNamesAlert.begin(), updateTogglesNamesAlert.end(), param.toStdString()) != updateTogglesNamesAlert.end()) {
      connect(toggle, &ToggleControl:: toggleFlipped, [=](bool state) {
        updateToggles();
        ConfirmationDialog::alert(tr("You must restart your car or your device to apply these changes."), this);
      });
    }

    // trigger offroadTransition when going onroad/offroad
    if (std::find(toggleOffroad.begin(), toggleOffroad.end(), param.toStdString()) != toggleOffroad.end()) {
      connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
        toggle->setEnabled(offroad);
      });
    }
  }

  connect(auto_lane_change_timer, &AutoLaneChangeTimer::toggleUpdated, this, &SPControlsPanel::updateToggles);
  connect(slo_type, &SpeedLimitOffsetType::offsetTypeUpdated, this, &SPControlsPanel::updateToggles);
  connect(toggles["GapAdjustCruise"], &ToggleControl::toggleFlipped, [=]() { emit updateStockToggles(); });

  toggles["EnableMads"]->setConfirmation(true, false);
  toggles["DisengageLateralOnBrake"]->setConfirmation(true, false);
  toggles["GapAdjustCruise"]->setConfirmation(true, false);

  connect(toggles["OsmLocalDb"], &ToggleControl::toggleFlipped, [=](bool state) {
    if (!state) {
      params.remove("OsmLocalDb");
    }
  });
}

void SPControlsPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void SPControlsPanel::updateToggles() {
  // toggle names to update when EnableMads is flipped
  std::vector<std::string> enableMadsGroup{"DisengageLateralOnBrake", "AccMadsCombo", "MadsCruiseMain"};
  for (const auto& enableMadstoggle : enableMadsGroup) {
    if (toggles.find(enableMadstoggle) != toggles.end()) {
      toggles[enableMadstoggle]->setVisible(params.getBool("EnableMads"));
    }
  }

  // toggle names to update when DynamicLaneProfileToggle is flipped
  toggles["VisionCurveLaneless"]->setVisible(params.getBool("DynamicLaneProfileToggle"));

  // toggle names to update when CustomOffsets is flipped
  std::vector<AbstractControl*> customOffsetsGroup{camera_offset, path_offset};
  for (const auto& customOffsetsControl : customOffsetsGroup) {
    customOffsetsControl->setVisible(params.getBool("CustomOffsets"));
  }

  // toggle names to update when GapAdjustCruise is flipped
  gac_mode->setVisible(params.getBool("GapAdjustCruise"));

  // toggle names to update when AutoLaneChangeTimer is not "Nudge"
  toggles["AutoLaneChangeBsmDelay"]->setVisible(QString::fromStdString(params.get("AutoLaneChangeTimer")) != "0");

  auto custom_torque_lateral = toggles["CustomTorqueLateral"];
  auto live_torque = toggles["LiveTorque"];

  // toggle names to update when EnforceTorqueLateral is flipped
  std::vector<std::string> enforceTorqueGroup{"CustomTorqueLateral", "LiveTorque"};
  for (const auto& enforceTorqueToggle : enforceTorqueGroup) {
    if (toggles.find(enforceTorqueToggle) != toggles.end()) {
      toggles[enforceTorqueToggle]->setVisible(params.getBool("EnforceTorqueLateral"));
    }
  }

  // toggle names to update when CustomTorqueLateral is flipped
  std::vector<AbstractControl*> customTorqueGroup{friction, lat_accel_factor};
  for (const auto& customTorqueControl : customTorqueGroup) {
    customTorqueControl->setVisible(params.getBool("CustomTorqueLateral"));
  }

  // toggle names to update when SpeedLimitControl is flipped
  std::vector<AbstractControl*> speedLimitControlGroup{slo_type, slvo};
  for (const auto& speedLimitControl : speedLimitControlGroup) {
    speedLimitControl->setVisible(params.getBool("SpeedLimitControl"));
  }

  if (params.getBool("EnforceTorqueLateral")) {
    if (params.getBool("CustomTorqueLateral")) {
      live_torque->setEnabled(false);
      params.putBool("LiveTorque", false);
    } else {
      live_torque->setEnabled(true);
    }

    if (params.getBool("LiveTorque")) {
      custom_torque_lateral->setEnabled(false);
      params.putBool("CustomTorqueLateral", false);
      for (const auto& customTorqueControl : customTorqueGroup) {
        customTorqueControl->setVisible(false);
      }
    } else {
      custom_torque_lateral->setEnabled(true);
    }

    live_torque->refresh();
    custom_torque_lateral->refresh();
  } else {
    params.putBool("LiveTorque", false);
    params.putBool("CustomTorqueLateral", false);
    for (const auto& customTorqueControl : customTorqueGroup) {
      customTorqueControl->setVisible(false);
    }
  }

  if (params.getBool("SpeedLimitControl")) {
    if (params.getBool("SpeedLimitPercOffset")) {
      slvo->setVisible(QString::fromStdString(params.get("SpeedLimitOffsetType")) != "0");
      slo_type->setVisible(true);
    } else {
      for (const auto& speedLimitControl : speedLimitControlGroup) {
        speedLimitControl->setVisible(false);
      }
    }
  } else {
    for (const auto& speedLimitControl : speedLimitControlGroup) {
      speedLimitControl->setVisible(false);
    }
  }

  // toggle names to update when SpeedLimitControl is flipped
  speed_limit_style->setVisible(params.getBool("SpeedLimitControl"));
  toggles["SpeedLimitPercOffset"]->setVisible(params.getBool("SpeedLimitControl"));

  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    if (CP.getSteerControlType() == cereal::CarParams::SteerControlType::ANGLE) {
      toggles["EnforceTorqueLateral"]->setEnabled(false);
      params.remove("EnforceTorqueLateral");
    }
  }
}

SPVehiclesPanel::SPVehiclesPanel(QWidget *parent) : QWidget(parent) {
  main_layout = new QStackedLayout(this);
  home = new QWidget(this);
  QVBoxLayout* fcr_layout = new QVBoxLayout(home);
  fcr_layout->setContentsMargins(0, 20, 0, 20);

  QString set = QString::fromStdString(params.get("CarModelText"));
  QPushButton* setCarBtn = new QPushButton(((set == "=== Not Selected ===") || (set.length() == 0)) ? "Select your car" : set);
  setCarBtn->setObjectName("setCarBtn");
  setCarBtn->setStyleSheet("margin-right: 30px;");
  connect(setCarBtn, &QPushButton::clicked, [=]() {
    QMap<QString, QString> cars = getCarNames();
    QString currentCar = QString::fromStdString(params.get("CarModel"));
    QString selection = MultiOptionDialog::getSelection("Select your car", cars.keys(), cars.key(currentCar), this);
    if (!selection.isEmpty()) {
      params.put("CarModel", cars[selection].toStdString());
      params.put("CarModelText", selection.toStdString());
      qApp->exit(18);
      watchdog_kick(0);
    }
  });
  fcr_layout->addSpacing(10);
  fcr_layout->addWidget(setCarBtn, 0, Qt::AlignRight);
  fcr_layout->addSpacing(10);

  home_widget = new QWidget(this);
  QVBoxLayout* toggle_layout = new QVBoxLayout(home_widget);
  home_widget->setObjectName("homeWidget");

  ScrollView *scroller = new ScrollView(home_widget, this);
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

SPVehiclesTogglesPanel::SPVehiclesTogglesPanel(SPVehiclesPanel *parent) : ListWidget(parent) {
  setSpacing(50);
  addItem(new LabelControl(tr("Hyundai/Kia/Genesis")));
  auto hkgSmoothStop = new ParamControl(
    "HkgSmoothStop",
    "HKG CAN: Smoother Stopping Performance (Beta)",
    "Smoother stopping behind a stopped car or desired stopping event. This is only applicable to HKG CAN platforms using openpilot longitudinal control.",
    "../assets/offroad/icon_blank.png"
  );
  hkgSmoothStop->setConfirmation(true, false);
  addItem(hkgSmoothStop);

  addItem(new LabelControl(tr("Toyota/Lexus")));
  stockLongToyota = new ParamControl(
    "StockLongToyota",
    "Enable Stock Toyota Longitudinal Control",
    "sunnypilot will <b>not</b> take over control of gas and brakes. Stock Toyota longitudinal control will be used.",
    "../assets/offroad/icon_blank.png"
  );
  stockLongToyota->setConfirmation(true, false);
  addItem(stockLongToyota);

  auto lkasToggle = new ParamControl(
    "LkasToggle",
    tr("Allow M.A.D.S. toggling w/ LKAS Button (Beta)"),
    QString("%1<br>"
            "<h4>%2</h4><br>")
            .arg(tr("Allows M.A.D.S. engagement/disengagement with \"LKAS\" button from the steering wheel."))
            .arg(tr("Note: Enabling this toggle may have unexpected behavior with steering control. It is the driver's responsibility to observe their environment and make decisions accordingly.")),
    "../assets/offroad/icon_blank.png"
  );
  lkasToggle->setConfirmation(true, false);
  addItem(lkasToggle);

  auto toyotaTss2LongTune = new ParamControl(
    "ToyotaTSS2Long",
    "TSS2 Longitudinal: Custom Tuning",
    "Smoother longitudinal performance for Toyota/Lexus TSS2/LSS2 cars. Big thanks to dragonpilot-community for this implementation.",
    "../assets/offroad/icon_blank.png"
  );
  toyotaTss2LongTune->setConfirmation(true, false);
  addItem(toyotaTss2LongTune);

  // trigger offroadTransition when going onroad/offroad
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    hkgSmoothStop->setEnabled(offroad);
    toyotaTss2LongTune->setEnabled(offroad);
  });
}

SPVisualsPanel::SPVisualsPanel(QWidget *parent) : ListWidget(parent) {
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "BrakeLights",
      tr("Display Braking Status"),
      tr("Enable this will turn the current speed value to red while the brake is used."),
      "../assets/offroad/icon_road.png",
    },
    {
      "StandStillTimer",
      tr("Display Stand Still Timer"),
      tr("Enable this will display time spent at a stop (i.e., at a stop lights, stop signs, traffic congestions)."),
      "../assets/offroad/icon_road.png",
    },
    {
      "DevUI",
      tr("Show Developer UI"),
      tr("Show developer UI (Dev UI) for real-time parameters from various sources."),
      "../assets/offroad/icon_calibration.png",
    },
    {
      "ButtonAutoHide",
      tr("Auto-Hide UI Buttons"),
      tr("Hide UI buttons on driving screen after a 30-second timeout. Tap on the screen at anytime to reveal the UI buttons."),
      "../assets/offroad/icon_road.png",
    },
    {
      "ReverseDmCam",
      tr("Display DM Camera in Reverse Gear"),
      tr("Show Driver Monitoring camera while the car is in reverse gear."),
      "../assets/offroad/icon_road.png",
    },
    {
      "ShowDebugUI",
      tr("OSM: Show debug UI elements"),
      tr("OSM: Show UI elements that aid debugging."),
      "../assets/offroad/icon_calibration.png",
    },
    {
      "CustomMapbox",
      tr("Enable Mapbox Navigation*"),
      QString("%1<br>"
              "%2<br>"
              "%3<br>"
              "<h4>%4</h4>")
      .arg(tr("Enable built-in navigation on sunnypilot, powered by Mapbox."))
      .arg(tr("Access via the web interface: \"http://<device_ip>:8082\""))
      .arg(tr("If you do not have comma Prime, you will need to provide your own Mapbox token at https://mapbox.com/. Reach out to sunnyhaibin#0865 on Discord for more information."))
      .arg(tr("Huge thanks to the dragonpilot team for making this possible!")),
      "../assets/img_map.png",
    },
    {
      "TrueVEgoUi",
      tr("Speedometer: Display True Speed"),
      tr("Display the true vehicle current speed from wheel speed sensors."),
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "HideVEgoUi",
      tr("Speedometer: Hide from Onroad Screen"),
      "",
      "../assets/offroad/icon_openpilot.png",
    },
    {
      "EndToEndLongAlertUI",
      tr("Display End-to-end Longitudinal Status (Beta)"),
      tr("Enable this will display an icon that appears when the End-to-end model decides to start or stop."),
      "../assets/offroad/icon_road.png",
    },
  };

  // Developer UI Info (Dev UI)
  dev_ui_info = new DevUiInfo();
  // Visuals: Display Metrics above Chevron
  chevron_info = new ChevronInfo();

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControl(param, title, desc, icon, this);

    addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "DevUI") {
      addItem(dev_ui_info);
    }

    if (param == "HideVEgoUi") {
      addItem(chevron_info);
    }
  }

  auto sidebar_temp = new SidebarTemp(this);
  addItem(sidebar_temp);

  // trigger updateToggles() when toggleFlipped
  connect(toggles["DevUI"], &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });

  // trigger offroadTransition when going onroad/offroad
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    toggles["CustomMapbox"]->setEnabled(offroad);
  });

  // trigger hardwrae reboot if user confirms the selection
  connect(toggles["CustomMapbox"], &ToggleControl::toggleFlipped, [=](bool state) {
    if (ConfirmationDialog::confirm(tr("\"Enable Mapbox Navigation\"\nYou must restart your car or your device to apply these changes.\nReboot now?"), "Reboot", parent)) {
      Hardware::reboot();
    }
  });
}

void SPVisualsPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void SPVisualsPanel::updateToggles() {
  dev_ui_info->setVisible(params.getBool("DevUI"));
}

// Max Time Offroad (Shutdown timer)
MaxTimeOffroad::MaxTimeOffroad() : AbstractControl(
  tr("Max Time Offroad"),
  tr("Device is automatically turned off after a set time when the engine is turned off (off-road) after driving (on-road)."),
  "../assets/offroad/icon_metric.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("MaxTimeOffroad"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("MaxTimeOffroad", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("MaxTimeOffroad"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 12 ) {
      value = 12;
    }
    QString values = QString::number(value);
    params.put("MaxTimeOffroad", values.toStdString());
    refresh();
  });
  refresh();
}

void MaxTimeOffroad::refresh() {
  QString option = QString::fromStdString(params.get("MaxTimeOffroad"));
  QString second = tr("s");
  QString minute = tr("m");
  QString hour = tr("h");
  if (option == "0") {
    label.setText(tr("Always On"));
  } else if (option == "1") {
    label.setText(tr("Immediate"));
  } else if (option == "2") {
    label.setText("30" + second);
  } else if (option == "3") {
    label.setText("1" + minute);
  } else if (option == "4") {
    label.setText("3" + minute);
  } else if (option == "5") {
    label.setText("5" + minute);
  } else if (option == "6") {
    label.setText("10" + minute);
  } else if (option == "7") {
    label.setText("30" + minute);
  } else if (option == "8") {
    label.setText("1" + hour);
  } else if (option == "9") {
    label.setText("3" + hour);
  } else if (option == "10") {
    label.setText("5" + hour);
  } else if (option == "11") {
    label.setText("10" + hour);
  } else if (option == "12") {
    label.setText("30" + hour);
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Onroad Screen Off (Auto Onroad Screen Timer)
OnroadScreenOff::OnroadScreenOff() : AbstractControl(
  tr("Driving Screen Off Timer"),
  tr("Turn off the device screen or reduce brightness to protect the screen after driving starts. It automatically brightens or turns on when a touch or event occurs."),
  "../assets/offroad/icon_metric.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("OnroadScreenOff"));
    int value = str.toInt();
    value = value - 1;
    if (value <= -2 ) {
      value = -2;
    }
    uiState()->scene.onroadScreenOff = value;
    QString values = QString::number(value);
    params.put("OnroadScreenOff", values.toStdString());
    refresh();
    emit toggleUpdated();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("OnroadScreenOff"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 10 ) {
      value = 10;
    }
    uiState()->scene.onroadScreenOff = value;
    QString values = QString::number(value);
    params.put("OnroadScreenOff", values.toStdString());
    refresh();
    emit toggleUpdated();
  });
  refresh();
}

void OnroadScreenOff::refresh()
{
  QString option = QString::fromStdString(params.get("OnroadScreenOff"));
  QString second = tr("s");
  if (option == "-2") {
    label.setText(tr("Always On"));
  } else if (option == "-1") {
    label.setText("15" + second);
  } else if (option == "0") {
    label.setText("30" + second);
  } else {
    label.setText(QString::fromStdString(params.get("OnroadScreenOff")) + "min(s)");
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Onroad Screen Off Brightness
OnroadScreenOffBrightness::OnroadScreenOffBrightness() : AbstractControl(
  tr("Driving Screen Off Brightness (%)"),
  tr("When using the Driving Screen Off feature, the brightness is reduced according to the automatic brightness ratio."),
  "../assets/offroad/icon_blank.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("OnroadScreenOffBrightness"));
    int value = str.toInt();
    value = value - 10;
    if (value <= 0 ) {
      value = 0;
    }
    uiState()->scene.onroadScreenOffBrightness = value;
    QString values = QString::number(value);
    params.put("OnroadScreenOffBrightness", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("OnroadScreenOffBrightness"));
    int value = str.toInt();
    value = value + 10;
    if (value >= 100 ) {
      value = 100;
    }
    uiState()->scene.onroadScreenOffBrightness = value;
    QString values = QString::number(value);
    params.put("OnroadScreenOffBrightness", values.toStdString());
    refresh();
  });
  refresh();
}

void OnroadScreenOffBrightness::refresh() {
  QString option = QString::fromStdString(params.get("OnroadScreenOffBrightness"));
  if (option == "0") {
    label.setText(tr("Dark"));
  } else {
    label.setText(QString::fromStdString(params.get("OnroadScreenOffBrightness")));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Brightness Control (Global)
BrightnessControl::BrightnessControl() : AbstractControl(
  tr("Brightness Control (Global, %)"),
  tr("Manually adjusts the global brightness of the screen."),
  "../assets/offroad/icon_metric.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("BrightnessControl"));
    int value = str.toInt();
    value = value - 5;
    if (value <= 0 ) {
      value = 0;
    }
    uiState()->scene.brightness = value;
    QString values = QString::number(value);
    params.put("BrightnessControl", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("BrightnessControl"));
    int value = str.toInt();
    value = value + 5;
    if (value >= 100 ) {
      value = 100;
    }
    uiState()->scene.brightness = value;
    QString values = QString::number(value);
    params.put("BrightnessControl", values.toStdString());
    refresh();
  });
  refresh();
}

void BrightnessControl::refresh() {
  QString option = QString::fromStdString(params.get("BrightnessControl"));
  if (option == "0") {
    label.setText(tr("Auto"));
  } else {
    label.setText(QString::fromStdString(params.get("BrightnessControl")));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Camera Offset Value
CameraOffset::CameraOffset() : AbstractControl(
  tr("Camera Offset (cm)"),
  tr("Hack to trick vehicle to be left or right biased in its lane. Decreasing the value will make the car keep more left, increasing will make it keep more right. Changes take effect immediately."),
  "../assets/offroad/icon_blank.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("CameraOffset"));
    int value = str.toInt();
    value = value - 1;
    if (value <= -10 ) {
      value = -10;
    }

    QString values = QString::number(value);
    params.put("CameraOffset", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("CameraOffset"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 10 ) {
      value = 10;
    }

    QString values = QString::number(value);
    params.put("CameraOffset", values.toStdString());
    refresh();
  });
  refresh();
}

void CameraOffset::refresh() {
  QString option = QString::fromStdString(params.get("CameraOffset"));
  label.setText(QString::fromStdString(params.get("CameraOffset")));
  btnminus.setText("-");
  btnplus.setText("+");
}

// Path Offset Value
PathOffset::PathOffset() : AbstractControl(
  tr("Path Offset (cm)"),
  tr("Hack to trick the model path to be left or right biased of the lane. Decreasing the value will shift the model more left, increasing will shift the model more right. Changes take effect immediately."),
  "../assets/offroad/icon_blank.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("PathOffset"));
    int value = str.toInt();
    value = value - 1;
    if (value <= -10 ) {
      value = -10;
    }

    QString values = QString::number(value);
    params.put("PathOffset", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("PathOffset"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 10 ) {
      value = 10;
    }

    QString values = QString::number(value);
    params.put("PathOffset", values.toStdString());
    refresh();
  });
  refresh();
}

void PathOffset::refresh() {
  QString option = QString::fromStdString(params.get("PathOffset"));
  label.setText(QString::fromStdString(params.get("PathOffset")));
  btnminus.setText("-");
  btnplus.setText("+");
}

// Auto Lane Change Timer (ALCT)
AutoLaneChangeTimer::AutoLaneChangeTimer() : AbstractControl(
  tr("Auto Lane Change Timer"),
  tr("Set a timer to delay the auto lane change operation when the blinker is used. No nudge on the steering wheel is required to auto lane change if a timer is set.\nPlease use caution when using this feature. Only use the blinker when traffic and road conditions permit."),
  "../assets/offroad/icon_road.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("AutoLaneChangeTimer"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("AutoLaneChangeTimer", values.toStdString());
    refresh();
    emit toggleUpdated();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("AutoLaneChangeTimer"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 5 ) {
      value = 5;
    }
    QString values = QString::number(value);
    params.put("AutoLaneChangeTimer", values.toStdString());
    refresh();
    emit toggleUpdated();
  });
  refresh();
}

void AutoLaneChangeTimer::refresh() {
  QString option = QString::fromStdString(params.get("AutoLaneChangeTimer"));
  QString second = tr("s");
  if (option == "0") {
    label.setText(tr("Nudge"));
  } else if (option == "1") {
    label.setText(tr("Nudgeless"));
  } else if (option == "2") {
    label.setText("0.5" + second);
  } else if (option == "3") {
    label.setText("1" + second);
  } else if (option == "4") {
    label.setText("1.5" + second);
  } else {
    label.setText("2" + second);
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// G.A.C. Mode
GapAdjustCruiseMode::GapAdjustCruiseMode() : AbstractControl(
  tr("Mode"),
  QString("%1<br>"
          "%2<br>"
          "%3")
  .arg(tr("SW: Steering Wheel Button only"))
  .arg(tr("UI: User Interface Button on screen only"))
  .arg(tr("SW + UI: Steering Wheel Button + User Interface Button on screen")),
  "../assets/offroad/icon_blank.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("GapAdjustCruiseMode"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("GapAdjustCruiseMode", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("GapAdjustCruiseMode"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 2 ) {
      value = 2;
    }
    QString values = QString::number(value);
    params.put("GapAdjustCruiseMode", values.toStdString());
    refresh();
  });
  refresh();
}

void GapAdjustCruiseMode::refresh() {
  QString option = QString::fromStdString(params.get("GapAdjustCruiseMode"));
  if (option == "0") {
    label.setText(tr("S.W."));
  } else if (option == "1") {
    label.setText(tr("UI"));
  } else if (option == "2") {
    label.setText(tr("S.W. + UI"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

TorqueFriction::TorqueFriction() : AbstractControl(
  tr("FRICTION"),
  tr("Adjust Friction for the Torque Lateral Controller"),
  "../assets/offroad/icon_blank.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("TorqueFriction"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("TorqueFriction", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("TorqueFriction"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 50 ) {
      value = 50;
    }
    QString values = QString::number(value);
    params.put("TorqueFriction", values.toStdString());
    refresh();
  });
  refresh();
}

void TorqueFriction::refresh() {
  auto strs = QString::fromStdString(params.get("TorqueFriction"));
  int valuei = strs.toInt();
  float valuef = valuei * 0.01;
  QString valuefs = QString::number(valuef);
  label.setText(QString::fromStdString(valuefs.toStdString()));
  btnminus.setText("-");
  btnplus.setText("+");
}

TorqueMaxLatAccel::TorqueMaxLatAccel() : AbstractControl(
  tr("LAT_ACCEL_FACTOR"),
  tr("Adjust Max Lateral Acceleration for the Torque Lateral Controller"),
  "../assets/offroad/icon_blank.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("TorqueMaxLatAccel"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 1 ) {
      value = 1;
    }
    QString values = QString::number(value);
    params.put("TorqueMaxLatAccel", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("TorqueMaxLatAccel"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 500 ) {
      value = 500;
    }
    QString values = QString::number(value);
    params.put("TorqueMaxLatAccel", values.toStdString());
    refresh();
  });
  refresh();
}

void TorqueMaxLatAccel::refresh() {
  auto strs = QString::fromStdString(params.get("TorqueMaxLatAccel"));
  int valuei = strs.toInt();
  float valuef = valuei * 0.01;
  QString valuefs = QString::number(valuef);
  label.setText(QString::fromStdString(valuefs.toStdString()));
  btnminus.setText("-");
  btnplus.setText("+");
}

SpeedLimitStyle::SpeedLimitStyle() : AbstractControl(
  tr("Speed Limit Style"),
  QString("%1<br>"
          "%2")
  .arg(tr("MUTCD: US/Canada"))
  .arg(tr("Vienna: Europe/Asia/etc.")),
  "../assets/offroad/icon_blank.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("SpeedLimitStyle"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("SpeedLimitStyle", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("SpeedLimitStyle"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 1 ) {
      value = 1;
    }
    QString values = QString::number(value);
    params.put("SpeedLimitStyle", values.toStdString());
    refresh();
  });
  refresh();
}

void SpeedLimitStyle::refresh() {
  QString option = QString::fromStdString(params.get("SpeedLimitStyle"));
  if (option == "0") {
    label.setText(tr("MUTCD"));
  } else {
    label.setText(tr("Vienna"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Speed Limit Control Custom Offset Type
SpeedLimitOffsetType::SpeedLimitOffsetType() : AbstractControl(
  tr("Speed Limit Offset Type"),
  QString("%1<br>"
          "%2")
  .arg(tr("Set speed limit higher or lower than actual speed limit for a more personalized drive."))
  .arg(tr("To use this feature, turn off \"Enable Speed Limit % Offset\".")),
  "../assets/offroad/icon_speed_limit.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("SpeedLimitOffsetType"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("SpeedLimitOffsetType", values.toStdString());
    refresh();
    emit offsetTypeUpdated();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("SpeedLimitOffsetType"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 2 ) {
      value = 2;
    }
    QString values = QString::number(value);
    params.put("SpeedLimitOffsetType", values.toStdString());
    refresh();
    emit offsetTypeUpdated();
  });
  refresh();
}

void SpeedLimitOffsetType::refresh() {
  QString option = QString::fromStdString(params.get("SpeedLimitOffsetType"));
  if (option == "0") {
    label.setText(tr("Default"));
  } else if (option == "1") {
    label.setText(tr("%"));
  } else if (option == "2") {
    label.setText(tr("Value"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Speed Limit Control Custom Offset
SpeedLimitValueOffset::SpeedLimitValueOffset() : AbstractControl(
  "",
  "",
  "../assets/offroad/icon_blank.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("SpeedLimitValueOffset"));
    int value = str.toInt();
    value = value - 1;
    if (value <= -30 ) {
      value = -30;
    }
    QString values = QString::number(value);
    params.put("SpeedLimitValueOffset", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("SpeedLimitValueOffset"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 30 ) {
      value = 30;
    }
    QString values = QString::number(value);
    params.put("SpeedLimitValueOffset", values.toStdString());
    refresh();
  });
  refresh();
}

void SpeedLimitValueOffset::refresh() {
  label.setText(QString::fromStdString(params.get("SpeedLimitValueOffset")));
  btnminus.setText("-");
  btnplus.setText("+");
}

// Developer UI Info (Dev UI)
DevUiInfo::DevUiInfo() : AbstractControl(
  tr("Developer UI List"),
  tr("Select the number of lists of real-time parameters you would like to display on the sunnypilot screen while driving."),
  "../assets/offroad/icon_blank.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("DevUIInfo"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("DevUIInfo", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("DevUIInfo"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 1 ) {
      value = 1;
    }
    QString values = QString::number(value);
    params.put("DevUIInfo", values.toStdString());
    refresh();
  });
  refresh();
}

void DevUiInfo::refresh() {
  QString option = QString::fromStdString(params.get("DevUIInfo"));
  if (option == "0") {
    label.setText(tr("5 Metrics"));
  } else {
    label.setText(tr("10 Metrics"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Display Metrics above Chevron
ChevronInfo::ChevronInfo() : AbstractControl(
  tr("Display Metrics above Chevron"),
  tr("Display useful metrics above the chevron that tracks the lead car (only applicable to cars with openpilot longitudinal control)."),
  "../assets/offroad/icon_calibration.png")

{
  label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
  label.setStyleSheet("color: #e0e879");
  hlayout->addWidget(&label);

  btnminus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnplus.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 50px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnminus.setFixedSize(150, 100);
  btnplus.setFixedSize(150, 100);
  hlayout->addWidget(&btnminus);
  hlayout->addWidget(&btnplus);

  QObject::connect(&btnminus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("ChevronInfo"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("ChevronInfo", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("ChevronInfo"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 2 ) {
      value = 2;
    }
    QString values = QString::number(value);
    params.put("ChevronInfo", values.toStdString());
    refresh();
  });
  refresh();
}

void ChevronInfo::refresh() {
  QString option = QString::fromStdString(params.get("ChevronInfo"));
  if (option == "0") {
    label.setText(tr("OFF"));
  } else if (option == "1") {
    label.setText(tr("Distance"));
  } else if (option == "2") {
    label.setText(tr("Speed"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

SidebarTemp::SidebarTemp(QWidget *parent) : QWidget(parent), outer_layout(this) {
  outer_layout.setMargin(0);
  outer_layout.setSpacing(0);
  outer_layout.addLayout(&inner_layout);
  inner_layout.setMargin(0);
  //inner_layout.setSpacing(25); // default spacing is 25
  outer_layout.addStretch();

  sidebarTemperature = new ParamControl(
    "SidebarTemperature",
    tr("Display Temperature on Sidebar"),
    tr("Display Ambient temperature, memory temperature, CPU core with the highest temperature, GPU temperature, or max of Memory/CPU/GPU on the sidebar."),
    "../assets/offroad/icon_calibration.png"
  );

  std::vector<QString> sidebar_temp_texts{tr("Ambient"), tr("Memory"), tr("CPU"), tr("GPU"), tr("Max")};
  sidebar_temp_setting = new ButtonParamControl(
    "SidebarTemperatureOptions", "", "",
    "../assets/offroad/icon_blank.png",
    sidebar_temp_texts
  );

  connect(sidebarTemperature, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });

  addItem(sidebarTemperature);
  addItem(sidebar_temp_setting);
}

void SidebarTemp::showEvent(QShowEvent *event) {
  updateToggles();
}

void SidebarTemp::updateToggles() {
  sidebar_temp_setting->setVisible(params.getBool("SidebarTemperature"));
}
