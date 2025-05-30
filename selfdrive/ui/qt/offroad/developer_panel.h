#pragma once

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/expandable_row.h"
#else
#include "selfdrive/ui/qt/offroad/settings.h"
#endif

class DeveloperPanel : public ListWidget {
  Q_OBJECT
public:
  explicit DeveloperPanel(SettingsWindow *parent);
  void showEvent(QShowEvent *event) override;

private:
  Params params;
  ParamControl* adbToggle;
  ParamControl* joystickToggle;
  ButtonControl* errorLogBtn;
  ParamControl* longManeuverToggle;
  ParamControl* experimentalLongitudinalToggle;
  ParamControl* enableGithubRunner;
  bool is_release;
  bool offroad = false;

private slots:
  void updateToggles(bool _offroad);
};
