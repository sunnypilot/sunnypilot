#pragma once

#include <QApplication>
#include <QStackedLayout>
#include <QPushButton>
#include <QStackedWidget>
#include <QWidget>

#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/controls.h"

class SPOptionControl : public AbstractControl {
  Q_OBJECT

private:
  struct MinMaxValue {
    int min_value;
    int max_value;
  };

public:
  SPOptionControl(const QString &param, const QString &title, const QString &desc, const QString &icon,
                  const MinMaxValue &range, const int per_value_change = 1) : AbstractControl(title, desc, icon) {
    const QString style = R"(
      QPushButton {
        padding: 0;
        border-radius: 50px;
        font-size: 35px;
        font-weight: 500;
        color: #E4E4E4;
        background-color: #393939;
      }
      QPushButton:pressed {
        background-color: #4a4a4a;
      }
      QPushButton:disabled {
        color: #33E4E4E4;
      }
    )";

    label.setAlignment(Qt::AlignVCenter|Qt::AlignRight);
    label.setStyleSheet("color: #e0e879");
    hlayout->addWidget(&label);

    const std::vector<QString> button_texts{"-", "+"};

    key = param.toStdString();
    value = atoi(params.get(key).c_str());

    button_group = new QButtonGroup(this);
    button_group->setExclusive(true);
    for (int i = 0; i < button_texts.size(); i++) {
      QPushButton *button = new QPushButton(button_texts[i], this);
      button->setStyleSheet(style);
      button->setFixedSize(150, 100);
      hlayout->addWidget(button);
      button_group->addButton(button, i);

      int change_value = (i == 0) ? -per_value_change : per_value_change;

      QObject::connect(button, &QPushButton::clicked, [=]() {
        key = param.toStdString();
        value = atoi(params.get(key).c_str());
        value += change_value;
        value = std::clamp(value, range.min_value, range.max_value);
        params.put(key, QString::number(value).toStdString());
        updateLabels();

        if (update) {
          emit updateOtherToggles();
        }
      });
    }
  }

  void setUpdateOtherToggles(bool _update) {
    update = _update;
  }

  inline void setLabel(const QString &text) { label.setText(text); }

  void setEnabled(bool enabled) {
    for (auto btn : button_group->buttons()) {
      btn->setEnabled(enabled);
    }
  }

signals:
  void updateLabels();
  void updateOtherToggles();

private:
  std::string key;
  int value;
  QButtonGroup *button_group;
  QLabel label;
  Params params;
  std::map<QString, QString> option_label = {};
  bool update = false;
};

class SpeedLimitOffsetType : public SPOptionControl {
  Q_OBJECT

public:
  SpeedLimitOffsetType();

  void refresh();

private:
  Params params;
};

class SpeedLimitValueOffset : public SPOptionControl {
  Q_OBJECT

public:
  SpeedLimitValueOffset();

  void refresh();

private:
  Params params;
};

class MaxTimeOffroad : public SPOptionControl {
  Q_OBJECT

public:
  MaxTimeOffroad();

  void refresh();

private:
  Params params;
};

class OnroadScreenOff : public SPOptionControl {
  Q_OBJECT

public:
  OnroadScreenOff();

  void refresh();

private:
  Params params;
};

class OnroadScreenOffBrightness : public SPOptionControl {
  Q_OBJECT

public:
  OnroadScreenOffBrightness();

  void refresh();

private:
  Params params;
};

class BrightnessControl : public SPOptionControl {
  Q_OBJECT

public:
  BrightnessControl();

  void refresh();

private:
  Params params;
};

class CameraOffset : public SPOptionControl {
  Q_OBJECT

public:
  CameraOffset();

  void refresh();

private:
  Params params;
};

class PathOffset : public SPOptionControl {
  Q_OBJECT

public:
  PathOffset();

  void refresh();

private:
  Params params;
};

class AutoLaneChangeTimer : public SPOptionControl {
  Q_OBJECT

public:
  AutoLaneChangeTimer();

  void refresh();

signals:
  void toggleUpdated();

private:
  Params params;
};

class TorqueFriction : public SPOptionControl {
  Q_OBJECT

public:
  TorqueFriction();

  void refresh();

private:
  Params params;
};

class TorqueMaxLatAccel : public SPOptionControl {
  Q_OBJECT

public:
  TorqueMaxLatAccel();

  void refresh();

private:
  Params params;
};

class DevUiInfo : public SPOptionControl {
  Q_OBJECT

public:
  DevUiInfo();

  void refresh();

private:
  Params params;
};

class ChevronInfo : public SPOptionControl {
  Q_OBJECT

public:
  ChevronInfo();

  void refresh();

private:
  Params params;
};

class SPGeneralPanel : public ListWidget {
  Q_OBJECT

public:
  explicit SPGeneralPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

public slots:
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControl*> toggles;

  OnroadScreenOff *onroad_screen_off;
  OnroadScreenOffBrightness *onroad_screen_off_brightness;
};

class SPControlsPanel : public ListWidget {
  Q_OBJECT

public:
  explicit SPControlsPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

public slots:
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControl*> toggles;
  ParamWatcher *param_watcher;

  CameraOffset *camera_offset;
  PathOffset *path_offset;
  AutoLaneChangeTimer *auto_lane_change_timer;
  SpeedLimitOffsetType *slo_type;
  SpeedLimitValueOffset *slvo;
  TorqueFriction *friction;
  TorqueMaxLatAccel *lat_accel_factor;
  ButtonParamControl *dlp_settings;

  void updateButtons();
};

class SPVehiclesPanel : public QWidget {
  Q_OBJECT

public:
  explicit SPVehiclesPanel(QWidget *parent = nullptr);

private:
  Params params;

  QStackedLayout* main_layout = nullptr;
  QWidget* home = nullptr;

  QWidget* home_widget;
};

class SPVehiclesTogglesPanel : public ListWidget {
  Q_OBJECT
public:
  explicit SPVehiclesTogglesPanel(SPVehiclesPanel *parent);

private:
  Params params;

  ParamControl *stockLongToyota;
};

class SPVisualsPanel : public ListWidget {
  Q_OBJECT

public:
  explicit SPVisualsPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

private:
  Params params;
  std::map<std::string, ParamControl*> toggles;

  DevUiInfo *dev_ui_info;
  ChevronInfo *chevron_info;
  ButtonParamControl *sidebar_temp_setting;

  void updateToggles();
};
