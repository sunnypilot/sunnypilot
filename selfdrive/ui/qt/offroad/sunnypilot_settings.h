#pragma once

#include <QApplication>
#include <QStackedLayout>
#include <QPushButton>
#include <QStackedWidget>
#include <QWidget>

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

class SpeedLimitOffsetType : public AbstractControl {
  Q_OBJECT

public:
  SpeedLimitOffsetType();

signals:
  void offsetTypeUpdated();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class SpeedLimitValueOffset : public AbstractControl {
  Q_OBJECT

public:
  SpeedLimitValueOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class MaxTimeOffroad : public AbstractControl {
  Q_OBJECT

public:
  MaxTimeOffroad();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class OnroadScreenOff : public AbstractControl {
  Q_OBJECT

public:
  OnroadScreenOff();

signals:
  void toggleUpdated();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class OnroadScreenOffBrightness : public AbstractControl {
  Q_OBJECT

public:
  OnroadScreenOffBrightness();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class BrightnessControl : public AbstractControl {
  Q_OBJECT

public:
  BrightnessControl();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class CameraOffset : public AbstractControl {
  Q_OBJECT

public:
  CameraOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class PathOffset : public AbstractControl {
  Q_OBJECT

public:
  PathOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class AutoLaneChangeTimer : public AbstractControl {
  Q_OBJECT

public:
  AutoLaneChangeTimer();

signals:
  void toggleUpdated();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class GapAdjustCruiseMode : public AbstractControl {
  Q_OBJECT

public:
  GapAdjustCruiseMode();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class TorqueFriction : public AbstractControl {
  Q_OBJECT

public:
  TorqueFriction();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class TorqueMaxLatAccel : public AbstractControl {
  Q_OBJECT

public:
  TorqueMaxLatAccel();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class DevUiInfo : public AbstractControl {
  Q_OBJECT

public:
  DevUiInfo();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class ChevronInfo : public AbstractControl {
  Q_OBJECT

public:
  ChevronInfo();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;

  void refresh();
};

class SidebarTemp : public QWidget {
  Q_OBJECT

public:
  explicit SidebarTemp(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

public slots:
  void updateToggles();

private:
  inline void addItem(QWidget *w) { inner_layout.addWidget(w); }
  inline void addItem(QLayout *layout) { inner_layout.addLayout(layout); }
  inline void setSpacing(int spacing) { inner_layout.setSpacing(spacing); }
  QVBoxLayout outer_layout;
  QVBoxLayout inner_layout;
  Params params;

  ParamControl *sidebarTemperature;
  ButtonParamControl *sidebar_temp_setting;
};

class DynamicLaneProfile : public QWidget {
  Q_OBJECT

public:
  explicit DynamicLaneProfile(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

signals:
  void updateExternalToggles();

public slots:
  void updateToggles();

private:
  inline void addItem(QWidget *w) { inner_layout.addWidget(w); }
  inline void addItem(QLayout *layout) { inner_layout.addLayout(layout); }
  inline void setSpacing(int spacing) { inner_layout.setSpacing(spacing); }
  QVBoxLayout outer_layout;
  QVBoxLayout inner_layout;
  Params params;

  ParamControl *dynamicLaneProfile;
  ButtonParamControl *dlp_settings;
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

signals:
  void updateStockToggles();

public slots:
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControl*> toggles;

  CameraOffset *camera_offset;
  PathOffset *path_offset;
  AutoLaneChangeTimer *auto_lane_change_timer;
  SpeedLimitOffsetType *slo_type;
  SpeedLimitValueOffset *slvo;
  GapAdjustCruiseMode *gac_mode;
  TorqueFriction *friction;
  TorqueMaxLatAccel *lat_accel_factor;
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

  void updateToggles();
};
