/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

inline bool madsLimitedSettings(const cereal::CarParams::Reader &CP, const cereal::CarParamsSP::Reader &CP_SP) {
  if (CP.getBrand() == "rivian") {
    return true;
  }
  if (CP.getBrand() == "tesla") {
    return !(CP_SP.getFlags() & 1);  // 1 == TeslaFlagsSP.HAS_VEHICLE_BUS
  }

  return false;
}

enum class MadsSteeringMode {
  REMAIN_ACTIVE = 0,
  PAUSE = 1,
  DISENGAGE = 2,
};

struct MadsSteeringModeOption {
  MadsSteeringMode mode;
  QString display_text;
  QString description;
};

class MadsSettings : public QWidget {
  Q_OBJECT

public:
  explicit MadsSettings(QWidget *parent = nullptr);

  void showEvent(QShowEvent *event) override;

signals:
  void backPress();

public slots:
  void updateToggles(bool _offroad);

private:
  Params params;
  bool offroad;

  ParamControl *madsMainCruiseToggle;
  ParamControl *madsUnifiedEngagementModeToggle;
  ButtonParamControl *madsSteeringMode;

  std::vector<int> madsSteeringModeValues = {};

  const QString MADS_MAIN_CRUISE_BASE_DESC = tr("Note: For vehicles without LFA/LKAS button, disabling this will prevent lateral control engagement.");
  const QString MADS_UNIFIED_ENGAGEMENT_MODE_BASE_DESC = QString("%1<br>"
                                                                 "<h4>%2</h4>")
                                                         .arg(tr("Engage lateral and longitudinal control with cruise control engagement."))
                                                         .arg(tr("Note: Once lateral control is engaged via UEM, it will remain engaged until it is manually disabled via the MADS button or car shut off."));

  const QString STATUS_CHECK_COMPATIBILITY = tr("Start the vehicle to check vehicle compatibility.");
  const QString DEFAULT_TO_OFF = tr("This feature defaults to OFF, and does not allow selection due to vehicle limitations.");
  const QString DEFAULT_TO_ON = tr("This feature defaults to ON, and does not allow selection due to vehicle limitations.");
  const QString STATUS_DISENGAGE_ONLY = tr("This platform only supports Disengage mode due to vehicle limitations.");

  static const std::vector<MadsSteeringModeOption> &madsSteeringModeOptions() {
    static const std::vector<MadsSteeringModeOption> options = {
      {MadsSteeringMode::REMAIN_ACTIVE,  tr("Remain Active"), tr("Remain Active: ALC will remain active when the brake pedal is pressed.")},
      {MadsSteeringMode::PAUSE,          tr("Pause"),         tr("Pause: ALC will pause when the brake pedal is pressed.")},
      {MadsSteeringMode::DISENGAGE,      tr("Disengage"),     tr("Disengage: ALC will disengage when the brake pedal is pressed.")},
    };
    return options;
  }

  static std::vector<MadsSteeringMode> getMadsSteeringModeValues() {
    std::vector<MadsSteeringMode> values;
    for (const auto& option : madsSteeringModeOptions()) {
      values.push_back(option.mode);
    }
    return values;
  }

  static std::vector<int> convertMadsSteeringModeValues(const std::vector<MadsSteeringMode> &modes) {
    std::vector<int> values;
    for (const auto& mode : modes) {
      values.push_back(static_cast<int>(mode));
    }
    return values;
  }

  static std::vector<QString> madsSteeringModeTexts() {
    std::vector<QString> texts;
    for (const auto& option : madsSteeringModeOptions()) {
      texts.push_back(option.display_text);
    }
    return texts;
  }

  static QString madsSteeringModeDescription(const MadsSteeringMode mode = MadsSteeringMode::REMAIN_ACTIVE) {
    QString base_desc = tr("Choose how Automatic Lane Centering (ALC) behaves after the brake pedal is manually pressed in sunnypilot.");
    QString result = base_desc + "<br><br>";

    for (const auto& option : madsSteeringModeOptions()) {
      QString desc = option.description;
      if (option.mode == mode) {
        desc = "<font color='white'><b>" + desc + "</b></font>";
      }
      result += desc + "<br>";
    }

    return result;
  }

  static QString madsDescriptionBuilder(const QString &custom_description, const QString &base_description) {
    return "<font color='white'><b>" + custom_description + "</b></font><br><br>" + base_description;
  }
};
