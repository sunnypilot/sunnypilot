/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/widgets/expandable_row.h"

ExpandableRow::ExpandableRow(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent)
    : ToggleControlSP(title, desc, icon, false, parent) {

  key = param.toStdString();
  QObject::connect(this, &ExpandableRow::toggleFlipped, this, &ExpandableRow::toggleClicked);

  collapsibleWidget = new QFrame(this);
  collapsibleWidget->setContentsMargins(0, 0, 0, 0);
  collapsibleWidget->setVisible(false);
  QVBoxLayout *collapsible_layout = new QVBoxLayout(this);
  collapsibleWidget->setLayout(collapsible_layout);

  list = new ListWidgetSP(this, false);

  main_layout->addWidget(collapsibleWidget);
  collapsible_layout->addWidget(list);

}

void ExpandableRow::toggleClicked(bool state) {
  params.putBool(key, state);
  collapsibleWidget->setVisible(state);
}
