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
  accFrameLayout->setSpacing(75);

  AccIncrementOptionControl *op1 = new AccIncrementOptionControl(QString::fromStdString("CustomAccShortPressIncrement"));
  QObject::connect(op1, &OptionControlSP::updateLabels, op1, &AccIncrementOptionControl::refresh);
  AccIncrementOptionControl *op2 = new AccIncrementOptionControl(QString::fromStdString("CustomAccLongPressIncrement"));
  QObject::connect(op2, &OptionControlSP::updateLabels, op2, &AccIncrementOptionControl::refresh);

  op1->setFixedWidth(200);
  op2->setFixedWidth(200);
  accFrameLayout->addWidget(new QLabel("Short Press Increment"), 0, 0, Qt::AlignCenter);
  accFrameLayout->addWidget(new QLabel("Long Press Increment"), 0, 1, Qt::AlignCenter);
  accFrameLayout->addWidget(op1, 1, 0, Qt::AlignCenter);
  accFrameLayout->addWidget(op2, 1, 1, Qt::AlignCenter);

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
  setLabel(QString::fromStdString(params.get(param_name)));
}
