/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/developer/custom_acc_increment.h"

CustomAccIncrement::CustomAccIncrement(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent)
    : ExpandableToggleRow(param, title, desc, icon, parent) {

  auto *accFrame = new QFrame(this);
  auto *accFrameLayout = new QGridLayout(this);
  accFrame->setLayout(accFrameLayout);
  accFrameLayout->setSpacing(0);

  auto *op1 = new AccIncrementOptionControl("CustomAccShortPressIncrement", {1, 10}, 1);
  connect(op1, &OptionControlSP::updateLabels, op1, &AccIncrementOptionControl::refresh);

  auto *op2 = new AccIncrementOptionControl("CustomAccLongPressIncrement", {5, 10}, 5);
  connect(op2, &OptionControlSP::updateLabels, op2, &AccIncrementOptionControl::refresh);

  op1->setFixedWidth(330);
  op2->setFixedWidth(330);
  accFrameLayout->addWidget(op1, 0, 0, Qt::AlignLeft);
  accFrameLayout->addWidget(op2, 0, 1, Qt::AlignRight);

  addItem(accFrame);

}

AccIncrementOptionControl::AccIncrementOptionControl(const QString &param, const MinMaxValue &range, const int per_value_change) : OptionControlSP(
  param,
  "",
  "",
  "",
  range, per_value_change, true) {

    param_name = param.toStdString();
    refresh();
}

void AccIncrementOptionControl::refresh() {
  std::string val = params.get(param_name);
  std::string label = "<span style='font-size: 45px; font-weight: 450; color: #FFFFFF;'>";
  label += param_name == "CustomAccShortPressIncrement" ? "Short Press" : "Long Press";
  label += " <br><span style='font-size: 40px; font-weight: 450; color:rgb(174, 255, 195);'>" + val;
  label += param_name == "CustomAccShortPressIncrement" ? (val == "1" ? " (Default)" : "") : (val == "5" ? " (Default)" : "");
  label += "</span></span>";
  setLabel(QString::fromStdString(label));
}
