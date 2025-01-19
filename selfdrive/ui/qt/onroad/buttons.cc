#include "selfdrive/ui/qt/onroad/buttons.h"

#include <QPainter>

#include "selfdrive/ui/qt/util.h"

void drawIcon(QPainter &p, const QPoint &center, const QPixmap &img, const QBrush &bg, float opacity) {
  p.setRenderHint(QPainter::Antialiasing);
  p.setOpacity(1.0);  // bg dictates opacity of ellipse
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(center, btn_size / 2, btn_size / 2);
  p.setOpacity(opacity);
  p.drawPixmap(center - QPoint(img.width() / 2, img.height() / 2), img);
  p.setOpacity(1.0);
}

// ExperimentalButton
ExperimentalButton::ExperimentalButton(QWidget *parent) : experimental_mode(false), engageable(false), QPushButton(parent) {
  setFixedSize(btn_size, btn_size);

  engage_img = loadPixmap("../assets/img_chffr_wheel.png", {img_size, img_size});
  experimental_img = loadPixmap("../assets/img_experimental.svg", {img_size, img_size});
  QObject::connect(this, &QPushButton::clicked, this, &ExperimentalButton::changeMode);
}

void ExperimentalButton::changeMode() {
  const auto cp = (*uiState()->sm)["carParams"].getCarParams();
  bool can_change = hasLongitudinalControl(cp) && params.getBool("ExperimentalModeConfirmed");
  if (can_change) {
    params.putBool("ExperimentalMode", !experimental_mode);
  }
}

void ExperimentalButton::updateState(const UIState &s) {
  const auto cs = (*s.sm)["selfdriveState"].getSelfdriveState();
  const auto long_plan_sp = (*s.sm)["longitudinalPlanSP"].getLongitudinalPlanSP();
  bool eng = cs.getEngageable() || cs.getEnabled();
  if ((cs.getExperimentalMode() != experimental_mode) || (eng != engageable)) {
    engageable = eng;
    experimental_mode = cs.getExperimentalMode();
    update();
  }

  int mode = int(long_plan_sp.getDec().getState());
  if ((long_plan_sp.getDec().getActive() != dynamic_experimental_control) || (mode != dec_mpc_mode)) {
    dynamic_experimental_control = long_plan_sp.getDec().getActive();
    dec_mpc_mode = mode;
    update();
  }
}

void ExperimentalButton::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  if (dynamic_experimental_control) {
    QPixmap left_half = engage_img.copy(0, 0, engage_img.width() / 2, engage_img.height());
    QPixmap right_half = experimental_img.copy(experimental_img.width() / 2, 0, experimental_img.width() / 2, experimental_img.height());

    QPixmap combined_img(engage_img.width(), engage_img.height());
    combined_img.fill(Qt::transparent);

    QPainter combined_painter(&combined_img);

    combined_painter.setOpacity(dec_mpc_mode == 1 ? 0.1 : 1.0);
    combined_painter.drawPixmap(0, 0, left_half);

    combined_painter.setOpacity(dec_mpc_mode == 1 ? 1.0 : 0.1);
    combined_painter.drawPixmap(engage_img.width() / 2, 0, right_half);

    combined_painter.end();

    drawIcon(p, QPoint(btn_size / 2, btn_size / 2), combined_img, QColor(0, 0, 0, 166), (isDown() || !engageable) ? 0.6 : 1.0);
  } else {
    QPixmap img = experimental_mode ? experimental_img : engage_img;
    drawIcon(p, QPoint(btn_size / 2, btn_size / 2), img, QColor(0, 0, 0, 166), (isDown() || !engageable) ? 0.6 : 1.0);
  }
}
