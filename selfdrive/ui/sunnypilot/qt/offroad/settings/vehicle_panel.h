/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/platform_selector.h"

class VehiclePanel : public QFrame {
  Q_OBJECT

public:
  explicit VehiclePanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;
  // Toggle states
  enum class ToggleState {
    ENABLED,
    DISABLED_LONGITUDINAL,
    DISABLED_DRIVING
  };
public slots:
  void updatePanel(bool _offroad);

private:
  // UI elements
  QStackedLayout* main_layout = nullptr;
  QWidget* vehicleScreen = nullptr;
  PlatformSelector *platformSelector = nullptr;
  ParamControlSP* hkgtuningToggle = nullptr;
  ButtonControl* hkgBrakingButton = nullptr;
  bool offroad;

  // State tracking
  Params params;

  // Helper methods
  ToggleState getToggleState(bool hasOpenpilotLong) const;
  void updateToggleState(ParamControlSP* toggle, bool hasOpenpilotLong);

private slots:
  void updateCarToggles();
  void updateToggles(bool offroad_transition);
  void handleToggleAction(ParamControlSP* toggle, bool checked);
};
