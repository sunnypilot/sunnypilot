#include "selfdrive/ui/qt/sidebar.h"

#include "selfdrive/ui/qt/qt_window.h"
#include "selfdrive/common/util.h"
#include "selfdrive/hardware/hw.h"
#include "selfdrive/ui/qt/util.h"

#include <QProcess>
#include <QSoundEffect>

void Sidebar::drawMetric(QPainter &p, const QString &label, const QString &val, QColor c, int y) {
  const QRect rect = {30, y, 240, val.isEmpty() ? (label.contains("\n") ? 124 : 100) : 148};

  p.setPen(Qt::NoPen);
  p.setBrush(QBrush(c));
  p.setClipRect(rect.x() + 6, rect.y(), 18, rect.height(), Qt::ClipOperation::ReplaceClip);
  p.drawRoundedRect(QRect(rect.x() + 6, rect.y() + 6, 100, rect.height() - 12), 10, 10);
  p.setClipping(false);

  QPen pen = QPen(QColor(0xff, 0xff, 0xff, 0x55));
  pen.setWidth(2);
  p.setPen(pen);
  p.setBrush(Qt::NoBrush);
  p.drawRoundedRect(rect, 20, 20);

  p.setPen(QColor(0xff, 0xff, 0xff));
  if (val.isEmpty()) {
    configFont(p, "Open Sans", 35, "Bold");
    const QRect r = QRect(rect.x() + 35, rect.y(), rect.width() - 50, rect.height());
    p.drawText(r, Qt::AlignCenter, label);
  } else {
    configFont(p, "Open Sans", 58, "Bold");
    p.drawText(rect.x() + 50, rect.y() + 71, val);
    configFont(p, "Open Sans", 35, "Regular");
    p.drawText(rect.x() + 50, rect.y() + 50 + 77, label);
  }
}

Sidebar::Sidebar(QWidget *parent) : QFrame(parent) {
  home_img = QImage("../assets/images/button_home.png").scaled(180, 180, Qt::KeepAspectRatio, Qt::SmoothTransformation);
  settings_img = QImage("../assets/images/button_settings.png").scaled(settings_btn.width(), settings_btn.height(), Qt::IgnoreAspectRatio, Qt::SmoothTransformation);;

  connect(this, &Sidebar::valueChanged, [=] { update(); });

  setFixedWidth(300);
  setMinimumHeight(vwp_h);
  setStyleSheet("background-color: rgb(57, 57, 57);");
}

void Sidebar::mousePressEvent(QMouseEvent *event) {
  if (settings_btn.contains(event->pos())) {
    QUIState::ui_state.scene.setbtn_count = QUIState::ui_state.scene.setbtn_count + 1;
    if (QUIState::ui_state.scene.setbtn_count > 1) {
      emit openSettings();
    }
    return;
  }
  // OPKR 
  if (home_btn.contains(event->pos())) {
      QUIState::ui_state.scene.homebtn_count = QUIState::ui_state.scene.homebtn_count + 1;
    if (QUIState::ui_state.scene.homebtn_count > 2) {
      QProcess::execute("/data/openpilot/run_mixplorer.sh");
    }
    return;
  }
  // OPKR map overlay
  if (overlay_btn.contains(event->pos()) && QUIState::ui_state.scene.started) {
    QSoundEffect effect;
    effect.setSource(QUrl::fromLocalFile("/data/openpilot/selfdrive/assets/sounds/warning_1.wav"));
    //effect.setLoopCount(1);
    //effect.setLoopCount(QSoundEffect::Infinite);
    //effect.setVolume(0.1);
    effect.play();
    QProcess::execute("am start --activity-task-on-home com.opkr.maphack/com.opkr.maphack.MainActivity");
    QUIState::ui_state.scene.map_on_top = false;
    QUIState::ui_state.scene.map_on_overlay = !QUIState::ui_state.scene.map_on_overlay;
  }
}

