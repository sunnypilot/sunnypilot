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
  onroad_screen_off->setUpdateOtherToggles(true);
  connect(onroad_screen_off, &SPOptionControl::updateLabels, onroad_screen_off, &OnroadScreenOff::refresh);
  connect(onroad_screen_off, &SPOptionControl::updateOtherToggles, this, &SPGeneralPanel::updateToggles);

  // General: Onroad Screen Off Brightness
  onroad_screen_off_brightness = new OnroadScreenOffBrightness();
  connect(onroad_screen_off_brightness, &SPOptionControl::updateLabels, onroad_screen_off_brightness, &OnroadScreenOffBrightness::refresh);

  // General: Brightness Control (Global)
  auto brightness_control = new BrightnessControl();
  connect(brightness_control, &SPOptionControl::updateLabels, brightness_control, &BrightnessControl::refresh);

  // General: Max Time Offroad (Shutdown timer)
  auto max_time_offroad = new MaxTimeOffroad();
  connect(max_time_offroad, &SPOptionControl::updateLabels, max_time_offroad, &MaxTimeOffroad::refresh);

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControl(param, title, desc, icon, this);

    addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "HotspotOnBoot") {
      // General: Max Time Offroad (Shutdown timer)
      addItem(max_time_offroad);

      addItem(onroad_screen_off);

      addItem(onroad_screen_off_brightness);
    }

    if (param == "OnroadScreenOffEvent") {
      // General: Brightness Control (Global)
      addItem(brightness_control);
    }
  }

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
    // Dynamic Lane Profile group will fit here
    {
      "VisionCurveLaneless",
      tr("Laneless for Curves in \"Auto lane\""),
      tr("While in Auto Lane, switch to Laneless for current/future curves."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DynamicExperimentalControlToggle",
      tr("Enable Dynamic Experimental Control"),
      tr("Enable toggle to allow the model to determine when to use openpilot ACC or openpilot End to End Longitudinal."),
      "../assets/offroad/icon_speed_limit.png",
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
      "EnforceTorqueLateral",
      tr("Enforce Torque Lateral Control"),
      tr("Enable this to enforce sunnypilot to steer with Torque lateral control."),
      "../assets/offroad/icon_calibration.png",
    },
    {
      "LiveTorque",
      tr("Enable Self-Tune"),
      tr("Enables self-tune for Torque lateral control for platforms that do not use Torque lateral control by default."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "LiveTorqueRelaxed",
      tr("Less Restrict Settings for Self-Tune (Beta)"),
      tr("Less strict settings when using Self-Tune. This allows torqued to be more forgiving when learning values."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "CustomTorqueLateral",
      tr("Enable Custom Tuning"),
      tr("Enables custom tuning for Torque lateral control. Modifying FRICTION and LAT_ACCEL_FACTOR below will override the offline values indicated in the YAML files within \"selfdrive/torque_data\". The values will also be used live when \"Override Self-Tune\" toggle is enabled."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "TorquedOverride",
      tr("Manual Real-Time Tuning"),
      tr("Enforces the torque lateral controller to use the fixed values instead of the learned values from Self-Tune. Enabling this toggle overrides Self-Tune values."),
      "../assets/offroad/icon_blank.png",
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
    "EnableMads", "CustomOffsets", "EnforceTorqueLateral", "SpeedLimitPercOffset", "SpeedLimitControl",
    "CustomTorqueLateral", "LiveTorque", "TorquedOverride"
  };

  // toggle for offroadTransition when going onroad/offroad
  std::vector<std::string> toggleOffroad{
    "EnableMads", "DisengageLateralOnBrake", "AccMadsCombo", "MadsCruiseMain", "BelowSpeedPause", "EnforceTorqueLateral",
    "LiveTorqueRelaxed"
  };

  // Controls: Camera Offset (cm)
  camera_offset = new CameraOffset();
  connect(camera_offset, &SPOptionControl::updateLabels, camera_offset, &CameraOffset::refresh);

  // Controls: Path Offset (cm)
  path_offset = new PathOffset();
  connect(path_offset, &SPOptionControl::updateLabels, path_offset, &PathOffset::refresh);

  // Controls: Auto Lane Change Timer
  auto_lane_change_timer = new AutoLaneChangeTimer();
  auto_lane_change_timer->setUpdateOtherToggles(true);
  connect(auto_lane_change_timer, &SPOptionControl::updateLabels, auto_lane_change_timer, &AutoLaneChangeTimer::refresh);
  connect(auto_lane_change_timer, &AutoLaneChangeTimer::updateOtherToggles, this, &SPControlsPanel::updateToggles);

  // Controls: Speed Limit Offset Type
  slo_type = new SpeedLimitOffsetType();
  slo_type->setUpdateOtherToggles(true);
  connect(slo_type, &SPOptionControl::updateLabels, slo_type, &SpeedLimitOffsetType::refresh);
  connect(slo_type, &SPOptionControl::updateOtherToggles, this, &SPControlsPanel::updateToggles);

  // Controls: Speed Limit Offset Values (% or actual value)
  slvo = new SpeedLimitValueOffset();
  connect(slvo, &SPOptionControl::updateLabels, slvo, &SpeedLimitValueOffset::refresh);

  // Controls: Torque - FRICTION
  friction = new TorqueFriction();
  connect(friction, &SPOptionControl::updateLabels, friction, &TorqueFriction::refresh);

  // Controls: Torque - LAT_ACCEL_FACTOR
  lat_accel_factor = new TorqueMaxLatAccel();
  connect(lat_accel_factor, &SPOptionControl::updateLabels, lat_accel_factor, &TorqueMaxLatAccel::refresh);

  std::vector<QString> dlp_settings_texts{tr("Laneful"), tr("Laneless"), tr("Auto")};
  dlp_settings = new ButtonParamControl(
    "DynamicLaneProfile", "Dynamic Lane Profile", "Default is Laneless. In Auto mode, sunnnypilot dynamically chooses between Laneline or Laneless model based on lane recognition confidence level on road and certain conditions.",
    "../assets/offroad/icon_blank.png",
    dlp_settings_texts
  );
  dlp_settings->showDescription();

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControl(param, title, desc, icon, this);

    addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "RoadEdge") {
      // Controls: Dynamic Lane Profile group
      addItem(dlp_settings);
    }

    if (param == "CustomOffsets") {
      // Controls: Camera Offset (cm)
      addItem(camera_offset);

      // Controls: Path Offset (cm)
      addItem(path_offset);

      // Controls: Auto Lane Change Timer
      addItem(auto_lane_change_timer);
    }

    if (param == "TorquedOverride") {
      // Control: FRICTION
      addItem(friction);

      // Controls: LAT_ACCEL_FACTOR
      addItem(lat_accel_factor);
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

    // trigger offroadTransition when going onroad/offroad
    if (std::find(toggleOffroad.begin(), toggleOffroad.end(), param.toStdString()) != toggleOffroad.end()) {
      connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
        toggle->setEnabled(offroad);
      });
    }
  }

  toggles["EnableMads"]->setConfirmation(true, false);
  toggles["DisengageLateralOnBrake"]->setConfirmation(true, false);

  connect(toggles["OsmLocalDb"], &ToggleControl::toggleFlipped, [=](bool state) {
    if (!state) {
      params.remove("OsmLocalDb");
    }
  });

  // update "FRICTION" and "LAT_ACCEL_FACTOR" titles when going onroad/offroad
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    friction->setEnabled(offroad);
    lat_accel_factor->setEnabled(offroad);

    friction->refresh();
    lat_accel_factor->refresh();
  });

  // update "FRICTION" and "LAT_ACCEL_FACTOR" titles when TorquedOverride is flipped
  connect(toggles["TorquedOverride"], &ToggleControl::toggleFlipped, [=](bool state) {
    friction->setEnabled(params.getBool("IsOffroad") || state);
    lat_accel_factor->setEnabled(params.getBool("IsOffroad") || state);

    friction->setTitle(state ? "FRICTION - Live && Offline" : "FRICTION - Offline Only");
    lat_accel_factor->setTitle(state ? "LAT_ACCEL_FACTOR - Live && Offline" : "LAT_ACCEL_FACTOR - Offline Only");

    friction->refresh();
    lat_accel_factor->refresh();
  });

  param_watcher = new ParamWatcher(this);

  QObject::connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    updateToggles();
    updateButtons();
  });
}

