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

  QListWidget* list = new QListWidget(this);
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
  main_layout->addWidget(new ParamControl("EnableDebugSnapshot",
                                          "Debug snapshot on screen center tap",
                                          "Stores snapshot file with current state of some modules.",
                                          "../assets/offroad/icon_calibration.png"));
}

SPControlsPanel::SPControlsPanel(QWidget* parent) : QWidget(parent) {

  QVBoxLayout* main_layout = new QVBoxLayout(this);
  QWidget* madsMainControl = new QWidget(this);
  QVBoxLayout* madsSubControl = new QVBoxLayout(this);

  ParamControl *madsControl = new ParamControl("EnableMads",
                                               "Enable M.A.D.S.",
                                               "Enable the beloved M.A.D.S. feature. Disable toggle to revert back to stock openpilot engagement/disengagement.",
                                               "../assets/offroad/icon_openpilot.png");
  madsSubControl->setContentsMargins(QMargins());
  madsSubControl->addWidget(horizontal_line());
  madsSubControl->addWidget(new ParamControl("DisengageLateralOnBrake",
                                             "Disengage Lateral On Brake Pedal",
                                             "When enabled, pressing the brake pedal will disengage lateral control on sunnypilot.",
                                             "../assets/offroad/icon_openpilot.png"));
  madsSubControl->addWidget(horizontal_line());
  madsSubControl->addWidget(new ParamControl("AccMadsCombo",
                                             "Enable ACC+MADS with RES+/SET-",
                                             "Engage both M.A.D.S. and ACC with a single press of RES+ or SET- button.\nNote: Once M.A.D.S. is engaged via this mode, it will remain engaged until it is manually disabled via the M.A.D.S. button or car shut off.",
                                             "../assets/offroad/icon_openpilot.png"));
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
  main_layout->addWidget(new AutoLaneChangeTimer());
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
  main_layout->addWidget(new ParamControl("SpeedLimitControl",
                                          "Enable Speed Limit Control (SLC)",
                                          "Use speed limit signs information from map data and car interface (if applicable) to automatically adapt cruise speed to road limits.",
                                          "../assets/offroad/icon_speed_limit.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("SpeedLimitPercOffset",
                                          "Enable Speed Limit % Offset",
                                          "Set speed limit slightly higher than actual speed limit for a more natural drive.",
                                          "../assets/offroad/icon_speed_limit.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("MapTurnSpeedControl",
                                          "Enable Map Data Turn Speed Control (MTSC)",
                                          "Use curvature information from map data to define speed limits to take turns ahead.",
                                          "../assets/offroad/icon_openpilot.png"));
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

  ScrollView *scroller = new ScrollView(home_widget, this);
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
}

SPVisualsPanel::SPVisualsPanel(QWidget* parent) : QWidget(parent) {

  QVBoxLayout* main_layout = new QVBoxLayout(this);

  main_layout->addWidget(new OnroadScreenOff());
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new OnroadScreenOffBrightness());
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new BrightnessControl());
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("ShowDebugUI",
                                          "Show debug UI elements",
                                          "Show UI elements that aid debugging.",
                                          "../assets/offroad/icon_calibration.png"));
  main_layout->addWidget(horizontal_line());
  main_layout->addWidget(new ParamControl("BrakeLights",
                                          "Display Braking Status",
                                          "Enable this will turn the current speed value to red while the brake is used.",
                                          "../assets/offroad/icon_road.png"));
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