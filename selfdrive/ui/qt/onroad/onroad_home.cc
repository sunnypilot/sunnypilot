#include "selfdrive/ui/qt/onroad/onroad_home.h"

#include <QPainter>
#include <QStackedLayout>
#include <QLinearGradient>
#include <QRadialGradient>
#include <QPainterPath>
#include <QEvent>

#include "selfdrive/ui/qt/util.h"

OnroadWindow::OnroadWindow(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout  = new QVBoxLayout(this);
  main_layout->setMargin(0); // Remove the margin to let camera view expand to edges
  QStackedLayout *stacked_layout = new QStackedLayout;
  stacked_layout->setStackingMode(QStackedLayout::StackAll);
  main_layout->addLayout(stacked_layout);

  nvg = new AnnotatedCameraWidget(VISION_STREAM_ROAD, this);

  QWidget * split_wrapper = new QWidget;
  split = new QHBoxLayout(split_wrapper);
  split->setContentsMargins(0, 0, 0, 0);
  split->setSpacing(0);
  split->addWidget(nvg);

  if (getenv("DUAL_CAMERA_VIEW")) {
    CameraWidget *arCam = new CameraWidget("camerad", VISION_STREAM_ROAD, this);
    split->insertWidget(0, arCam);
  }

  stacked_layout->addWidget(split_wrapper);

  alerts = new OnroadAlerts(this);
  alerts->setAttribute(Qt::WA_TransparentForMouseEvents, true);
  stacked_layout->addWidget(alerts);

  // Create our overlay widget for the fade effect
  fadeOverlay = new QWidget(this);
  fadeOverlay->setAttribute(Qt::WA_TransparentForMouseEvents, true);
  stacked_layout->addWidget(fadeOverlay);

  // setup stacking order
  alerts->raise();
  fadeOverlay->raise();

  setAttribute(Qt::WA_OpaquePaintEvent);

  // We handle the connection of the signals on the derived class
#ifndef SUNNYPILOT
  QObject::connect(uiState(), &UIState::uiUpdate, this, &OnroadWindow::updateState);
  QObject::connect(uiState(), &UIState::offroadTransition, this, &OnroadWindow::offroadTransition);
#endif

  // Connect paint event for fade overlay
  fadeOverlay->installEventFilter(this);
}

void OnroadWindow::updateState(const UIState &s) {
  if (!s.scene.started) {
    return;
  }

  alerts->updateState(s);
  nvg->updateState(s);

  QColor bgColor = bg_colors[s.status];
  if (bg != bgColor) {
    // repaint border
    bg = bgColor;
    fadeOverlay->update();
  }
}

void OnroadWindow::offroadTransition(bool offroad) {
  alerts->clear();
}

void OnroadWindow::paintEvent(QPaintEvent *event) {
  // move eventfilet in here but we will save it for another day
}

bool OnroadWindow::eventFilter(QObject *obj, QEvent *event) {
  if (obj == fadeOverlay && event->type() == QEvent::Paint) {
    QPainter p(fadeOverlay);
    p.setRenderHint(QPainter::Antialiasing);

    int borderWidth = UI_BORDER_SIZE;
    int w = width();
    int h = height();

    // Top edge
    QLinearGradient topGrad(0, 0, 0, borderWidth);
    topGrad.setColorAt(0, bg);
    topGrad.setColorAt(1, QColor(bg.red(), bg.green(), bg.blue(), 0));
    p.fillRect(0, 0, w, borderWidth, topGrad);

    // Bottom edge
    QLinearGradient bottomGrad(0, h - borderWidth, 0, h);
    bottomGrad.setColorAt(0, QColor(bg.red(), bg.green(), bg.blue(), 0));
    bottomGrad.setColorAt(1, bg);
    p.fillRect(0, h - borderWidth, w, borderWidth, bottomGrad);

    // Left edge
    QLinearGradient leftGrad(0, 0, borderWidth, 0);
    leftGrad.setColorAt(0, bg);
    leftGrad.setColorAt(1, QColor(bg.red(), bg.green(), bg.blue(), 0));
    p.fillRect(0, borderWidth, borderWidth, h - 2 * borderWidth, leftGrad);

    // Right edge
    QLinearGradient rightGrad(w - borderWidth, 0, w, 0);
    rightGrad.setColorAt(0, QColor(bg.red(), bg.green(), bg.blue(), 0));
    rightGrad.setColorAt(1, bg);
    p.fillRect(w - borderWidth, borderWidth, borderWidth, h - 2 * borderWidth, rightGrad);

    // Corner gradients - use radial gradients for smoother corner transitions
    int cornerSize = borderWidth;

    // Top-left corner
    QRadialGradient topLeftGrad(cornerSize, cornerSize, cornerSize);
    topLeftGrad.setColorAt(0, QColor(bg.red(), bg.green(), bg.blue(), 0));
    topLeftGrad.setColorAt(1, bg);
    p.fillRect(0, 0, cornerSize, cornerSize, topLeftGrad);

    // Top-right corner
    QRadialGradient topRightGrad(w - cornerSize, cornerSize, cornerSize);
    topRightGrad.setColorAt(0, QColor(bg.red(), bg.green(), bg.blue(), 0));
    topRightGrad.setColorAt(1, bg);
    p.fillRect(w - cornerSize, 0, cornerSize, cornerSize, topRightGrad);

    // Bottom-left corner
    QRadialGradient bottomLeftGrad(cornerSize, h - cornerSize, cornerSize);
    bottomLeftGrad.setColorAt(0, QColor(bg.red(), bg.green(), bg.blue(), 0));
    bottomLeftGrad.setColorAt(1, bg);
    p.fillRect(0, h - cornerSize, cornerSize, cornerSize, bottomLeftGrad);

    // Bottom-right corner
    QRadialGradient bottomRightGrad(w - cornerSize, h - cornerSize, cornerSize);
    bottomRightGrad.setColorAt(0, QColor(bg.red(), bg.green(), bg.blue(), 0));
    bottomRightGrad.setColorAt(1, bg);
    p.fillRect(w - cornerSize, h - cornerSize, cornerSize, cornerSize, bottomRightGrad);

    return true;
  }

  return QWidget::eventFilter(obj, event);
}