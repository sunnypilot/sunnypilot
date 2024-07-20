#include "selfdrive/ui/sunnypilot/qt/onroad/sp_priv_buttons.h"
#include "selfdrive/ui/qt/util.h"


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

// ExperimentalButtonSP
void ExperimentalButtonSP::updateState(const UIStateSP &s) {
    const auto cs = (*s.sm)["controlsState"].getControlsState();
    bool eng = cs.getEngageable() || cs.getEnabled();
    if ((cs.getExperimentalMode() != experimental_mode) || (eng != engageable)) {
        engageable = eng;
        experimental_mode = cs.getExperimentalMode();
        update();
    }
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

void OnroadSettingsButton::updateState(const UIStateSP &s) {
    const auto cp = (*s.sm)["carParams"].getCarParams();
    auto dlp_enabled = s.scene.driving_model_generation == cereal::ModelGeneration::ONE;
    bool allow_btn = s.scene.onroad_settings_toggle && (dlp_enabled || hasLongitudinalControl(cp) || !cp.getPcmCruiseSpeed());

    setVisible(allow_btn);
    setEnabled(allow_btn);
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
