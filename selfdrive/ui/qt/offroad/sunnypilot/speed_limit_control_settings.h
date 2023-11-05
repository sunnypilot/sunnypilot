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

  QString slcPolicyDescriptionBuilder(QString param) {
    std::string key = param.toStdString();
    int value = atoi(params.get(key).c_str());
    QString description = tr("Select the precedence order of sources used to adapt cruise speed to road limits:");
    description += "<br><br>";

    for (int i = 0; i < speed_limit_control_policy_descriptions.size(); i++) {
      if (i == value) {
        description += "<b>" + speed_limit_control_policy_descriptions[i] + "</b>";
      } else {
        description += speed_limit_control_policy_descriptions[i];
      }

      if (i < speed_limit_control_policy_descriptions.size() - 1) {
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
  tr("Nav Only: Data from Mapbox active navigation only."),
  tr("Map Only: Data from OpenStreetMap only."),
  tr("Car Only: Data from the car's built-in sources (if available)."),
  tr("Nav First: Nav -> Map -> Car"),
  tr("Map First: Map -> Nav -> Car"),
  tr("Car First: Car -> Nav -> Map"),
};