void Sidebar::updateState(const UIState &s) {
  auto &sm = *(s.sm);

  auto deviceState = sm["deviceState"].getDeviceState();
  setProperty("netType", network_type[deviceState.getNetworkType()]);
  setProperty("netStrength", signal_imgs[deviceState.getNetworkStrength()]);

  auto last_ping = deviceState.getLastAthenaPingTime();
  if (last_ping == 0) {
    setProperty("connectStr", "오프라인");
    setProperty("connectStatus", warning_color);
  } else {
    bool online = nanos_since_boot() - last_ping < 80e9;
    setProperty("connectStr",  online ? "온라인" : "오류");
    setProperty("connectStatus", online ? good_color : danger_color);
  }

  QColor tempStatus = danger_color;
  auto ts = deviceState.getThermalStatus();
  if (ts == cereal::DeviceState::ThermalStatus::GREEN) {
    tempStatus = good_color;
  } else if (ts == cereal::DeviceState::ThermalStatus::YELLOW) {
    tempStatus = warning_color;
  }
  setProperty("tempStatus", tempStatus);
  setProperty("tempVal", (int)deviceState.getAmbientTempC());

  QString pandaStr = "차량\n연결됨";
  QColor pandaStatus = good_color;
  if (s.scene.pandaType == cereal::PandaState::PandaType::UNKNOWN) {
    pandaStatus = danger_color;
    pandaStr = "차량\n연결안됨";
  } else if (s.scene.satelliteCount > 0) {
  	pandaStr = QString("차량연결됨\nSAT : %1").arg(s.scene.satelliteCount);
  } else if (Hardware::TICI() && s.scene.started) {
    pandaStr = QString("SATS %1\nACC %2").arg(s.scene.satelliteCount).arg(fmin(10, s.scene.gpsAccuracy), 0, 'f', 2);
    pandaStatus = sm["liveLocationKalman"].getLiveLocationKalman().getGpsOK() ? good_color : warning_color;
  }
  setProperty("pandaStr", pandaStr);
  setProperty("pandaStatus", pandaStatus);

  if (s.sm->updated("deviceState") || s.sm->updated("pandaState")) {
    // atom
    m_battery_img = s.scene.deviceState.getBatteryStatus() == "Charging" ? 1 : 0;
    m_batteryPercent = s.scene.deviceState.getBatteryPercent();
    m_strip = s.scene.deviceState.getWifiIpAddress();
    repaint();
  }
}

void Sidebar::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.setPen(Qt::NoPen);
  p.setRenderHint(QPainter::Antialiasing);

  // static imgs
  p.setOpacity(0.65);
  p.drawImage(settings_btn.x(), settings_btn.y(), settings_img);
  p.setOpacity(1.0);
  p.drawImage(60, 1080 - 180 - 40, home_img);

  // network
  p.drawImage(58, 196, net_strength);
  configFont(p, "Open Sans", 35, "Regular");
  p.setPen(QColor(0xff, 0xff, 0xff));
  const QRect r = QRect(50, 237, 100, 50);
  p.drawText(r, Qt::AlignCenter, net_type);

  // metrics
  drawMetric(p, "시스템온도", QString("%1°C").arg(temp_val), temp_status, 338);
  drawMetric(p, panda_str, "", panda_status, 518);
  drawMetric(p, "네트워크\n" + connect_str, "", connect_status, 676);

  // atom - ip
  if( m_batteryPercent <= 1) return;
  QString  strip = m_strip.c_str();
  const QRect r2 = QRect(35, 295, 230, 50);
  configFont(p, "Open Sans", 28, "Bold");
  p.setPen(Qt::yellow);
  p.drawText(r2, Qt::AlignHCenter, strip);

  // atom - battery
  QRect  rect(160, 247, 76, 36);
  QRect  bq(rect.left() + 6, rect.top() + 5, int((rect.width() - 19) * m_batteryPercent * 0.01), rect.height() - 11 );
  QBrush bgBrush("#149948");
  p.fillRect(bq, bgBrush);  
  p.drawImage(rect, battery_imgs[m_battery_img]);

  p.setPen(Qt::white);
  configFont(p, "Open Sans", 25, "Regular");

  char temp_value_str1[32];
  snprintf(temp_value_str1, sizeof(temp_value_str1), "%d%%", m_batteryPercent );
  p.drawText(rect, Qt::AlignCenter, temp_value_str1);
}
