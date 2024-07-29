/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#pragma once

#include <string>
#include <vector>

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/util.h"

class SpeedLimitPolicySettings : public QWidget {
  Q_OBJECT

public:
  explicit SpeedLimitPolicySettings(QWidget* parent = nullptr);
  void showEvent(QShowEvent *event) override;
  static const std::vector<QString> speed_limit_policy_texts;
  static const std::vector<QString> speed_limit_policy_descriptions;

signals:
  void backPress();

public slots:
  void updateToggles();

private:
  Params params;

  ButtonParamControlSP *speed_limit_policy;
  ParamWatcher *param_watcher;

  QString speedLimitPolicyDescriptionBuilder(QString param, std::vector<QString> descriptions) {
    std::string key = param.toStdString();
    int value = atoi(params.get(key).c_str());
    value += 1;  // always bump one due to first line being generic description
    QString description = "";

    for (int i = 0; i < descriptions.size(); i++) {
      if (i == 1) {
        description += "<br><br>";
      }

      if (i == value) {
        description += "<b>" + descriptions[i] + "</b>";
      } else {
        description += descriptions[i];
      }

      if ((i > 0) && (i < descriptions.size() - 1)) {
        description += "<br>";
      }
    }

    return description;
  }
};

// Add this line outside the class definition
inline const std::vector<QString> SpeedLimitPolicySettings::speed_limit_policy_texts{
  tr("Nav") + "\n" + tr("Only"),
  tr("Map") + "\n" + tr("Only"),
  tr("Car") + "\n" + tr("Only"),
  tr("Nav") + "\n" + tr("First"),
  tr("Map") + "\n" + tr("First"),
  tr("Car") + "\n" + tr("First"),
};

inline const std::vector<QString> SpeedLimitPolicySettings::speed_limit_policy_descriptions{
  tr("Select the precedence order of sources. Utilized by Speed Limit Control and Speed Limit Warning"),
  tr("Nav Only: Data from Mapbox active navigation only."),
  tr("Map Only: Data from OpenStreetMap only."),
  tr("Car Only: Data from the car's built-in sources (if available)."),
  tr("Nav First: Nav -> Map -> Car"),
  tr("Map First: Map -> Nav -> Car"),
  tr("Car First: Car -> Nav -> Map"),
};
