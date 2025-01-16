#pragma once

#include <QPushButton>
#include <QFile>

#include "system/hardware/hw.h"

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#define ButtonControl ButtonControlSP
#define ToggleControl ToggleControlSP
#else
#include "selfdrive/ui/qt/widgets/controls.h"
#endif

class TSKKeyboard : public ButtonControl {
  Q_OBJECT

public:
  TSKKeyboard();

private:
  Params params;

  QString getArchive(QString);
  bool isValid(QString);
  void refresh();
};
