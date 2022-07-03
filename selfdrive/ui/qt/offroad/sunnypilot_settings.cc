#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <QComboBox>
#include <QAbstractItemView>
#include <QScroller>
#include <QListView>
#include <QListWidget>

#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/qt/offroad/sunnypilot_settings.h"
#include "selfdrive/ui/qt/widgets/input.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

#include "selfdrive/ui/ui.h"

static QStringList get_list(const char* path) {
  QStringList stringList;
  QFile textFile(path);
  if (textFile.open(QIODevice::ReadOnly)) {
    QTextStream textStream(&textFile);
    while (true) {
      QString line = textStream.readLine();
      if (line.isNull())
        break;
      else
        stringList.append(line);
    }
  }

  return stringList;
}

ForceCarRecognition::ForceCarRecognition(QWidget* parent): QWidget(parent) {

  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setMargin(20);
  main_layout->setSpacing(20);

  QPushButton* back = new QPushButton("Back");
  back->setObjectName("backBtn");
  back->setFixedSize(500, 100);
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  QListWidget* list = new QListWidget();
  list->setStyleSheet("QListView {padding: 40px; background-color: #393939; border-radius: 15px; height: 140px;} QListView::item{height: 100px}");
  QScroller::grabGesture(list->viewport(), QScroller::LeftMouseButtonGesture);
  list->setVerticalScrollMode(QAbstractItemView::ScrollPerPixel);

  list->addItem("[-Not selected-]");

  QStringList items = get_list("/data/params/d/Cars");
  list->addItems(items);
  list->setCurrentRow(0);

  QString set = QString::fromStdString(Params().get("CarModel"));

  int index = 0;
  for (QString item : items) {
    if (set == item) {
      list->setCurrentRow(index + 1);
      break;
    }
    index++;
  }

  QObject::connect(list, QOverload<QListWidgetItem*>::of(&QListWidget::itemClicked),
    [=](QListWidgetItem* item){

    if (list->currentRow() == 0)
      Params().remove("CarModel");
    else
      Params().put("CarModel", list->currentItem()->text().toStdString());

    emit selectedCar();
    });

  main_layout->addWidget(list);
}

