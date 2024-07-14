#pragma once

#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"

class OnroadScreenOff : public OptionControlSP {
  Q_OBJECT

public:
  OnroadScreenOff();

  void refresh();

private:
  Params params;
};

class OnroadScreenOffBrightness : public OptionControlSP {
  Q_OBJECT

public:
  OnroadScreenOffBrightness();

  void refresh();

private:
  Params params;
};

class MaxTimeOffroad : public OptionControlSP {
  Q_OBJECT

public:
  MaxTimeOffroad();

  void refresh();

private:
  Params params;
};

class BrightnessControl : public OptionControlSP {
  Q_OBJECT

public:
  BrightnessControl();

  void refresh();

private:
  Params params;
};

class DisplayPanel : public ListWidget {
  Q_OBJECT

public:
  explicit DisplayPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;

public slots:
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControlSP*> toggles;

  OnroadScreenOff *onroad_screen_off;
  OnroadScreenOffBrightness *onroad_screen_off_brightness;
};
