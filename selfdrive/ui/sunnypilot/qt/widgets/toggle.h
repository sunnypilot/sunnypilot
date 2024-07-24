#pragma once

#include "selfdrive/ui/qt/widgets/toggle.h"

class ToggleSP : public Toggle {
  Q_OBJECT

public:
  explicit ToggleSP(QWidget* parent = nullptr);

protected:
  void paintEvent(QPaintEvent*) override;
};
