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

  std::vector<int> madsSteeringModeValues = getMadsSteeringModeValues();

  const QString STATUS_CHECK_COMPATIBILITY = tr("Start the car to check car compatibility");
  const QString STATUS_DISENGAGE_ONLY = tr("This platform only supports Disengage mode due to car limitations.");

  static const std::vector<MadsSteeringModeOption> &madsSteeringModeOptions() {
    static const std::vector<MadsSteeringModeOption> options = {
      {MadsSteeringMode::REMAIN_ACTIVE,  tr("Remain Active"), tr("Remain Active: ALC will remain active when the brake pedal is pressed.")},
      {MadsSteeringMode::PAUSE,          tr("Pause"),         tr("Pause: ALC will pause steering when the brake pedal is pressed.")},
      {MadsSteeringMode::DISENGAGE,      tr("Disengage"),     tr("Disengage: ALC will disengage when the brake pedal is pressed.")},
    };
    return options;
  }

  static std::vector<int> getMadsSteeringModeValues() {
    std::vector<int> values;
    for (const auto& option : madsSteeringModeOptions()) {
      values.push_back(static_cast<int>(option.mode));
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

  static QString madsSteeringModeDescriptionBuilder(const QString &custom_description, const QString &madsSteeringModeDescription) {
    return "<font color='white'><b>" + custom_description + "</b></font><br><br>" + madsSteeringModeDescription;
  }
};