SPGeneralPanel::SPGeneralPanel(QWidget* parent) : QWidget(parent) {

  QVBoxLayout* main_layout = new QVBoxLayout(this);
  QWidget* uploadRawMain = new QWidget();
  QVBoxLayout* uploadRawSub = new QVBoxLayout();

  main_layout->addWidget(new ParamControl("QuietDrive",
                                          "Quiet Drive 🤫",
                                          "sunnypilot will display alerts but only play the most important warning sounds. This feature can be toggled while the car is on.",
                                          "../assets/offroad/icon_mute.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("PrebuiltOn",
                                          "Fast Boot (Prebuilt)",
                                          "sunnypilot will fast boot by creating a Prebuilt file. Note: Turn off this feature if you have made any UI changes!",
                                          "../assets/offroad/icon_shell.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new MaxTimeOffroad());
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new OnroadScreenOff());
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new OnroadScreenOffBrightness());
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new BrightnessControl());
  main_layout->addWidget(horizontal_line());
  ParamControl *uploadRaw = new ParamControl("UploadRaw",
                                             "Upload Raw Logs",
                                             "Upload full logs and full resolution video by default while on Wi-Fi. If not enabled, individual logs can be marked for upload at useradmin.comma.ai.",
                                             "../assets/offroad/icon_network.png");
  uploadRawSub->setContentsMargins(QMargins());
  uploadRawSub->addWidget(horizontal_line());
  uploadRawSub->addWidget(new ParamControl("UploadHiRes",
                                           "Upload Full Resolution Video",
                                           "Upload full resolution video by default while on Wi-Fi, along with \"Upload Raw Logs\". If not enabled, individual videos can be marked for upload at useradmin.comma.ai.",
                                           "../assets/offroad/icon_network.png"));
  uploadRawMain->setLayout(uploadRawSub);
  QObject::connect(uploadRaw, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      uploadRawMain->show();
    } else {
      uploadRawMain->hide();
    }
  });

  main_layout->addWidget(uploadRaw);
  main_layout->addWidget(uploadRawMain);

  if (!Params().getBool("UploadRaw"))
    uploadRawMain->hide();
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("EnableUpdates",
                                          "Enable Updates",
                                          "Enable this toggle to receive updates for sunnypilot.",
                                          "../assets/offroad/icon_network.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("DisableOnroadUploads",
                                          "Disable Onroad Uploads",
                                          "Disable uploads completely when onroad. Necessary to avoid high data usage when connected to Wi-Fi hotspot. Turn on this feature if you are looking to utilize map-based features, such as Speed Limit Control (SLC) and Map-based Turn Speed Control (MTSC).",
                                          "../assets/offroad/icon_network.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("ProcessNotRunningOff",
                                          "Bypass \"System Malfunction\" Error",
                                          "Prevent sunnypilot from returning the \"System Malfunction\" alert that hinders the ability use sunnypilot. Turn on this feature if you experience this alert frequently.",
                                          "../assets/offroad/icon_shell.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("ControlsdLaggingOff",
                                          "Bypass \"Controls Process Lagging\" Error",
                                          "Prevent sunnypilot from returning the \"Controls Process Lagging\" alert that hinders the ability use sunnypilot. Turn on this feature if you experience this alert frequently.",
                                          "../assets/offroad/icon_shell.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("CommIssueOff",
                                          "Bypass \"Communication Issue\" Error",
                                          "Prevent sunnypilot from returning the \"Communication Issue between Processes\" alert that hinders the ability use sunnypilot. Turn on this feature if you experience this alert frequently.",
                                          "../assets/offroad/icon_shell.png"));
  main_layout->addWidget(horizontal_line());
  ParamControl *noOffroadFix = new ParamControl("NoOffroadFix",
                                                "Fix sunnypilot No Offroad",
                                                "Enforce sunnypilot to go offroad and turns off after shutting down the car. This feature fixes non-official devices running sunnypilot without comma power.\nOnly enable this feature if your comma device does not shut down after the car is turned off.",
                                                "../assets/offroad/icon_shell.png");
  QObject::connect(noOffroadFix, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      ConfirmationDialog::alert("❗❗❗Fix sunnypilot No Offroad❗❗❗\nUnexpected shutdowns or reboots may occur if your device does not need this feature.\nTurn it off if you do not need this.", this);
    }
  });
  main_layout->addWidget(noOffroadFix);
  main_layout->addWidget(horizontal_line());
  ParamControl *timeValidBypass = new ParamControl("TimeValidBypass",
                                                   "Bypass Time and Date Check",
                                                   "Disable sunnypilot to perform time and date check. This feature allows your device to bypass the time and date check to use sunnypilot.\nOnly enable this feature if your device does not engage without the time and date check.",
                                                   "../assets/offroad/icon_calibration.png");
  QObject::connect(timeValidBypass, &ToggleControl::toggleFlipped, [=](bool state) {
    if (ConfirmationDialog::confirm("\"Bypass Time and Date Check\"\n\nReboot recommended.\nReboot?", parent)) {
      Hardware::reboot();
    }
  });
  main_layout->addWidget(timeValidBypass);
  main_layout->addWidget(horizontal_line());
  ParamControl *noGps = new ParamControl("noGps",
                                         "Bypass GPS Check",
                                         "Disable GPS check on sunnypilot. This feature allows your device to bypass the GPS check to use sunnypilot.\nOnly enable this feature if your device does not have a GPS chip.",
                                         "../assets/offroad/icon_calibration.png");
  QObject::connect(noGps, &ToggleControl::toggleFlipped, [=](bool state) {
    if (ConfirmationDialog::confirm("\"Bypass Time and Date Check\"\n\nReboot recommended.\nReboot?", parent)) {
      Hardware::reboot();
    }
  });
  main_layout->addWidget(noGps);
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("EnableDebugSnapshot",
                                          "Debug snapshot on screen center tap",
                                          "Stores snapshot file with current state of some modules.",
                                          "../assets/offroad/icon_calibration.png"));
  main_layout->addWidget(horizontal_line());
  ParamControl *customMapbox = new ParamControl("CustomMapbox",
                                                "Enable Mapbox Navigation",
                                                "Enable this will allow non-comma-Prime users to use Mapbox navigation on applicable comma devices.\nLearn more in sunnyhaibin's Discord server https://discord.gg/wRW3meAgtx",
                                                "../assets/offroad/icon_openpilot.png");
  QObject::connect(customMapbox, &ToggleControl::toggleFlipped, [=](bool state) {
    if (ConfirmationDialog::confirm("\"Enable Mapbox Navigation\"\n\nReboot required.\nReboot?", parent)) {
      Hardware::reboot();
    }
  });
  main_layout->addWidget(customMapbox);
}

