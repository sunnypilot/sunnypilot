#pragma once

#include <QApplication>

#include "common/watchdog.h"
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class VehiclePanel : public QWidget {
  Q_OBJECT

public:
  explicit VehiclePanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

public slots:
  void updateToggles();

private:
  Params params;

  QStackedLayout* main_layout = nullptr;
  QWidget* home = nullptr;

  QPushButton* setCarBtn;
  QString set;

  QWidget* home_widget;
  QString prompt_select = tr("Select your car");
};

class SPVehiclesTogglesPanel : public ListWidgetSP {
  Q_OBJECT
public:
  explicit SPVehiclesTogglesPanel(VehiclePanel *parent);
  void showEvent(QShowEvent *event) override;

public slots:
  void updateToggles();

private:
  Params params;
  bool is_onroad = false;

  ParamControlSP *stockLongToyota;
  ParamControlSP *toyotaEnhancedBsm;

  const QString toyotaEnhancedBsmDescription = QString("%1<br><br>"
                                                       "%2")
                                               .arg(tr("sunnypilot will use debugging CAN messages to receive unfiltered BSM signals, allowing detection of more objects."))
                                               .arg(tr("Tested on RAV4 TSS1, Lexus LSS1, Toyota TSS1/1.5, and Prius TSS2."));

  QString toyotaEnhancedBsmDesciptionBuilder(const QString &custom_description) {
    QString description = "<b>" + custom_description + "</b><br><br>" + toyotaEnhancedBsmDescription;
    return description;
  }
};
