#include "selfdrive/ui/qt/widgets/sunnypilot.h"

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

#include "selfdrive/common/params.h"
#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/qt/widgets/input.h"

#include "selfdrive/ui/ui.h"

static QStringList get_list(const char* path)
{
  QStringList stringList;
  QFile textFile(path);
  if(textFile.open(QIODevice::ReadOnly))
  {
      QTextStream textStream(&textFile);
      while (true)
      {
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
  for(QString item : items) {
    if(set == item) {
        list->setCurrentRow(index + 1);
        break;
    }
    index++;
  }

  QObject::connect(list, QOverload<QListWidgetItem*>::of(&QListWidget::itemClicked),
    [=](QListWidgetItem* item){

    if(list->currentRow() == 0)
        Params().remove("CarModel");
    else
        Params().put("CarModel", list->currentItem()->text().toStdString());

    emit selectedCar();
    });

  main_layout->addWidget(list);
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
    QUIState::ui_state.scene.brightness = value;
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
    QUIState::ui_state.scene.brightness = value;
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
    QUIState::ui_state.scene.onroadScreenOff = value;
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
    QUIState::ui_state.scene.onroadScreenOff = value;
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
    QUIState::ui_state.scene.onroadScreenOffBrightness = value;
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
    QUIState::ui_state.scene.onroadScreenOffBrightness = value;
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