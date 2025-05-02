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
}

void OffroadHomeSP::showEvent(QShowEvent *event) {
  refreshOffroadStatus();
  OffroadHome::showEvent(event);
}

void OffroadHomeSP::refreshOffroadStatus() {
  btn_exit_offroad->setVisible(params.getBool("OffroadMode"));
  OffroadHome::refresh();
}