SPControlsPanel::SPControlsPanel(QWidget* parent) : QWidget(parent) {

  QVBoxLayout* main_layout = new QVBoxLayout(this);
  QWidget* madsMainControl = new QWidget();
  QVBoxLayout* madsSubControl = new QVBoxLayout();
  QWidget* gacMain = new QWidget();
  QVBoxLayout* gacSub = new QVBoxLayout();
  QWidget* customOffsetsMain = new QWidget();
  QVBoxLayout* customOffsetsSub = new QVBoxLayout();
  QWidget* customTorqueMain = new QWidget();
  QVBoxLayout* customTorqueSub = new QVBoxLayout();
  QWidget* speedLimitMain = new QWidget();
  QVBoxLayout* speedLimitSub = new QVBoxLayout();
  QWidget* speedOffsetMain = new QWidget();
  QVBoxLayout* speedOffsetSub = new QVBoxLayout();
  QWidget* dlpMain = new QWidget();
  QVBoxLayout* dlpSub = new QVBoxLayout();

  ParamControl *madsControl = new ParamControl("EnableMads",
                                               "Enable M.A.D.S.",
                                               "Enable the beloved M.A.D.S. feature. Disable toggle to revert back to stock openpilot engagement/disengagement.",
                                               "../assets/offroad/icon_openpilot.png");
  QObject::connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    madsControl->setEnabled(offroad);
  });
  QObject::connect(madsControl, &ToggleControl::toggleFlipped, [=](bool state) {
    if (ConfirmationDialog::confirm("\"Enable M.A.D.S.\"\n\nReboot recommended.\nReboot?", parent)) {
      Hardware::reboot();
    }
  });
  madsSubControl->setContentsMargins(QMargins());
  madsSubControl->addWidget(horizontal_line());
  ParamControl *disengageLateralOnBrake = new ParamControl("DisengageLateralOnBrake",
                                                           "Disengage ALC* On Brake Pedal",
                                                           "*Automatic Lane Centering (ALC)\nWhen enabled, pressing the brake pedal will disengage Automatic Lane Centering (ALC) on sunnypilot.",
                                                           "../assets/offroad/icon_openpilot.png");
  QObject::connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    disengageLateralOnBrake->setEnabled(offroad);
  });
  QObject::connect(disengageLateralOnBrake, &ToggleControl::toggleFlipped, [=](bool state) {
    if (ConfirmationDialog::confirm("\"Disengage Lateral On Brake Pedal\"\n\nReboot recommended.\nReboot?", parent)) {
      Hardware::reboot();
    }
  });
  madsSubControl->addWidget(disengageLateralOnBrake);
  madsSubControl->addWidget(horizontal_line());
  ParamControl *accMadsCombo = new ParamControl("AccMadsCombo",
                                                "Enable ACC+MADS with RES+/SET-",
                                                "Engage both M.A.D.S. and ACC with a single press of RES+ or SET- button.\nNote: Once M.A.D.S. is engaged via this mode, it will remain engaged until it is manually disabled via the M.A.D.S. button or car shut off.",
                                                "../assets/offroad/icon_openpilot.png");
  QObject::connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    accMadsCombo->setEnabled(offroad);
  });
  madsSubControl->addWidget(accMadsCombo);
  madsMainControl->setLayout(madsSubControl);
  QObject::connect(madsControl, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      madsMainControl->show();
    } else {
      madsMainControl->hide();
    }
  });

  main_layout->addWidget(madsControl);
  main_layout->addWidget(madsMainControl);

  if (!Params().getBool("EnableMads"))
    madsMainControl->hide();

  main_layout->addWidget(horizontal_line());
  ParamControl *belowSpeed = new ParamControl("BelowSpeedPause",
                                              "Pause Lateral Below Speed w/ Blinker",
                                              "Enable this toggle to pause lateral actuation with blinker when traveling below 30 MPH or 50 KM/H.",
                                              "../assets/offroad/icon_openpilot.png");
  QObject::connect(belowSpeed, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      ConfirmationDialog::alert("\"Pause Lateral Below Speed w/ Blinker\"\nYou must restart your car or your device to apply these changes.", this);
    }
  });
  main_layout->addWidget(belowSpeed);
  ParamControl *dlpControl = new ParamControl("EndToEndToggle",
                                              "Enable Dynamic Lane Profile",
                                              "Enable toggle to use Dynamic Lane Profile. Disable toggle to use Laneline only.",
                                              "../assets/offroad/icon_road.png");
  QObject::connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    dlpControl->setEnabled(offroad);
  });
  ParamControl *dlpCurve = new ParamControl("VisionCurveLaneless",
                                            "Laneless for Curves in \"Auto lane\"",
                                            "While in Auto Lane, switch to Laneless for current/future curves.",
                                            "../assets/offroad/icon_blank.png");
  dlpSub->addWidget(dlpCurve);
  dlpMain->setLayout(dlpSub);
  QObject::connect(dlpControl, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      dlpMain->show();
    } else {
      dlpMain->hide();
    }
  });

  main_layout->addWidget(dlpControl);
  main_layout->addWidget(dlpMain);

  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new AutoLaneChangeTimer());
  main_layout->addWidget(horizontal_line());
  ParamControl *customOffsets = new ParamControl("CustomOffsets",
                                                 "Custom Offsets",
                                                 "Add custom offsets to Camera and Path in sunnypilot.",
                                                 "../assets/offroad/icon_metric.png");
  customOffsetsSub->setContentsMargins(QMargins());
  customOffsetsSub->addWidget(horizontal_line());
  customOffsetsSub->addWidget(new CameraOffset());
  customOffsetsSub->addWidget(horizontal_line());
  customOffsetsSub->addWidget(new PathOffset());
  customOffsetsMain->setLayout(customOffsetsSub);
  QObject::connect(customOffsets, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      customOffsetsMain->show();
    } else {
      customOffsetsMain->hide();
    }
  });

  main_layout->addWidget(customOffsets);
  main_layout->addWidget(customOffsetsMain);

  if (!Params().getBool("CustomOffsets"))
    customOffsetsMain->hide();
  main_layout->addWidget(horizontal_line());
  ParamControl *gapAdjustCruise = new ParamControl("GapAdjustCruise",
                                                   "Enable Gap Adjust Cruise*",
                                                   "Enable the Interval button on the steering wheel to adjust the cruise gap.\n*Only available to cars with openpilot Longitudinal Control*",
                                                   "../assets/offroad/icon_dynamic_gac.png");
  gacSub->setContentsMargins(QMargins());
  gacSub->addWidget(horizontal_line());
  gacSub->addWidget(new GapAdjustCruiseMode());
  gacMain->setLayout(gacSub);
  QObject::connect(gapAdjustCruise, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      gacMain->show();
    } else {
      gacMain->hide();
    }
  });

  main_layout->addWidget(gapAdjustCruise);
  main_layout->addWidget(gacMain);

  if (!Params().getBool("GapAdjustCruise"))
    gacMain->hide();
  main_layout->addWidget(horizontal_line());
  ParamControl *customTorqueLateral = new ParamControl("CustomTorqueLateral",
                                                       "Torque Lateral Control Live Tune",
                                                       "Enables live tune for Torque lateral control.",
                                                       "../assets/offroad/icon_calibration.png");
  customTorqueSub->setContentsMargins(QMargins());
  customTorqueSub->addWidget(horizontal_line());
  customTorqueSub->addWidget(new TorqueFriction());
  customTorqueSub->addWidget(horizontal_line());
  customTorqueSub->addWidget(new TorqueMaxLatAccel());
  customTorqueSub->addWidget(horizontal_line());
  customTorqueSub->addWidget(new TorqueDeadzoneDeg());
  customTorqueMain->setLayout(customTorqueSub);
  QObject::connect(customTorqueLateral, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      customTorqueMain->show();
    } else {
      customTorqueMain->hide();
    }
  });

  main_layout->addWidget(customTorqueLateral);
  main_layout->addWidget(customTorqueMain);

  if (!Params().getBool("CustomTorqueLateral"))
    customTorqueMain->hide();

  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("HandsOnWheelMonitoring",
                                          "Enable Hands on Wheel Monitoring",
                                          "Monitor and alert when driver is not keeping the hands on the steering wheel.",
                                          "../assets/offroad/icon_openpilot.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("VisionTurnSpeedControl",
                                          "Enable Vision Based Turn Speed Control (V-TSC)",
                                          "Use vision path predictions to estimate the appropriate speed to drive through turns ahead.",
                                          "../assets/offroad/icon_road.png"));
  main_layout->addWidget(horizontal_line());
  ParamControl *speedLimitControl = new ParamControl("SpeedLimitControl",
                                                     "Enable Speed Limit Control (SLC)",
                                                     "Use speed limit signs information from map data and car interface (if applicable) to automatically adapt cruise speed to road limits.",
                                                     "../assets/offroad/icon_speed_limit.png");
  speedLimitSub->setContentsMargins(QMargins());
  speedLimitSub->addWidget(horizontal_line());
  speedLimitSub->addWidget(new SpeedLimitStyle());
  speedLimitSub->addWidget(horizontal_line());
  ParamControl *speedPercControl = new ParamControl("SpeedLimitPercOffset",
                                                    "Enable Speed Limit % Offset",
                                                    "Set speed limit slightly higher than actual speed limit for a more natural drive.",
                                                    "../assets/offroad/icon_speed_limit.png");
  speedOffsetSub->setContentsMargins(QMargins());
  speedOffsetSub->addWidget(horizontal_line());
  speedOffsetSub->addWidget(new SpeedLimitValueOffset());
  speedOffsetMain->setLayout(speedOffsetSub);
  QObject::connect(speedPercControl, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      speedOffsetMain->hide();
    } else {
      speedOffsetMain->show();
    }
  });

  speedLimitSub->addWidget(speedPercControl);
  speedLimitSub->addWidget(speedOffsetMain);

  if (Params().getBool("SpeedLimitPercOffset"))
    speedOffsetMain->hide();

  speedLimitMain->setLayout(speedLimitSub);
  QObject::connect(speedLimitControl, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      speedLimitMain->show();
    } else {
      speedLimitMain->hide();
    }
  });

  main_layout->addWidget(speedLimitControl);
  main_layout->addWidget(speedLimitMain);

  if (!Params().getBool("SpeedLimitControl"))
    speedLimitMain->hide();
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("MapTurnSpeedControl",
                                          "Enable Map Data Turn Speed Control (M-TSC)",
                                          "Use curvature information from map data to define speed limits to take turns ahead.",
                                          "../assets/offroad/icon_openpilot.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("ReverseAccChange",
                                          "Enable Short Press for Higher ACC Value",
                                          "Change the ACC +/- buttons behavior with cruise speed change in openpilot.",
                                          "../assets/offroad/icon_acc_change.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new AccChangeType());
}

