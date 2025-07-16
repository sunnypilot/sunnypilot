/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include <QStackedWidget>

#include "selfdrive/ui/sunnypilot/qt/offroad/offroad_home.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/drive_stats.h"

OffroadHomeSP::OffroadHomeSP(QWidget *parent) : OffroadHome(parent) {
  QFrame *left_widget = new QFrame(this);
  QVBoxLayout *left_layout = new QVBoxLayout(left_widget);
  left_layout->setContentsMargins(0, 0, 0, 0);
  left_layout->setSpacing(30);

  btn_exit_offroad = new ExitOffroadButton(this);
  QObject::connect(btn_exit_offroad, &ExitOffroadButton::clicked, [=]() {
    refreshOffroadStatus();
  });
  left_layout->addWidget(btn_exit_offroad);

  left_layout->addWidget(new DriveStats(this));
  left_widget->setStyleSheet("border-radius: 10px;");

  home_layout->insertWidget(0, left_widget);

  offroad_notif = new QPushButton(tr("ALWAYS OFFROAD ACTIVE"));
  offroad_notif->setVisible(false);
  offroad_notif->setStyleSheet("background-color: #E22C2C;");
  header_layout->insertWidget(0, offroad_notif, 0, Qt::AlignHCenter | Qt::AlignLeft);

  QObject::connect(deviceSP(), &DeviceSP::displayPowerChanged, this, &OffroadHomeSP::refreshOffroadStatus);

}

void OffroadHomeSP::showEvent(QShowEvent *event) {
  refreshOffroadStatus();
  OffroadHome::showEvent(event);
}

void OffroadHomeSP::refreshOffroadStatus() {
  bool is_offroad = params.getBool("OffroadMode");
  btn_exit_offroad->setVisible(is_offroad);
  offroad_notif->setVisible(is_offroad);
  OffroadHome::refresh();
}
