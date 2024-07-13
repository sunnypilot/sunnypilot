#pragma once

#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/drive_stats.h"

class TripsPanel : public QFrame {
  Q_OBJECT

public:
  explicit TripsPanel(QWidget* parent = 0);

private:
  Params params;

  QStackedLayout* center_layout;
  DriveStats *driveStatsWidget;
};