void SPControlsPanel::showEvent(QShowEvent *event) {
  updateToggles();
  updateButtons();
}

void SPControlsPanel::updateToggles() {
  // toggle names to update when EnableMads is flipped
  std::vector<std::string> enableMadsGroup{"DisengageLateralOnBrake", "AccMadsCombo", "MadsCruiseMain"};
  for (const auto& enableMadstoggle : enableMadsGroup) {
    if (toggles.find(enableMadstoggle) != toggles.end()) {
      toggles[enableMadstoggle]->setVisible(toggles["EnableMads"]->isToggled());
    }
  }

  // toggle VisionCurveLaneless when DynamicLaneProfile == 2/Auto
  toggles["VisionCurveLaneless"]->setEnabled(QString::fromStdString(params.get("DynamicLaneProfile")) == "2");

  // toggle names to update when CustomOffsets is flipped
  std::vector<AbstractControl*> customOffsetsGroup{camera_offset, path_offset};
  for (const auto& customOffsetsControl : customOffsetsGroup) {
    customOffsetsControl->setVisible(toggles["CustomOffsets"]->isToggled());
  }

  // toggle names to update when AutoLaneChangeTimer is not "Nudge"
  toggles["AutoLaneChangeBsmDelay"]->setVisible(QString::fromStdString(params.get("AutoLaneChangeTimer")) != "0");

  auto enforce_torque_lateral = toggles["EnforceTorqueLateral"];
  auto custom_torque_lateral = toggles["CustomTorqueLateral"];
  auto live_torque = toggles["LiveTorque"];
  auto live_torque_relaxed = toggles["LiveTorqueRelaxed"];
  auto torqued_override = toggles["TorquedOverride"];

  auto speed_limit_control = toggles["SpeedLimitControl"];
  auto speed_limit_perc_offset = toggles["SpeedLimitPercOffset"];

  // toggle names to update when EnforceTorqueLateral is flipped
  std::vector<std::string> enforceTorqueGroup{"CustomTorqueLateral", "LiveTorque", "TorquedOverride"};
  for (const auto& enforceTorqueToggle : enforceTorqueGroup) {
    if (toggles.find(enforceTorqueToggle) != toggles.end()) {
      toggles[enforceTorqueToggle]->setVisible(enforce_torque_lateral->isToggled());
    }
  }

  // toggle names to update when CustomTorqueLateral is flipped
  std::vector<AbstractControl*> customTorqueGroup{friction, lat_accel_factor};
  for (const auto& customTorqueControl : customTorqueGroup) {
    customTorqueControl->setVisible(custom_torque_lateral->isToggled());
  }

  // toggle names to update when SpeedLimitControl is flipped
  std::vector<AbstractControl*> speedLimitControlGroup{slo_type, slvo};
  for (const auto& speedLimitControl : speedLimitControlGroup) {
    speedLimitControl->setVisible(speed_limit_control->isToggled());
  }

  if (enforce_torque_lateral->isToggled()) {
    live_torque_relaxed->setVisible(live_torque->isToggled());
    torqued_override->setVisible(custom_torque_lateral->isToggled());
  } else {
    params.putBool("LiveTorque", false);
    params.putBool("CustomTorqueLateral", false);
    for (const auto& customTorqueControl : customTorqueGroup) {
      customTorqueControl->setVisible(false);
    }
  }

  if (speed_limit_control->isToggled()) {
    if (speed_limit_perc_offset->isToggled()) {
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
  speed_limit_perc_offset->setVisible(speed_limit_control->isToggled());

  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    if (CP.getSteerControlType() == cereal::CarParams::SteerControlType::ANGLE) {
      enforce_torque_lateral->setEnabled(false);
      params.remove("EnforceTorqueLateral");
    }
  }
}

void SPControlsPanel::updateButtons() {
  param_watcher->addParam("DynamicLaneProfile");

  if (!isVisible()) return;

  dlp_settings->setButton("DynamicLaneProfile");
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

  // Hyundai/Kia/Genesis
  addItem(new LabelControl(tr("Hyundai/Kia/Genesis")));
  auto hkgSmoothStop = new ParamControl(
    "HkgSmoothStop",
    "HKG CAN: Smoother Stopping Performance (Beta)",
    "Smoother stopping behind a stopped car or desired stopping event. This is only applicable to HKG CAN platforms using openpilot longitudinal control.",
    "../assets/offroad/icon_blank.png"
  );
  hkgSmoothStop->setConfirmation(true, false);
  addItem(hkgSmoothStop);

  // Subaru
  addItem(new LabelControl(tr("Subaru")));
  auto subaruManualParkingBrakeSng = new ParamControl(
    "SubaruManualParkingBrakeSng",
    tr("Manual Parking Brake: Stop and Go (Beta)"),
    tr("Experimental feature to enable stop and go for Subaru Global models with manual handbrake. Models with electric parking brake should keep this disabled. Thanks to martinl for this implementation!"),
    "../assets/offroad/icon_blank.png"
  );
  subaruManualParkingBrakeSng->setConfirmation(true, false);
  addItem(subaruManualParkingBrakeSng);

  // Toyota/Lexus
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

  auto toyotaSngHack = new ParamControl(
    "ToyotaSnG",
    "Enable Stop and Go Hack",
    "sunnypilot will allow some Toyota/Lexus cars to auto resume during stop and go traffic. This feature is only applicable to certain models. Use at your own risk.",
    "../assets/offroad/icon_blank.png"
  );
  toyotaSngHack->setConfirmation(true, false);
  addItem(toyotaSngHack);

  // trigger offroadTransition when going onroad/offroad
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    hkgSmoothStop->setEnabled(offroad);
    toyotaTss2LongTune->setEnabled(offroad);
    toyotaSngHack->setEnabled(offroad);
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
    {
      "Map3DBuildings",
      tr("Map: Display 3D Buildings"),
      tr("Parse and display 3D buildings on map. Thanks to jakethesnake420 for this implementation."),
      "../assets/img_map.png",
    },
  };

  // Visuals: Developer UI Info (Dev UI)
  dev_ui_info = new DevUiInfo();
  connect(dev_ui_info, &SPOptionControl::updateLabels, dev_ui_info, &DevUiInfo::refresh);

  // Visuals: Display Metrics above Chevron
  chevron_info = new ChevronInfo();
  connect(chevron_info, &SPOptionControl::updateLabels, chevron_info, &ChevronInfo::refresh);

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

  std::vector<QString> sidebar_temp_texts{tr("Off"), tr("Ambient"), tr("RAM"), tr("CPU"), tr("GPU"), tr("Max")};
  sidebar_temp_setting = new ButtonParamControl(
    "SidebarTemperatureOptions", "Display Temperature on Sidebar", "",
    "../assets/offroad/icon_blank.png",
    sidebar_temp_texts,
    255
  );
  sidebar_temp_setting->showDescription();
  addItem(sidebar_temp_setting);

  // trigger updateToggles() when toggleFlipped
  connect(toggles["DevUI"], &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });

  // trigger offroadTransition when going onroad/offroad
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
  });
}

void SPVisualsPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void SPVisualsPanel::updateToggles() {
  dev_ui_info->setVisible(toggles["DevUI"]->isToggled());
}

// Max Time Offroad (Shutdown timer)
MaxTimeOffroad::MaxTimeOffroad() : SPOptionControl (
  "MaxTimeOffroad",
  tr("Max Time Offroad"),
  tr("Device is automatically turned off after a set time when the engine is turned off (off-road) after driving (on-road)."),
  "../assets/offroad/icon_metric.png",
  {0, 12}) {

  refresh();
}

void MaxTimeOffroad::refresh() {
  QString option = QString::fromStdString(params.get("MaxTimeOffroad"));
  QString second = tr("s");
  QString minute = tr("m");
  QString hour = tr("h");
  if (option == "0") {
    setLabel(tr("Always On"));
  } else if (option == "1") {
    setLabel(tr("Immediate"));
  } else if (option == "2") {
    setLabel("30" + second);
  } else if (option == "3") {
    setLabel("1" + minute);
  } else if (option == "4") {
    setLabel("3" + minute);
  } else if (option == "5") {
    setLabel("5" + minute);
  } else if (option == "6") {
    setLabel("10" + minute);
  } else if (option == "7") {
    setLabel("30" + minute);
  } else if (option == "8") {
    setLabel("1" + hour);
  } else if (option == "9") {
    setLabel("3" + hour);
  } else if (option == "10") {
    setLabel("5" + hour);
  } else if (option == "11") {
    setLabel("10" + hour);
  } else if (option == "12") {
    setLabel("30" + hour);
  }
}

