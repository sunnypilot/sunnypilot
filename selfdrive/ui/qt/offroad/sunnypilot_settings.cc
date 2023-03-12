#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <QFileInfo>
#include <QDateTime>

#include "common/watchdog.h"
#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/qt/offroad/sunnypilot_settings.h"
#include "selfdrive/ui/qt/widgets/input.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/util.h"

#include "selfdrive/ui/ui.h"

SPGeneralPanel::SPGeneralPanel(QWidget *parent) : QWidget(parent) {
  main_layout = new QVBoxLayout(this);

  // General: Quiet Drive
  main_layout->addWidget(new ParamControl(
    "QuietDrive",
    tr("Quiet Drive 🤫"),
    tr("sunnypilot will display alerts but only play the most important warning sounds. This feature can be toggled while the car is on."),
    "../assets/offroad/icon_mute.png"
  ));

  // General: Green Traffic Light Chime
  endToEndLongAlert = new ParamControl(
    "EndToEndLongAlert",
    tr("Green Traffic Light Chime (Beta)"),
    QString("%1<br>"
            "<h4>%2</h4><br>")
            .arg(tr("A chime will play when the traffic light you are waiting for turns green and you have no vehicle in front of you. If you are waiting behind another vehicle, the chime will play once the vehicle advances unless ACC is engaged."))
            .arg(tr("Note: This chime is only designed as a notification. It is the driver's responsibility to observe their environment and make decisions accordingly.")),
    "../assets/offroad/icon_road.png"
  );
  endToEndLongAlert->setConfirmation(true, false);
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(endToEndLongAlert);

  // General: Custom Boot Screen
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "CustomBootScreen",
    tr("Custom Boot Screen"),
    tr("Display sunnypilot welcome screen while booting the device."),
    "../assets/offroad/icon_shell.png"
  ));

  // General: Max Time Offroad (Shutdown timer)
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new MaxTimeOffroad());

  // General: Onroad Screen Off (Auto Onroad Screen Timer)
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new OnroadScreenOff());

  // General: Onroad Screen Off Brightness
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new OnroadScreenOffBrightness());

  // General: Brightness Control (Global)
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new BrightnessControl());

  // General: Disable Onroad Uploads
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "DisableOnroadUploads",
    tr("Disable Onroad Uploads"),
    tr("Disable uploads completely when onroad. Necessary to avoid high data usage when connected to Wi-Fi hotspot. Turn on this feature if you are looking to utilize map-based features, such as Speed Limit Control (SLC) and Map-based Turn Speed Control (MTSC)."),
    "../assets/offroad/icon_network.png"
  ));

  // General: Error Troubleshoot
  auto errorBtn = new ButtonControl(
    tr("Error Troubleshoot"),
    tr("VIEW"),
    tr("Display error from the tmux session when an error has occurred from a system process.")
  );
  QFileInfo file("/data/community/crashes/error.txt");
  QDateTime modifiedTime = file.lastModified();
  QString modified_time = modifiedTime.toString("yyyy-MM-dd hh:mm:ss ");
  connect(errorBtn, &ButtonControl::clicked, [=]() {
    const std::string txt = util::read_file("/data/community/crashes/error.txt");
    ConfirmationDialog::rich(modified_time + QString::fromStdString(txt), this);
  });
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(errorBtn);

  // General: Debug snapshot on screen center tap
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "EnableDebugSnapshot",
    tr("Debug snapshot on screen center tap"),
    tr("Stores snapshot file with current state of some modules."),
    "../assets/offroad/icon_calibration.png"
  ));
}

