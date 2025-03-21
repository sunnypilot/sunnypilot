/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <map>

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"

class NeuralNetworkLateralControl : public ParamControl {
  Q_OBJECT

public:
  NeuralNetworkLateralControl();
  void showEvent(QShowEvent *event) override;

public slots:
  void updateToggle();

private:
  Params params;

  void refresh();

  QString nnffDescriptionBuilder(const QString &custom_description) {
    QString description = "<b>" +
                          custom_description +
                          "</b><br><br>" +
                          nnff_description;
    return description;
  }

  const QString nnff_description = QString("%1<br><br>"
                                           "%2")
                                   .arg(tr("Formerly known as <b>\"NNFF\"</b>, this replaces the lateral <b>\"torque\"</b> controller, "
                                           "with one using a neural network trained on each car's (actually, each separate EPS firmware) driving data for increased controls accuracy."))
                                   .arg(tr("Reach out to the sunnypilot team in the following channel at the sunnypilot Discord server with feedback, "
                                           "or to provide log data for your car if your car is currently unsupported: ") +
                                           "<font color='white'><b>#tuning-nnlc</b></font>");
};