// Onroad Screen Off (Auto Onroad Screen Timer)
OnroadScreenOff::OnroadScreenOff() : SPOptionControl (
  "OnroadScreenOff",
  tr("Driving Screen Off Timer"),
  tr("Turn off the device screen or reduce brightness to protect the screen after driving starts. It automatically brightens or turns on when a touch or event occurs."),
  "../assets/offroad/icon_metric.png",
  {-2, 10}) {

  refresh();
}

void OnroadScreenOff::refresh() {
  QString option = QString::fromStdString(params.get("OnroadScreenOff"));
  QString second = tr("s");
  if (option == "-2") {
    setLabel(tr("Always On"));
  } else if (option == "-1") {
    setLabel("15" + second);
  } else if (option == "0") {
    setLabel("30" + second);
  } else {
    setLabel(option + "min(s)");
  }
}

// Onroad Screen Off Brightness
OnroadScreenOffBrightness::OnroadScreenOffBrightness() : SPOptionControl (
  "OnroadScreenOffBrightness",
  tr("Driving Screen Off Brightness (%)"),
  tr("When using the Driving Screen Off feature, the brightness is reduced according to the automatic brightness ratio."),
  "../assets/offroad/icon_blank.png",
  {0, 100},
  10) {

  refresh();
}

void OnroadScreenOffBrightness::refresh() {
  QString option = QString::fromStdString(params.get("OnroadScreenOffBrightness"));
  if (option == "0") {
    setLabel(tr("Dark"));
  } else {
    setLabel(option);
  }
}