SPControlsPanel::SPControlsPanel(QWidget *parent) : QWidget(parent) {
  main_layout = new QVBoxLayout(this);

  // M.A.D.S.
  madsMainControl = new QWidget();
  madsSubControl = new QVBoxLayout(madsMainControl);
  // Controls: Enable M.A.D.S.
  madsControl = new ParamControl(
    "EnableMads",
    tr("Enable M.A.D.S."),
    tr("Enable the beloved M.A.D.S. feature. Disable toggle to revert back to stock openpilot engagement/disengagement."),
    "../assets/offroad/icon_openpilot.png"
  );
  madsControl->setConfirmation(true, false);
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    madsControl->setEnabled(offroad);
  });
  madsSubControl->setContentsMargins(QMargins());
  madsSubControl->addWidget(horizontal_line());

  // Controls: Disengage ALC On Brake Pedal
  disengageLateralOnBrake = new ParamControl(
    "DisengageLateralOnBrake",
    tr("Disengage ALC On Brake Pedal ℹ"),
    QString("%1<br>"
            "<h4>%2</h4><br>"
            "<h4>%3</h4><br>")
    .arg(tr("Define brake pedal interactions with sunnypilot when M.A.D.S. is enabled."))
    .arg(tr("Enabled: Pressing the brake pedal will disengage Automatic Lane Centering (ALC) on sunnypilot."))
    .arg(tr("Disabled: Pressing the brake pedal will <b>NOT</b> disengage Automatic Lane Centering (ALC) on sunnypilot.")),
    "../assets/offroad/icon_openpilot.png"
  );
  disengageLateralOnBrake->setConfirmation(true, false);
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    disengageLateralOnBrake->setEnabled(offroad);
  });
  madsSubControl->addWidget(disengageLateralOnBrake);
  madsSubControl->addWidget(horizontal_line());

  // Controls: Enable ACC+MADS with RES+/SET-
  accMadsCombo = new ParamControl(
    "AccMadsCombo",
    tr("Enable ACC+MADS with RES+/SET-"),
    QString("%1<br>"
            "<h4>%2</h4><br>")
    .arg(tr("Engage both M.A.D.S. and ACC with a single press of RES+ or SET- button."))
    .arg(tr("Note: Once M.A.D.S. is engaged via this mode, it will remain engaged until it is manually disabled via the M.A.D.S. button or car shut off.")),
    "../assets/offroad/icon_openpilot.png"
  );
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    accMadsCombo->setEnabled(offroad);
  });
  madsSubControl->addWidget(accMadsCombo);
  connect(madsControl, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });
  main_layout->addWidget(madsControl);
  main_layout->addWidget(madsMainControl);


  // Controls: Pause Lateral Below Speed w/ Blinker
  belowSpeed = new ParamControl(
    "BelowSpeedPause",
    tr("Pause Lateral Below Speed w/ Blinker"),
    tr("Enable this toggle to pause lateral actuation with blinker when traveling below 30 MPH or 50 KM/H."),
    "../assets/offroad/icon_openpilot.png"
  );
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    belowSpeed->setEnabled(offroad);
  });
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(belowSpeed);

  // D.L.P.
  dlpMain = new QWidget();
  dlpSub = new QVBoxLayout(dlpMain);
  // Controls: Enable Dynamic Lane Profile
  dlpControl = new ParamControl(
    "DynamicLaneProfileToggle",
    tr("Enable Dynamic Lane Profile"),
    tr("Enable toggle to use Dynamic Lane Profile. Disable toggle to use Laneless only."),
    "../assets/offroad/icon_road.png"
  );

  // Controls: Laneless for Curves in Auto lane
  dlpCurve = new ParamControl(
    "VisionCurveLaneless",
    tr("Laneless for Curves in \"Auto lane\""),
    tr("While in Auto Lane, switch to Laneless for current/future curves."),
    "../assets/offroad/icon_blank.png"
  );
  dlpSub->addWidget(horizontal_line());
  dlpSub->addWidget(dlpCurve);
  connect(dlpControl, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(dlpControl);
  main_layout->addWidget(dlpMain);


  // Custom Offsets
  customOffsetsMain = new QWidget();
  customOffsetsSub = new QVBoxLayout(customOffsetsMain);
  // Controls: Custom Offsets
  customOffsets = new ParamControl(
    "CustomOffsets",
    tr("Custom Offsets"),
    tr("Add custom offsets to Camera and Path in sunnypilot."),
    "../assets/offroad/icon_metric.png"
  );
  customOffsetsSub->setContentsMargins(QMargins());

  // Controls: Camera Offset (cm)
  customOffsetsSub->addWidget(horizontal_line());
  customOffsetsSub->addWidget(new CameraOffset());

  // Controls: Path Offset (cm)
  customOffsetsSub->addWidget(horizontal_line());
  customOffsetsSub->addWidget(new PathOffset());
  connect(customOffsets, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(customOffsets);
  main_layout->addWidget(customOffsetsMain);

  // Controls: Auto Lane Change Timer
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new AutoLaneChangeTimer());

  // G.A.C.
  gacMain = new QWidget();
  gacSub = new QVBoxLayout(gacMain);
  // Controls: Enable Gap Adjust Cruise
  gapAdjustCruise = new ParamControl(
    "GapAdjustCruise",
    tr("Enable Gap Adjust Cruise ℹ"),
    QString("%1<br>"
            "<h4>%2</h4>")
    .arg(tr("Enable the Interval button on the steering wheel to adjust the cruise gap."))
    .arg(tr("Only available to cars with openpilot Longitudinal Control")),
    "../assets/offroad/icon_dynamic_gac.png"
  );
  gapAdjustCruise->setConfirmation(true, false);
  gacSub->setContentsMargins(QMargins());

  // Controls: Mode
  gacSub->addWidget(horizontal_line());
  gacSub->addWidget(new GapAdjustCruiseMode());
  connect(gapAdjustCruise, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(gapAdjustCruise);
  main_layout->addWidget(gacMain);

  // Torque Lateral Control
  torqueMain = new QWidget();
  torqueSub = new QVBoxLayout(torqueMain);
  customTorqueMain = new QWidget();
  customTorqueSub = new QVBoxLayout(customTorqueMain);
  // Controls: Enforce Torque Lateral Control
  torqueLateral = new ParamControl(
    "EnforceTorqueLateral",
    tr("Enforce Torque Lateral Control"),
    tr("Enable this to enforce sunnypilot to steer with Torque lateral control."),
    "../assets/offroad/icon_calibration.png"
  );
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    torqueLateral->setEnabled(offroad);
  });
  // Torque Lateral Control Live Tune
  customTorqueLateral = new ParamControl(
    "CustomTorqueLateral",
    tr("Torque Lateral Control Live Tune"),
    tr("Enables live tune for Torque lateral control."),
    "../assets/offroad/icon_calibration.png"
  );
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    customTorqueLateral->setEnabled(offroad);
  });
  customTorqueSub->setContentsMargins(QMargins());
  // Control: FRICTION
  customTorqueSub->addWidget(horizontal_line());
  customTorqueSub->addWidget(new TorqueFriction());
  // Controls: LAT_ACCEL_FACTOR
  customTorqueSub->addWidget(horizontal_line());
  customTorqueSub->addWidget(new TorqueMaxLatAccel());
  connect(customTorqueLateral, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
    ConfirmationDialog::alert(tr("You must restart your car or your device to apply these changes."), this);
  });
  torqueSub->addWidget(horizontal_line());
  torqueSub->addWidget(customTorqueLateral);
  torqueSub->addWidget(customTorqueMain);
  // Controls: Torque Lateral Controller Self-Tune
  liveTorque = new ParamControl(
    "LiveTorque",
    tr("Torque Lateral Controller Self-Tune"),
    tr("Enables self-tune for Torque lateral control."),
    "../assets/offroad/icon_calibration.png"
  );
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    liveTorque->setEnabled(offroad);
  });
  connect(liveTorque, &ToggleControl::toggleFlipped, [=]() {
    updateToggles();
    ConfirmationDialog::alert(tr("You must restart your car or your device to apply these changes."), this);
  });
  torqueSub->addWidget(horizontal_line());
  torqueSub->addWidget(liveTorque);
  connect(torqueLateral, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(torqueLateral);
  main_layout->addWidget(torqueMain);


  // Controls: Enable Hands on Wheel Monitoring
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "HandsOnWheelMonitoring",
    tr("Enable Hands on Wheel Monitoring"),
    tr("Monitor and alert when driver is not keeping the hands on the steering wheel."),
    "../assets/offroad/icon_openpilot.png"
  ));

  // Controls: Enable Vision Based Turn Speed Control (V-TSC)
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "TurnVisionControl",
    tr("Enable Vision Based Turn Speed Control (V-TSC)"),
    tr("Use vision path predictions to estimate the appropriate speed to drive through turns ahead."),
    "../assets/offroad/icon_road.png"));

  // S.L.C.
  speedLimitMain = new QWidget();
  speedLimitSub = new QVBoxLayout(speedLimitMain);
  speedOffsetMain = new QWidget();
  speedOffsetSub = new QVBoxLayout(speedOffsetMain);
  speedOffsetValMain = new QWidget();
  speedOffsetValSub = new QVBoxLayout(speedOffsetValMain);
  // Controls: Enable Speed Limit Control (SLC)
  main_layout->addWidget(horizontal_line());
  speedLimitControl = new ParamControl(
    "SpeedLimitControl",
    tr("Enable Speed Limit Control (SLC)"),
    tr("Use speed limit signs information from map data and car interface (if applicable) to automatically adapt cruise speed to road limits."),
    "../assets/offroad/icon_speed_limit.png"
  );
  speedLimitSub->setContentsMargins(QMargins());

  // Controls: MUTCD: US/Canada\nVienna: Europe/Asia/etc.
  speedLimitSub->addWidget(horizontal_line());
  speedLimitSub->addWidget(new SpeedLimitStyle());

  // Controls: Enable Speed Limit Offset
  speedLimitSub->addWidget(horizontal_line());
  speedPercControl = new ParamControl(
    "SpeedLimitPercOffset",
    tr("Enable Speed Limit Offset"),
    tr("Set speed limit slightly higher than actual speed limit for a more natural drive."),
    "../assets/offroad/icon_speed_limit.png"
  );
  speedOffsetSub->setContentsMargins(QMargins());

  // Controls: Speed Limit Offset Type
  slo_type = new SpeedLimitOffsetType();
  speedOffsetSub->addWidget(horizontal_line());
  speedOffsetSub->addWidget(slo_type);

  speedOffsetValSub->setContentsMargins(QMargins());

  // Controls: Speed Limit Offset Values (% or actual value)
  slvo = new SpeedLimitValueOffset();
  speedOffsetValSub->addWidget(horizontal_line());
  speedOffsetValSub->addWidget(slvo);

  connect(slo_type, &SpeedLimitOffsetType::offsetTypeUpdated, this, &SPControlsPanel::updateToggles);

  speedOffsetSub->addWidget(speedOffsetValMain);

  connect(speedPercControl, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });

  speedLimitSub->addWidget(speedPercControl);
  speedLimitSub->addWidget(speedOffsetMain);

  connect(speedLimitControl, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });

  main_layout->addWidget(speedLimitControl);
  main_layout->addWidget(speedLimitMain);


  // Controls: Enable Map Data Turn Speed Control (M-TSC)
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "TurnSpeedControl",
    tr("Enable Map Data Turn Speed Control (M-TSC)"),
    tr("Use curvature information from map data to define speed limits to take turns ahead."),
    "../assets/offroad/icon_openpilot.png"
  ));

  // Controls: ACC +/-: Long Press Reverse
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "ReverseAccChange",
    tr("ACC +/-: Long Press Reverse"),
    QString("%1<br>"
            "<h4>%2</h4><br>"
            "<h4>%3</h4><br>")
    .arg(tr("Change the ACC +/- buttons behavior with cruise speed change in sunnypilot."))
    .arg(tr("Disabled (Stock): Short=1, Long = 5 (imperial) / 10 (metric)"))
    .arg(tr("Enabled: Short = 5 (imperial) / 10 (metric), Long=1")),
    "../assets/offroad/icon_acc_change.png"
  ));

  // Controls: OSM: Use Offline Database
  osmLocalDb = new ParamControl(
    "OsmLocalDb",
    tr("OSM: Use Offline Database"),
    "",
    "../assets/img_map.png"
  );
  connect(osmLocalDb, &ToggleControl::toggleFlipped, [=](bool state) {
    if (!state) params.remove("OsmLocalDb");
  });
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(osmLocalDb);
}

void SPControlsPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void SPControlsPanel::updateToggles() {
  madsMainControl->setVisible(params.getBool("EnableMads"));
  madsMainControl->update();

  dlpMain->setVisible(params.getBool("DynamicLaneProfileToggle"));
  dlpMain->update();

  customOffsetsMain->setVisible(params.getBool("CustomOffsets"));
  customOffsetsMain->update();

  gacMain->setVisible(params.getBool("GapAdjustCruise"));
  gacMain->update();

  customTorqueMain->setVisible(params.getBool("CustomTorqueLateral"));
  customTorqueMain->update();
  torqueMain->setVisible(params.getBool("EnforceTorqueLateral"));
  torqueMain->update();
  if (params.getBool("EnforceTorqueLateral")) {
    if (params.getBool("CustomTorqueLateral")) {
      liveTorque->setEnabled(false);
      params.putBool("LiveTorque", false);
    } else {
      liveTorque->setEnabled(true);
    }

    if (params.getBool("LiveTorque")) {
      customTorqueLateral->setEnabled(false);
      params.putBool("CustomTorqueLateral", false);
      customTorqueMain->setVisible(false);
    } else {
      customTorqueLateral->setEnabled(true);
    }

    liveTorque->refresh();
    customTorqueLateral->refresh();
  } else {
    params.putBool("LiveTorque", false);
    params.putBool("CustomTorqueLateral", false);
    customTorqueMain->setVisible(false);
  }

  speedOffsetValMain->setVisible(QString::fromStdString(params.get("SpeedLimitOffsetType")) != "0");
  speedOffsetValMain->update();
  speedOffsetMain->setVisible(params.getBool("SpeedLimitPercOffset"));
  speedOffsetMain->update();
  speedLimitMain->setVisible(params.getBool("SpeedLimitControl"));
  speedLimitMain->update();
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
  scroller->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
  fcr_layout->addWidget(scroller, 1);

  main_layout->addWidget(home);

  setStyleSheet(R"(
    #setCarBtn {
      font-size: 50px;
      margin: 0px;
      padding: 20px;
      border-width: 0;
      border-radius: 30px;
      color: #dddddd;
      background-color: #444444;
    }
  )");

  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(new LabelControl(tr("Toyota/Lexus")));
  stockLongToyota = new ParamControl(
    "StockLongToyota",
    "Enable Stock Toyota Longitudinal Control",
    "sunnypilot will <b>not</b> take over control of gas and brakes. Stock Toyota longitudinal control will be used.",
    "../assets/offroad/icon_blank.png"
  );
  stockLongToyota->setConfirmation(true, false);
  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(stockLongToyota);
  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(new LabelControl(tr("Volkswagen MQB/PQ")));
  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(new VwAccType());
}

