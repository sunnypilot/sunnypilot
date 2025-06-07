#pragma once

#include <QLabel>
#include <QPushButton>

#include "common/params.h"

class ExitOffroadButton : public QPushButton {
  Q_OBJECT

private:
  QTimer *glowTimer;
  int glowAlpha = 100;  // Current alpha of glow
  int glowDelta = 10;    // Change per tick
  
public:
  explicit ExitOffroadButton(QWidget* parent = 0);

  Params params;
  bool offroad_mode;
  int img_width = 100;
  int horizontal_padding = 30;
  QPixmap pixmap;
  QLabel *mode_label;
  QLabel *mode_icon;

protected:
  void paintEvent(QPaintEvent *event) override;
};
