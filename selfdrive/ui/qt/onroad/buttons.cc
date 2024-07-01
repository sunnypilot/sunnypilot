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

static void drawCustomButtonIcon(QPainter &p, const int btn_size_x, const int btn_size_y, const QPixmap &img, const QBrush &bg, float opacity) {
  QPoint center(btn_size_x / 2, btn_size_y / 2);
  p.setRenderHint(QPainter::Antialiasing);
  p.setOpacity(1.0);  // bg dictates opacity of ellipse
  p.setPen(Qt::NoPen);
  p.setBrush(bg);
  p.drawEllipse(center, btn_size_x / 2, btn_size_y / 2);
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
  bool can_change = (hasLongitudinalControl(cp) || (!cp.getPcmCruiseSpeed() && params.getBool("CustomStockLongPlanner")))
                    && params.getBool("ExperimentalModeConfirmed");
  if (can_change) {
    params.putBool("ExperimentalMode", !experimental_mode);
  }
}

void ExperimentalButton::updateState(const UIState &s) {
  const auto cs = (*s.sm)["controlsState"].getControlsState();
  const auto lp_sp = (*s.sm)["longitudinalPlanSP"].getLongitudinalPlanSP();
  bool eng = (cs.getEngageable() || cs.getEnabled()) && !(lp_sp.getVisionTurnControllerState() > cereal::LongitudinalPlanSP::VisionTurnControllerState::DISABLED);
  if ((cs.getExperimentalMode() != experimental_mode) || (eng != engageable)) {
    engageable = eng;
    experimental_mode = cs.getExperimentalMode();
    update();
  }
}

void ExperimentalButton::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  QPixmap img = experimental_mode ? experimental_img : engage_img;
  drawIcon(p, QPoint(btn_size / 2, btn_size / 2), img, QColor(0, 0, 0, 166), (isDown() || !engageable) ? 0.6 : 1.0);
}


// MapSettingsButton
MapSettingsButton::MapSettingsButton(QWidget *parent) : QPushButton(parent) {
  // btn_size: 192 * 80% ~= 152
  // img_size: (152 / 4) * 3 = 114
  setFixedSize(152, 152);
  settings_img = loadPixmap("../assets/navigation/icon_directions_outlined.svg", {114, 114});

  // hidden by default, made visible if map is created (has prime or mapbox token)
  setVisible(false);
  setEnabled(false);
}

void MapSettingsButton::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  drawCustomButtonIcon(p, 152, 152, settings_img, QColor(0, 0, 0, 166), isDown() ? 0.6 : 1.0);
}


// OnroadSettingsButton
OnroadSettingsButton::OnroadSettingsButton(QWidget *parent) : QPushButton(parent) {
  // btn_size: 192 * 80% ~= 152
  // img_size: (152 / 4) * 3 = 114
  setFixedSize(152, 152);
  settings_img = loadPixmap("../assets/navigation/icon_settings.svg", {114, 114});

  // hidden by default, made visible if Driving Personality / GAC, DLP, DEC, or SLC is enabled
  setVisible(false);
  setEnabled(false);
}

void OnroadSettingsButton::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  drawCustomButtonIcon(p, 152, 152, settings_img, QColor(0, 0, 0, 166), isDown() ? 0.6 : 1.0);
}

void OnroadSettingsButton::updateState(const UIState &s) {
  const auto cp = (*s.sm)["carParams"].getCarParams();
  auto dlp_enabled = s.scene.driving_model_gen == 1;
  bool allow_btn = s.scene.onroad_settings_toggle && (dlp_enabled || hasLongitudinalControl(cp) || !cp.getPcmCruiseSpeed());

  setVisible(allow_btn);
  setEnabled(allow_btn);
}
