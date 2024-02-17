#pragma once

#include <QApplication>

#include "common/watchdog.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

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
};

class SPVehiclesTogglesPanel : public ListWidget {
  Q_OBJECT
public:
  explicit SPVehiclesTogglesPanel(VehiclePanel *parent);

private:
  Params params;

  ParamControl *stockLongToyota;
};
