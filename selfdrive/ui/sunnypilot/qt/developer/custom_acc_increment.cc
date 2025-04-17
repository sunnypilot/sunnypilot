/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/developer/custom_acc_increment.h"

CustomAccIncrement::CustomAccIncrement(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent)
    : ExpandableRow(param, title, desc, icon, parent) {

  QFrame *accFrame = new QFrame(this);
  QGridLayout *accFrameLayout = new QGridLayout(this);
  accFrame->setLayout(accFrameLayout);
  accFrameLayout->setSpacing(0);

  AccIncrementOptionControl *op1 = new AccIncrementOptionControl(QString::fromStdString("CustomAccShortPressIncrement"));
  QObject::connect(op1, &OptionControlSP::updateLabels, op1, &AccIncrementOptionControl::refresh);

  AccIncrementOptionControl *op2 = new AccIncrementOptionControl(QString::fromStdString("CustomAccLongPressIncrement"));
  QObject::connect(op2, &OptionControlSP::updateLabels, op2, &AccIncrementOptionControl::refresh);

  op1->setFixedWidth(330);
  op2->setFixedWidth(330);
  accFrameLayout->addWidget(op1, 0, 0, Qt::AlignLeft);
  accFrameLayout->addWidget(op2, 0, 1, Qt::AlignRight);

  addItem(accFrame);

}

AccIncrementOptionControl::AccIncrementOptionControl(const QString &param) : OptionControlSP(
  param,
  "",
  "",
  "",
  {1,10}, 1, true) {

    param_name = param.toStdString();
    refresh();
}

void AccIncrementOptionControl::refresh() {
  std::string val = params.get(param_name);
  std::string label = "<span style='font-size: 35px; font-weight: 450; color: #FFFFFF;'>";
  label += param_name == "CustomAccShortPressIncrement" ? "Short Press" : "Long Press";
  label += " <br><span style='font-size: 35px; font-weight: 450; color: #FFFFFF;'>" + val;
  label += param_name == "CustomAccShortPressIncrement" ? (val == "1" ? " (Default)" : "") : (val == "5" ? " (Default)" : "");
  label += "</span></span>";
  setLabel(QString::fromStdString(label));
}
