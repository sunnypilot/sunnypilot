#pragma once

#include <QPushButton>

#include "system/hardware/hw.h"

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#define ButtonControl ButtonControlSP
#else
#include "selfdrive/ui/qt/widgets/controls.h"
#endif

class ExternalStorageControl : public ButtonControl {
  Q_OBJECT

public:
  ExternalStorageControl();

protected:
  void showEvent(QShowEvent *event) override;

private:
  Params params;

  void refresh();
  bool isStorageMounted();
  bool isFilesystemPresent();
  bool isDriveInitialized();
  void mountStorage();
  void unmountStorage();
  void formatStorage();
  void checkAndUpdateFstab();
};
