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

#include <map>
#include <string>
#include <vector>

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/util.h"

class SpeedLimitValueOffset : public OptionControlSP {
  Q_OBJECT

public:
  SpeedLimitValueOffset();

  void refresh();

private:
  Params params;
};

class SlcSettings : public QWidget {
  Q_OBJECT

public:
  explicit SlcSettings(QWidget* parent = nullptr);
  void showEvent(QShowEvent *event) override;
  static const std::vector<QString> speed_limit_engage_descriptions;

signals:
  void backPress();

public slots:
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControlSP*> toggles;

  SpeedLimitValueOffset *slvo;
  ButtonParamControlSP *speed_limit_offset_settings;
  ButtonParamControlSP *speed_limit_engage_settings;
  ParamWatcher *param_watcher;

  QString slcDescriptionBuilder(QString param, std::vector<QString> descriptions) {
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

inline const std::vector<QString> SlcSettings::speed_limit_engage_descriptions{
  tr("Select the desired mode to set the cruising speed to the speed limit:"),
  tr("Auto: Automatic speed adjustment on motorways based on speed limit data."),
  tr("User Confirm: Inform the driver to change set speed of Adaptive Cruise Control to help the driver stay within the speed limit."),
};
