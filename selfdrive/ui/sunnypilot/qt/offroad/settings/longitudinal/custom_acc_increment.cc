/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/custom_acc_increment.h"

CustomAccIncrement::CustomAccIncrement(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent)
    : ExpandableToggleRow(param, title, desc, icon, parent) {
  auto *accFrame = new QFrame(this);
  auto *accFrameLayout = new QGridLayout();
  accFrame->setLayout(accFrameLayout);
  accFrameLayout->setSpacing(0);

  auto *shortPressControl = new AccIncrementOptionControl("CustomAccShortPressIncrement", {1, 10}, 1);
  connect(shortPressControl, &OptionControlSP::updateLabels, shortPressControl, &AccIncrementOptionControl::refresh);

  auto *longPressControl = new AccIncrementOptionControl("CustomAccLongPressIncrement", {1, 3}, 1, &customLongValues);
  connect(longPressControl, &OptionControlSP::updateLabels, longPressControl, &AccIncrementOptionControl::refresh);

  shortPressControl->setFixedWidth(280);
  longPressControl->setFixedWidth(280);
  accFrameLayout->addWidget(shortPressControl, 0, 0, Qt::AlignLeft);
  accFrameLayout->addWidget(longPressControl, 0, 1, Qt::AlignRight);

  addItem(accFrame);
}

AccIncrementOptionControl::AccIncrementOptionControl(const QString &param, const MinMaxValue &range, const int per_value_change, const QMap<QString, QString> *valMap)
    : OptionControlSP(param, "", "", "", range, per_value_change, true, valMap) {
  param_name = param.toStdString();
  refresh();
}

void AccIncrementOptionControl::refresh() {
  std::string val = params.get(param_name);
  std::string label = "<span style='font-size: 45px; font-weight: 450; color: #FFFFFF;'>";
  label += param_name == "CustomAccShortPressIncrement" ? "Short Press" : "Long Press";
  label += " <br><span style='font-size: 40px; font-weight: 450; color:rgb(174, 255, 195);'>" + val;
  label += param_name == "CustomAccShortPressIncrement"
             ? (val == "1" ? " (Default)" : "")
             : (val == "5" ? " (Default)" : "");
  label += "</span></span>";
  setLabel(QString::fromStdString(label));
}