// Brightness Control (Global)
BrightnessControl::BrightnessControl() : SPOptionControl (
  "BrightnessControl",
  tr("Brightness Control (Global, %)"),
  tr("Manually adjusts the global brightness of the screen."),
  "../assets/offroad/icon_metric.png",
  {0, 100},
  5) {

  refresh();
}

void BrightnessControl::refresh() {
  QString option = QString::fromStdString(params.get("BrightnessControl"));
  if (option == "0") {
    setLabel(tr("Auto"));
  } else {
    setLabel(option);
  }
}

// Camera Offset Value
CameraOffset::CameraOffset() : SPOptionControl (
  "CameraOffset",
  tr("Camera Offset - Laneful Only (cm)"),
  tr("Hack to trick vehicle to be left or right biased in its lane. Decreasing the value will make the car keep more left, increasing will make it keep more right. Changes take effect immediately. Default: +4 cm"),
  "../assets/offroad/icon_blank.png",
  {-20, 20}) {

  refresh();
}

void CameraOffset::refresh() {
  QString option = QString::fromStdString(params.get("CameraOffset"));
  setLabel(option);
}

// Path Offset Value
PathOffset::PathOffset() : SPOptionControl (
  "PathOffset",
  tr("Path Offset (cm)"),
  tr("Hack to trick the model path to be left or right biased of the lane. Decreasing the value will shift the model more left, increasing will shift the model more right. Changes take effect immediately."),
  "../assets/offroad/icon_blank.png",
  {-10, 10}) {

  refresh();
}

void PathOffset::refresh() {
  QString option = QString::fromStdString(params.get("PathOffset"));
  setLabel(option);
}

// Auto Lane Change Timer (ALCT)
AutoLaneChangeTimer::AutoLaneChangeTimer() : SPOptionControl (
  "AutoLaneChangeTimer",
  tr("Auto Lane Change Timer"),
  tr("Set a timer to delay the auto lane change operation when the blinker is used. No nudge on the steering wheel is required to auto lane change if a timer is set.\nPlease use caution when using this feature. Only use the blinker when traffic and road conditions permit."),
  "../assets/offroad/icon_road.png",
  {0, 5}) {

  refresh();
}

void AutoLaneChangeTimer::refresh() {
  QString option = QString::fromStdString(params.get("AutoLaneChangeTimer"));
  QString second = tr("s");
  if (option == "0") {
    setLabel(tr("Nudge"));
  } else if (option == "1") {
    setLabel(tr("Nudgeless"));
  } else if (option == "2") {
    setLabel("0.5" + second);
  } else if (option == "3") {
    setLabel("1" + second);
  } else if (option == "4") {
    setLabel("1.5" + second);
  } else {
    setLabel("2" + second);
  }
}

