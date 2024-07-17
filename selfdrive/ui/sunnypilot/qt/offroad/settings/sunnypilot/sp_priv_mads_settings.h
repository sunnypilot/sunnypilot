#pragma once

#include <map>
#include <string>

#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_scrollview.h"

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
  std::map<std::string, ParamControlSP*> toggles;

  ButtonParamControlSP *dlob_settings;
};
