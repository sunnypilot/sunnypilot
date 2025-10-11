/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#pragma once
#include <QFile>
#include <QFileInfo>

#include "selfdrive/ui/qt/offroad/developer_panel.h"

class DeveloperPanelSP : public DeveloperPanel {
  Q_OBJECT
public:
  explicit DeveloperPanelSP(SettingsWindow *parent);

private:
  ParamControlSP *enableCopyparty;
  ParamControlSP *enableGithubRunner;
  ButtonControlSP *errorLogBtn;
  ParamControlSP *prebuiltToggle;
  Params params;
  ParamControlSP *showAdvancedControls;

private slots:
  void updateToggles(bool offroad);

protected:
  void showEvent(QShowEvent *event) override;
};