TorqueFriction::TorqueFriction() : SPOptionControl (
  "TorqueFriction",
  tr("FRICTION"),
  tr("Adjust Friction for the Torque Lateral Controller. <b>Live</b>: Override self-tune values; <b>Offline</b>: Override self-tune offline values at car restart."),
  "../assets/offroad/icon_blank.png",
  {0, 50}) {

  refresh();
}

void TorqueFriction::refresh() {
  QString torqueFrictionStr = QString::fromStdString(params.get("TorqueFriction"));
  float valuef = torqueFrictionStr.toInt() * 0.01;
  setTitle(params.getBool("TorquedOverride") ? "FRICTION - Live && Offline" : "FRICTION - Offline Only");
  setLabel(QString::number(valuef));
}

TorqueMaxLatAccel::TorqueMaxLatAccel() : SPOptionControl (
  "TorqueMaxLatAccel",
  tr("LAT_ACCEL_FACTOR"),
  tr("Adjust Max Lateral Acceleration for the Torque Lateral Controller. <b>Live</b>: Override self-tune values; <b>Offline</b>: Override self-tune offline values at car restart."),
  "../assets/offroad/icon_blank.png",
  {1, 500}) {

  refresh();
}

void TorqueMaxLatAccel::refresh() {
  QString torqueMaxLatAccelStr = QString::fromStdString(params.get("TorqueMaxLatAccel"));
  float valuef = torqueMaxLatAccelStr.toInt() * 0.01;
  setTitle(params.getBool("TorquedOverride") ? "LAT_ACCEL_FACTOR - Live && Offline" : "LAT_ACCEL_FACTOR - Offline Only");
  setLabel(QString::number(valuef));
}

// Speed Limit Control Custom Offset Type
SpeedLimitOffsetType::SpeedLimitOffsetType() : SPOptionControl (
  "SpeedLimitOffsetType",
  tr("Speed Limit Offset Type"),
  QString("%1<br>"
          "%2")
  .arg(tr("Set speed limit higher or lower than actual speed limit for a more personalized drive."))
  .arg(tr("To use this feature, turn off \"Enable Speed Limit % Offset\".")),
  "../assets/offroad/icon_speed_limit.png",
  {0, 2}) {

  refresh();
}

void SpeedLimitOffsetType::refresh() {
  QString option = QString::fromStdString(params.get("SpeedLimitOffsetType"));
  if (option == "0") {
    setLabel(tr("Default"));
  } else if (option == "1") {
    setLabel(tr("Value"));
  } else if (option == "2") {
    setLabel(tr("%"));
  }
}

// Speed Limit Control Custom Offset
SpeedLimitValueOffset::SpeedLimitValueOffset() : SPOptionControl (
  "SpeedLimitValueOffset",
  "",
  "",
  "../assets/offroad/icon_blank.png",
  {-30, 30}) {

  refresh();
}

void SpeedLimitValueOffset::refresh() {
  QString option = QString::fromStdString(params.get("SpeedLimitValueOffset"));
  setLabel(option);
}

// Developer UI Info (Dev UI)
DevUiInfo::DevUiInfo() : SPOptionControl (
  "DevUIInfo",
  tr("Developer UI List"),
  tr("Select the number of lists of real-time parameters you would like to display on the sunnypilot screen while driving."),
  "../assets/offroad/icon_blank.png",
  {0, 1}) {

  refresh();
}

void DevUiInfo::refresh() {
  QString option = QString::fromStdString(params.get("DevUIInfo"));
  if (option == "0") {
    setLabel(tr("5 Metrics"));
  } else {
    setLabel(tr("10 Metrics"));
  }
}

// Display Metrics above Chevron
ChevronInfo::ChevronInfo() : SPOptionControl (
  "ChevronInfo",
  tr("Display Metrics above Chevron"),
  tr("Display useful metrics above the chevron that tracks the lead car (only applicable to cars with openpilot longitudinal control)."),
  "../assets/offroad/icon_calibration.png",
  {0, 2}) {

  refresh();
}

void ChevronInfo::refresh() {
  QString option = QString::fromStdString(params.get("ChevronInfo"));
  if (option == "0") {
    setLabel(tr("OFF"));
  } else if (option == "1") {
    setLabel(tr("Distance"));
  } else if (option == "2") {
    setLabel(tr("Speed"));
  }
}
