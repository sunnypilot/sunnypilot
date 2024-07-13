#pragma once

#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

class MadsSettings : public QWidget {
  Q_OBJECT

public:
  explicit MadsSettings(QWidget* parent = nullptr);
  void showEvent(QShowEvent *event) override;

signals:
  void backPress();

public slots:
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControl*> toggles;

  ButtonParamControl *dlob_settings;
};