SPVehiclesPanel::SPVehiclesPanel(QWidget* parent) : QWidget(parent) {

  //QVBoxLayout* main_layout_init = new QVBoxLayout(this);
  main_layout = new QStackedLayout(this);
  home = new QWidget(this);
  QVBoxLayout* fcr_layout = new QVBoxLayout(home);
  fcr_layout->setContentsMargins(0, 20, 0, 20);

  QString set = QString::fromStdString(Params().get("CarModel"));

  QPushButton* setCarBtn = new QPushButton(set.length() ? set : "Set your car");
  setCarBtn->setObjectName("setCarBtn");
  setCarBtn->setStyleSheet("margin-right: 30px;");
  connect(setCarBtn, &QPushButton::clicked, [=]() { main_layout->setCurrentWidget(setCar); });
  fcr_layout->addSpacing(10);
  fcr_layout->addWidget(setCarBtn, 0, Qt::AlignRight);
  fcr_layout->addSpacing(10);

  home_widget = new QWidget(this);
  QVBoxLayout* toggle_layout = new QVBoxLayout(home_widget);
  home_widget->setObjectName("homeWidget");

  ScrollView *scroller = new ScrollView(home_widget);
  scroller->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
  fcr_layout->addWidget(scroller, 1);

  main_layout->addWidget(home);

  setCar = new ForceCarRecognition(this);
  connect(setCar, &ForceCarRecognition::backPress, [=]() { main_layout->setCurrentWidget(home); });
  connect(setCar, &ForceCarRecognition::selectedCar, [=]() {
    QString set = QString::fromStdString(Params().get("CarModel"));
    setCarBtn->setText(set.length() ? set : "Set your car");
    main_layout->setCurrentWidget(home);
  });
  main_layout->addWidget(setCar);

  QPalette pal = palette();
  pal.setColor(QPalette::Background, QColor(0x29, 0x29, 0x29));
  setAutoFillBackground(true);
  setPalette(pal);

  setStyleSheet(R"(
    #backBtn, #setCarBtn {
      font-size: 50px;
      margin: 0px;
      padding: 20px;
      border-width: 0;
      border-radius: 30px;
      color: #dddddd;
      background-color: #444444;
    }
  )");

  QList<ParamControl*> toggles;

  for (ParamControl *toggle : toggles) {
    if (main_layout->count() != 0) {
      toggle_layout->addWidget(horizontal_line());
    }
    toggle_layout->addWidget(toggle);
  }

  toggle_layout->addWidget(new LabelControl("Hyundai/Kia/Genesis (HKG)"));
  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(new ParamControl("EnhancedScc",
                                                 "Enhanced SCC Radar Interceptor*",
                                                 "openpilot will take over control of gas and brakes and will NOT disable the car's radar. This preserves AEB.\nOnly enable this feature if you have the Enhanced SCC Radar Interceptor hardware installed.\nWant to get one for your car? Reach out to sunnyhaibin#0865 on Discord for more information.",
                                                 "../assets/offroad/icon_blank.png"));
  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(new LabelControl("Toyota", ""));
  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(new ParamControl("StockLongToyota",
                                                 "Enable Stock Toyota Longitudinal Control",
                                                 "openpilot will *not* take over control of gas and brakes. Stock Toyota longitudinal control will be used.",
                                                 "../assets/offroad/icon_blank.png"));
  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(new ParamControl("CorollaIndi",
                                            "Corolla TSS2: Use birdman's INDI Lateral Tune",
                                            "Use birdman6450#7399's Corolla 2020 TSS2 Tune",
                                            "../assets/offroad/icon_blank.png"));
  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(new LabelControl("Volkswagen", ""));
  toggle_layout->addWidget(horizontal_line());
  toggle_layout->addWidget(new VwAccType());
}

