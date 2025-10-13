/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/max_time_offroad.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

enum class DeviceSleepModeStatus {
  DEFAULT,
  OFFROAD,
};

class DevicePanelSP : public DevicePanel {
  Q_OBJECT

public:
  explicit DevicePanelSP(SettingsWindowSP *parent = 0);
  void showEvent(QShowEvent *event) override;
  void setOffroadMode();
  void updateState(bool _offroad);
  void resetSettings();

private:
  std::map<QString, PushButtonSP*> buttons;
  PushButtonSP *offroadBtn;
  MaxTimeOffroad *maxTimeOffroad;
  ButtonParamControlSP *toggleDeviceBootMode;
  QVBoxLayout *power_group_layout;
  bool offroad;

  std::vector<PushButtonSP*> always_enabled_btns = {};

  const QString alwaysOffroadStyle = R"(
    PushButtonSP {
      border-radius: 20px;
      font-size: 50px;
      font-weight: 450;
      height: 150px;
      padding: 0 25px 0 25px;
      color: #FFFFFF;
      background-color: #393939;
    }
    PushButtonSP:pressed {
      background-color: #4A4A4A;
    }
  )";

  const QString autoOffroadStyle = R"(
    PushButtonSP {
      border-radius: 20px;
      font-size: 50px;
      font-weight: 450;
      height: 150px;
      padding: 0 25px 0 25px;
      color: #FFFFFF;
      background-color: #E22C2C;
    }
    PushButtonSP:pressed {
      background-color: #FF2424;
    }
  )";

  const QString rebootButtonStyle = R"(
    PushButtonSP {
      border-radius: 20px;
      font-size: 50px;
      font-weight: 450;
      height: 150px;
      padding: 0 25px 0 25px;
      color: #FFFFFF;
      background-color: #393939;
    }
    PushButtonSP:pressed {
      background-color: #4A4A4A;
    }
  )";

  const QString powerOffButtonStyle = R"(
    PushButtonSP {
      border-radius: 20px;
      font-size: 50px;
      font-weight: 450;
      height: 150px;
      padding: 0 25px 0 25px;
      color: #FFFFFF;
      background-color: #E22C2C;
    }
    PushButtonSP:pressed {
      background-color: #FF2424;
    }
  )";

  static QString deviceSleepModeDescription(DeviceSleepModeStatus status = DeviceSleepModeStatus::DEFAULT) {
    QString def_str = tr("⁍ Default: Device will boot/wake-up normally & will be ready to engage.");
    QString offrd_str = tr("⁍ Offroad: Device will be in Always Offroad mode after boot/wake-up.");

    if (status == DeviceSleepModeStatus::DEFAULT) {
      def_str = "<font color='white'><b>" + def_str + "</b></font>";
    } else if (status == DeviceSleepModeStatus::OFFROAD) {
      offrd_str = "<font color='white'><b>" + offrd_str + "</b></font>";
    }

    return QString("%1<br><br>%2<br>%3")
             .arg(tr("Controls state of the device after boot/sleep."))
             .arg(def_str)
             .arg(offrd_str);
  }
};
