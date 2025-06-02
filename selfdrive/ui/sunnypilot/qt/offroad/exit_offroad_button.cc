#include <QDebug>
#include <QHBoxLayout>
#include <QPainter>
#include <QPainterPath>
#include <QStyle>

#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/widgets/input.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/exit_offroad_button.h"


ExitOffroadButton::ExitOffroadButton(QWidget *parent) : QPushButton(parent), glowTimer(new QTimer(this)) {
  setMouseTracking(true);

  connect(glowTimer, &QTimer::timeout, this, [this]() {
    // Pulse alpha up and down
    glowAlpha += glowDelta;
    if (glowAlpha > 220 || glowAlpha < 10) {
      glowDelta *= -1;
    }
    update(); // trigger repaint
  });

  glowTimer->start(45);
  
  pixmap = QPixmap("../../sunnypilot/selfdrive/assets/offroad/icon_exit_offroad.png").scaledToWidth(img_width, Qt::SmoothTransformation);

  // go to toggles and expand experimental mode description
  connect(this, &QPushButton::clicked, [=]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to exit Always Offroad mode?"), tr("Confirm"), this)) {
      params.remove("OffroadMode");
    }
  });

  setFixedHeight(125);
  QHBoxLayout *main_layout = new QHBoxLayout;
  main_layout->setContentsMargins(horizontal_padding, 0, horizontal_padding, 0);

  mode_label = new QLabel(tr("EXIT ALWAYS OFFROAD MODE"));
  mode_icon = new QLabel;
  mode_icon->setSizePolicy(QSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed));
  mode_icon->setPixmap(pixmap);

  main_layout->addWidget(mode_label, 1, Qt::AlignLeft);
  main_layout->addWidget(mode_icon, 0, Qt::AlignRight);

  setLayout(main_layout);

  setStyleSheet(R"(
    QPushButton {
      border: none;
    }

    QLabel {
      font-size: 45px;
      font-weight: 300;
      text-align: left;
      font-family: JetBrainsMono;
      color: #000000;
    }
  )");
}

void drawPulsingGlowOverlay(QPainter &p, QPainterPath path, int glowAlpha) {
  // Draw pulsing glow effect clipped to button area
  p.save();
  p.setClipPath(path);
  p.setCompositionMode(QPainter::CompositionMode_HardLight);

  const QColor animatedGlowColor(255, 255, 255, std::min(255, glowAlpha));
  QPen glowPen(animatedGlowColor, 8);
  glowPen.setJoinStyle(Qt::RoundJoin);
  p.setPen(glowPen);
  p.drawPath(path);
  
  p.restore();
}

void ExitOffroadButton::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.setRenderHint(QPainter::Antialiasing);

  QPainterPath path;
  path.addRoundedRect(rect(), 10, 10);

  // gradient
  bool pressed = isDown();
  QLinearGradient gradient(rect().left(), 0, rect().right(), 0);
  gradient.setColorAt(0, QColor(35, 149, 255, pressed ? 0xcc : 0xff));
  gradient.setColorAt(0.3, QColor(35, 149, 255, pressed ? 0xcc : 0xff));
  gradient.setColorAt(1, QColor(20, 255, 171, pressed ? 0xcc : 0xff));
  p.fillPath(path, gradient);

  drawPulsingGlowOverlay(p, path, glowAlpha);

  // vertical line
  p.setPen(QPen(QColor(0, 0, 0, 0x4d), 3, Qt::SolidLine));
  int line_x = rect().right() - img_width - (2 * horizontal_padding);
  p.drawLine(line_x, rect().bottom(), line_x, rect().top());
}
