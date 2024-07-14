#pragma once

#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

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

class CustomOffsetsSettings : public QWidget {
  Q_OBJECT

public:
  explicit CustomOffsetsSettings(QWidget* parent = nullptr);

signals:
  void backPress();

private:
  Params params;
  std::map<std::string, ParamControlSP*> toggles;

  CameraOffset *camera_offset;
  PathOffset *path_offset;
};
