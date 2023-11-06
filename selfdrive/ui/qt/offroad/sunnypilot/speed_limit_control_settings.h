#pragma once

#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/util.h"

class SpeedLimitValueOffset : public SPOptionControl {
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
  static const std::vector<QString> speed_limit_control_policy_texts;
  static const std::vector<QString> speed_limit_control_policy_descriptions;

signals:
  void backPress();

public slots:
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControl*> toggles;

  SpeedLimitValueOffset *slvo;
  ButtonParamControl *speed_limit_control_policy;
  ButtonParamControl *speed_limit_offset_settings;
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

// Add this line outside the class definition
inline const std::vector<QString> SlcSettings::speed_limit_control_policy_texts{
  tr("Nav\nOnly"),
  tr("Map\nOnly"),
  tr("Car\nOnly"),
  tr("Nav\nFirst"),
  tr("Map\nFirst"),
  tr("Car\nFirst"),
};

inline const std::vector<QString> SlcSettings::speed_limit_control_policy_descriptions{
  tr("Select the precedence order of sources used to adapt cruise speed to road limits:"),
  tr("Nav Only: Data from Mapbox active navigation only."),
  tr("Map Only: Data from OpenStreetMap only."),
  tr("Car Only: Data from the car's built-in sources (if available)."),
  tr("Nav First: Nav -> Map -> Car"),
  tr("Map First: Map -> Nav -> Car"),
  tr("Car First: Car -> Nav -> Map"),
};
