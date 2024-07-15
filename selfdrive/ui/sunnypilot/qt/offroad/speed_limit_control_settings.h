#pragma once

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/sp_priv_ui.h"
#else
#include "selfdrive/ui/ui.h"
#endif
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_scrollview.h"
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