SPVisualsPanel::SPVisualsPanel(QWidget* parent) : QWidget(parent) {

  QVBoxLayout* main_layout = new QVBoxLayout(this);
  QWidget* devUiMain = new QWidget();
  QVBoxLayout* devUiSub = new QVBoxLayout();

  ParamControl *devUi = new ParamControl("DevUI",
                                         "Show Developer UI",
                                         "Show developer UI (Dev UI) for real-time parameters from various sources.",
                                         "../assets/offroad/icon_calibration.png");
  devUiSub->setContentsMargins(QMargins());
  devUiSub->addWidget(horizontal_line());
  devUiSub->addWidget(new DevUiRow());
  devUiMain->setLayout(devUiSub);
  QObject::connect(devUi, &ToggleControl::toggleFlipped, [=](bool state) {
    if (state) {
      devUiMain->show();
    } else {
      devUiMain->hide();
    }
  });

  main_layout->addWidget(devUi);
  main_layout->addWidget(devUiMain);

  if (!Params().getBool("DevUI"))
    devUiMain->hide();
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("BrakeLights",
                                          "Display Braking Status",
                                          "Enable this will turn the current speed value to red while the brake is used.",
                                          "../assets/offroad/icon_road.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("StandStillTimer",
                                          "Display Stand Still Timer",
                                          "Enable this will display time spent at a stop (i.e., at a stop lights, stop signs, traffic congestions).",
                                          "../assets/offroad/icon_road.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("ShowDebugUI",
                                          "Show debug UI elements",
                                          "Show UI elements that aid debugging.",
                                          "../assets/offroad/icon_calibration.png"));
}


