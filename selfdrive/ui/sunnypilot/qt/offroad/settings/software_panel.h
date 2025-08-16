/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/util.h"
#include "selfdrive/ui/qt/offroad/settings.h"

class SoftwarePanelSP final : public SoftwarePanel {
  Q_OBJECT

public:
  explicit SoftwarePanelSP(QWidget *parent = nullptr);

private:
  void searchBranches(const QString &query);
  ParamControl *disableUpdatesToggle = nullptr;
  void handleDisableUpdatesToggled(bool state);
private slots:
  void updateDisableUpdatesToggle(bool offroad);
protected:
  void showEvent(QShowEvent *event) override;
};