SPVisualsPanel::SPVisualsPanel(QWidget *parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);

  // Visuals: Display Braking Status
  main_layout->addWidget(new ParamControl(
    "BrakeLights",
    tr("Display Braking Status"),
    tr("Enable this will turn the current speed value to red while the brake is used."),
    "../assets/offroad/icon_road.png"
  ));

  // Visuals: Display Stand Still Timer
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "StandStillTimer",
    tr("Display Stand Still Timer"),
    tr("Enable this will display time spent at a stop (i.e., at a stop lights, stop signs, traffic congestions)."),
    "../assets/offroad/icon_road.png"
  ));

  // Dev U.I.
  devUiMain = new QWidget();
  devUiSub = new QVBoxLayout(devUiMain);
  // Visuals: Show Developer UI
  devUi = new ParamControl(
    "DevUI",
    tr("Show Developer UI"),
    tr("Show developer UI (Dev UI) for real-time parameters from various sources."),
    "../assets/offroad/icon_calibration.png"
  );
  devUiSub->setContentsMargins(QMargins());
  devUiSub->addWidget(horizontal_line());
  devUiSub->addWidget(new DevUiInfo());
  connect(devUi, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(devUi);
  main_layout->addWidget(devUiMain);


  // Visuals: OSM: Show debug UI elements
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "ShowDebugUI",
    tr("OSM: Show debug UI elements"),
    tr("OSM: Show UI elements that aid debugging."),
    "../assets/offroad/icon_calibration.png"
  ));

  // Mapbox
  mapboxMain = new QWidget();
  mapboxSub = new QVBoxLayout(mapboxMain);
  // Visuals: Enable Mapbox Navigation
  customMapbox = new ParamControl(
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
    "../assets/img_map.png"
  );
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    customMapbox->setEnabled(offroad);
  });
  connect(customMapbox, &ToggleControl::toggleFlipped, [=](bool state) {
    if (ConfirmationDialog::confirm(tr("\"Enable Mapbox Navigation\"\nYou must restart your car or your device to apply these changes.\nReboot now?"), "Reboot", parent)) {
      Hardware::reboot();
    }
  });
  mapboxFullScreen = new ParamControl(
    "MapboxFullScreen",
    "Display Navigation Full Screen",
    "Enable this will display the built-in navigation in full screen.\nTo switch back to driving view, tap on the border edge.",
    "../assets/offroad/icon_blank.png"
  );
  connect(mapboxFullScreen, &ToggleControl::toggleFlipped, [=](bool state) {
    ConfirmationDialog::alert("\"Enable Mapbox Navigation\"\nEnable this will display the built-in navigation in full screen.\nTo switch back to driving view, tap on the border edge.", this);
  });
  mapboxSub->setContentsMargins(QMargins());
  mapboxSub->addWidget(horizontal_line());
  mapboxSub->addWidget(mapboxFullScreen);
  QObject::connect(customMapbox, &ToggleControl::toggleFlipped, [=](bool state) {
    updateToggles();
  });
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(customMapbox);
  main_layout->addWidget(mapboxMain);

  // Visuals: Speedometer: Display True Speed
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "TrueVEgoUi",
    tr("Speedometer: Display True Speed"),
    tr("Display the true vehicle current speed from wheel speed sensors."),
    "../assets/offroad/icon_openpilot.png"
  ));

  // Visuals: Speedometer: Hide from Onroad Screen
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl(
    "HideVEgoUi",
    tr("Speedometer: Hide from Onroad Screen"),
    "",
    "../assets/offroad/icon_openpilot.png"
  ));

  // Visuals: Display Metrics above Chevron
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ChevronInfo());
}

void SPVisualsPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void SPVisualsPanel::updateToggles() {
  devUiMain->setVisible(params.getBool("DevUI"));
  devUiMain->update();

  mapboxMain->setVisible(params.getBool("CustomMapbox"));
  mapboxMain->update();
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

// Volkswagen - MQB ACC Type
VwAccType::VwAccType() : AbstractControl(
  tr("Short Press +1/-1 Type"),
  tr("Define the type of ACC control your car has with short press to +1 or -1."),
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
    auto str = QString::fromStdString(params.get("VwAccType"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("VwAccType", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("VwAccType"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 1 ) {
      value = 1;
    }
    QString values = QString::number(value);
    params.put("VwAccType", values.toStdString());
    refresh();
  });
  refresh();
}

void VwAccType::refresh() {
  QString option = QString::fromStdString(params.get("VwAccType"));
  if (option == "0") {
    label.setText(tr("+/-"));
  } else if (option == "1") {
    label.setText(tr("RES/SET"));
  }
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