// Max Time Offroad (Shutdown timer)
MaxTimeOffroad::MaxTimeOffroad() : AbstractControl("Max Time Offroad",
                                                   "Device is automatically turned off after a set time when the engine is turned off (off-road) after driving (on-road).",
                                                   "../assets/offroad/icon_metric.png") {

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
  if (option == "0") {
    label.setText(QString::fromStdString("AlwaysOn"));
  } else if (option == "1") {
    label.setText(QString::fromStdString("Immediate"));
  } else if (option == "2") {
    label.setText(QString::fromStdString("30s"));
  } else if (option == "3") {
    label.setText(QString::fromStdString("1m"));
  } else if (option == "4") {
    label.setText(QString::fromStdString("3m"));
  } else if (option == "5") {
    label.setText(QString::fromStdString("5m"));
  } else if (option == "6") {
    label.setText(QString::fromStdString("10m"));
  } else if (option == "7") {
    label.setText(QString::fromStdString("30m"));
  } else if (option == "8") {
    label.setText(QString::fromStdString("1h"));
  } else if (option == "9") {
    label.setText(QString::fromStdString("3h"));
  } else if (option == "10") {
    label.setText(QString::fromStdString("5h"));
  } else if (option == "11") {
    label.setText(QString::fromStdString("10h"));
  } else if (option == "12") {
    label.setText(QString::fromStdString("30h"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Auto Lane Change Timer (ALCT)
AutoLaneChangeTimer::AutoLaneChangeTimer() : AbstractControl("Auto Lane Change Timer",
                                                             "Set a timer to delay the auto lane change operation when the blinker is used. No nudge on the steering wheel is required to auto lane change if a timer is set.\nPlease use caution when using this feature. Only use the blinker when traffic and road conditions permit.",
                                                             "../assets/offroad/icon_road.png") {

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
  if (option == "0") {
    label.setText(QString::fromStdString("Nudge"));
  } else if (option == "1") {
    label.setText(QString::fromStdString("Nudgeless"));
  } else if (option == "2") {
    label.setText(QString::fromStdString("0.5s"));
  } else if (option == "3") {
    label.setText(QString::fromStdString("1s"));
  } else if (option == "4") {
    label.setText(QString::fromStdString("1.5s"));
  } else {
    label.setText(QString::fromStdString("2s"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Onroad Screen Off (Auto Onroad Screen Timer)
OnroadScreenOff::OnroadScreenOff() : AbstractControl("Driving Screen Off Timer",
                                                     "Turn off the device screen or reduce brightness to protect the screen after driving starts. It automatically brightens or turns on when a touch or event occurs.",
                                                     "../assets/offroad/icon_metric.png") {

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
  if (option == "-2") {
    label.setText(QString::fromStdString("Always On"));
  } else if (option == "-1") {
    label.setText(QString::fromStdString("15s"));
  } else if (option == "0") {
    label.setText(QString::fromStdString("30s"));
  } else {
    label.setText(QString::fromStdString(params.get("OnroadScreenOff")) + "min(s)");
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Onroad Screen Off Brightness
OnroadScreenOffBrightness::OnroadScreenOffBrightness() : AbstractControl("Driving Screen Off Brightness (%)",
                                                                         "When using the Driving Screen Off feature, the brightness is reduced according to the automatic brightness ratio.",
                                                                         "../assets/offroad/icon_metric.png") {

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
    label.setText(QString::fromStdString("Dark"));
  } else {
    label.setText(QString::fromStdString(params.get("OnroadScreenOffBrightness")));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Brightness Control (Global)
BrightnessControl::BrightnessControl() : AbstractControl("Brightness Control (Global, %)",
                                                         "Manually adjusts the global brightness of the screen.",
                                                         "../assets/offroad/icon_metric.png") {

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
    label.setText(QString::fromStdString("Auto"));
  } else {
    label.setText(QString::fromStdString(params.get("BrightnessControl")));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Developer UI Rows (Dev UI)
DevUiRow::DevUiRow() : AbstractControl("Developer UI Rows",
                                       "Select the number of rows of real-time parameters you would like to display on the sunnypilot screen while driving.",
                                       "../assets/offroad/icon_blank.png") {

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
    auto str = QString::fromStdString(params.get("DevUIRow"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("DevUIRow", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("DevUIRow"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 1 ) {
      value = 1;
    }
    QString values = QString::number(value);
    params.put("DevUIRow", values.toStdString());
    refresh();
  });
  refresh();
}

void DevUiRow::refresh() {
  QString option = QString::fromStdString(params.get("DevUIRow"));
  if (option == "0") {
    label.setText(QString::fromStdString("1-Row"));
  } else {
    label.setText(QString::fromStdString("2-Row"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Camera Offset Value
CameraOffset::CameraOffset() : AbstractControl("Camera Offset (cm)",
                                               "Hack to trick vehicle to be left or right biased in its lane. Decreasing the value will make the car keep more left, increasing will make it keep more right. Changes take effect immediately.",
                                               "../assets/offroad/icon_blank.png") {

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
PathOffset::PathOffset() : AbstractControl("Path Offset (cm)",
                                           "Hack to trick the model path to be left or right biased of the lane. Decreasing the value will shift the model more left, increasing will shift the model more right. Changes take effect immediately.",
                                           "../assets/offroad/icon_blank.png") {

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

TorqueFriction::TorqueFriction() : AbstractControl("Friction", "Adjust Friction for the Torque Lateral Controller", "../assets/offroad/icon_blank.png") {

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
    if (value <= 1 ) {
      value = 1;
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

TorqueMaxLatAccel::TorqueMaxLatAccel() : AbstractControl("Max Lateral Acceleration", "Adjust Max Lateral Acceleration for the Torque Lateral Controller", "../assets/offroad/icon_blank.png") {

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
    if (value >= 50 ) {
      value = 50;
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
  float valuef = valuei * 0.1;
  QString valuefs = QString::number(valuef);
  label.setText(QString::fromStdString(valuefs.toStdString()));
  btnminus.setText("-");
  btnplus.setText("+");
}

TorqueDeadzoneDeg::TorqueDeadzoneDeg() : AbstractControl("Steering Angle Deadzone Degree", "Adjust Steering Angle Deadzone Degree for the Torque Lateral Controller", "../assets/offroad/icon_blank.png") {

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
    auto str = QString::fromStdString(params.get("TorqueDeadzoneDeg"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("TorqueDeadzoneDeg", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("TorqueDeadzoneDeg"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 50 ) {
      value = 50;
    }
    QString values = QString::number(value);
    params.put("TorqueDeadzoneDeg", values.toStdString());
    refresh();
  });
  refresh();
}

void TorqueDeadzoneDeg::refresh() {
  auto strs = QString::fromStdString(params.get("TorqueDeadzoneDeg"));
  int valuei = strs.toInt();
  float valuef = valuei * 0.1;
  QString valuefs = QString::number(valuef);
  label.setText(QString::fromStdString(valuefs.toStdString()));
  btnminus.setText("-");
  btnplus.setText("+");
}

// Speed Limit Control Custom Offset
SpeedLimitValueOffset::SpeedLimitValueOffset() : AbstractControl("Speed Limit Offset (MPH / KM/H)*", "Set speed limit higher or lower than actual speed limit for a more personalized drive.\n*To use this feature, turn off \"Enable Speed Limit % Offset\".", "../assets/offroad/icon_speed_limit.png") {

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
    //QUIState::ui_state.speed_lim_off = value;
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
    //QUIState::ui_state.speed_lim_off = value;
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

SpeedLimitStyle::SpeedLimitStyle() : AbstractControl("Speed Limit Style",
                                                     "MUTCD: US/Canada\nVienna: Europe/Asia/etc.",
                                                     "../assets/offroad/icon_blank.png") {

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
    label.setText(QString::fromStdString("MUTCD"));
  } else {
    label.setText(QString::fromStdString("Vienna"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

GapAdjustCruiseMode::GapAdjustCruiseMode() : AbstractControl("Mode",
                                                             "SW: Steering Wheel Button\nUI: User Interface Button on screen\nSW + UI: Steering Wheel Button + User Interface Button on screen",
                                                             "../assets/offroad/icon_blank.png") {

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
    label.setText(QString::fromStdString("S.W."));
  } else if (option == "1") {
    label.setText(QString::fromStdString("UI"));
  } else if (option == "2") {
    label.setText(QString::fromStdString("S.W. + UI"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

// Volkswagen - MQB ACC Type
VwAccType::VwAccType() : AbstractControl("Short Press +1/-1 Type",
                                         "Define the type of ACC control your car has with short press to +1 or -1.",
                                         "../assets/offroad/icon_acc_change.png") {

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
    label.setText(QString::fromStdString("+/-"));
  } else if (option == "1") {
    label.setText(QString::fromStdString("RES/SET"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}

AccChangeType::AccChangeType() : AbstractControl("Higher ACC Value",
                                                 "Define the value of higher ACC value change.",
                                                 "../assets/offroad/icon_blank.png") {

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
    auto str = QString::fromStdString(params.get("AccChangeType"));
    int value = str.toInt();
    value = value - 1;
    if (value <= 0 ) {
      value = 0;
    }
    QString values = QString::number(value);
    params.put("AccChangeType", values.toStdString());
    refresh();
  });

  QObject::connect(&btnplus, &QPushButton::clicked, [=]() {
    auto str = QString::fromStdString(params.get("AccChangeType"));
    int value = str.toInt();
    value = value + 1;
    if (value >= 1 ) {
      value = 1;
    }
    QString values = QString::number(value);
    params.put("AccChangeType", values.toStdString());
    refresh();
  });
  refresh();
}

void AccChangeType::refresh() {
  QString option = QString::fromStdString(params.get("AccChangeType"));
  if (option == "0") {
    label.setText(QString::fromStdString("5"));
  } else if (option == "1") {
    label.setText(QString::fromStdString("10"));
  }
  btnminus.setText("-");
  btnplus.setText("+");
}
