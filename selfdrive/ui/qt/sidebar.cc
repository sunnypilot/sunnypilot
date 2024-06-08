#include "selfdrive/ui/qt/sidebar.h"

#include <cmath>

#include <QMouseEvent>
#include <common/swaglog.h>

#include "selfdrive/ui/qt/util.h"
#include "common/params.h"

void Sidebar::drawMetric(QPainter &p, const QPair<QString, QString> &label, QColor c, int y) {
  const QRect rect = {30, y, 240, 126};

  p.setPen(Qt::NoPen);
  p.setBrush(QBrush(c));
  p.setClipRect(rect.x() + 4, rect.y(), 18, rect.height(), Qt::ClipOperation::ReplaceClip);
  p.drawRoundedRect(QRect(rect.x() + 4, rect.y() + 4, 100, 118), 18, 18);
  p.setClipping(false);

  QPen pen = QPen(QColor(0xff, 0xff, 0xff, 0x55));
  pen.setWidth(2);
  p.setPen(pen);
  p.setBrush(Qt::NoBrush);
  p.drawRoundedRect(rect, 20, 20);

  p.setPen(QColor(0xff, 0xff, 0xff));
  p.setFont(InterFont(35, QFont::DemiBold));
  p.drawText(rect.adjusted(22, 0, 0, 0), Qt::AlignCenter, label.first + "\n" + label.second);
}

Sidebar::Sidebar(QWidget *parent) : QFrame(parent), onroad(false), flag_pressed(false), settings_pressed(false) {
  home_img = loadPixmap("../assets/images/button_home.png", home_btn.size());
  flag_img = loadPixmap("../assets/images/button_flag.png", home_btn.size());
  settings_img = loadPixmap("../assets/images/button_settings.png", settings_btn.size(), Qt::IgnoreAspectRatio);

  connect(this, &Sidebar::valueChanged, [=] { update(); });

  setAttribute(Qt::WA_OpaquePaintEvent);
  setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Expanding);
  setFixedWidth(300);

  QObject::connect(uiState(), &UIState::uiUpdate, this, &Sidebar::updateState);

  pm = std::make_unique<PubMaster, const std::initializer_list<const char *>>({"userFlag"});
}

void Sidebar::mousePressEvent(QMouseEvent *event) {
  if (onroad && home_btn.contains(event->pos())) {
    flag_pressed = true;
    update();
  } else if (settings_btn.contains(event->pos())) {
    settings_pressed = true;
    update();
  }
}

void Sidebar::mouseReleaseEvent(QMouseEvent *event) {
  if (flag_pressed || settings_pressed) {
    flag_pressed = settings_pressed = false;
    update();
  }
  if (onroad && home_btn.contains(event->pos())) {
    MessageBuilder msg;
    msg.initEvent().initUserFlag();
    pm->send("userFlag", msg);
  } else if (settings_btn.contains(event->pos())) {
    emit openSettings();
  }
}

void Sidebar::offroadTransition(bool offroad) {
  onroad = !offroad;
  update();
}

void Sidebar::updateState(const UIState &s) {
  if (!isVisible()) return;

  auto &sm = *(s.sm);

  auto deviceState = sm["deviceState"].getDeviceState();
  setProperty("netType", network_type[deviceState.getNetworkType()]);
  int strength = (int)deviceState.getNetworkStrength();
  setProperty("netStrength", strength > 0 ? strength + 1 : 0);

  ItemStatus connectStatus;
  auto last_ping = deviceState.getLastAthenaPingTime();
  if (last_ping == 0) {
    connectStatus = ItemStatus{{tr("CONNECT"), tr("OFFLINE")}, warning_color};
  } else {
    connectStatus = nanos_since_boot() - last_ping < 80e9
                        ? ItemStatus{{tr("CONNECT"), tr("ONLINE")}, good_color}
                        : ItemStatus{{tr("CONNECT"), tr("ERROR")}, danger_color};
  }
  setProperty("connectStatus", QVariant::fromValue(connectStatus));

  if (sm.frame % UI_FREQ == 0) { // Update every 1 Hz
    switch (s.scene.sidebar_temp_options) {
      case 0:
        break;
      case 1:
        sidebar_temp = QString::number((int)deviceState.getMemoryTempC());
        break;
      case 2: {
        const auto& cpu_temp_list = deviceState.getCpuTempC();
        float max_cpu_temp = std::numeric_limits<float>::lowest();

        for (const float& temp : cpu_temp_list) {
          max_cpu_temp = std::max(max_cpu_temp, temp);
        }

        if (max_cpu_temp >= 0) {
          sidebar_temp = QString::number(std::nearbyint(max_cpu_temp));
        }
        break;
      }
      case 3: {
        const auto& gpu_temp_list = deviceState.getGpuTempC();
        float max_gpu_temp = std::numeric_limits<float>::lowest();

        for (const float& temp : gpu_temp_list) {
          max_gpu_temp = std::max(max_gpu_temp, temp);
        }

        if (max_gpu_temp >= 0) {
          sidebar_temp = QString::number(std::nearbyint(max_gpu_temp));
        }
        break;
      }
      case 4:
        sidebar_temp = QString::number((int)deviceState.getMaxTempC());
        break;
      default:
        break;
    }

    setProperty("sidebarTemp", sidebar_temp + "°C");
  }

  bool show_sidebar_temp = s.scene.sidebar_temp_options != 0;
  ItemStatus tempStatus = {{tr("TEMP"), show_sidebar_temp ? sidebar_temp_str : tr("HIGH")}, danger_color};
  auto ts = deviceState.getThermalStatus();
  if (ts == cereal::DeviceState::ThermalStatus::GREEN) {
    tempStatus = {{tr("TEMP"), show_sidebar_temp ? sidebar_temp_str : tr("GOOD")}, good_color};
  } else if (ts == cereal::DeviceState::ThermalStatus::YELLOW) {
    tempStatus = {{tr("TEMP"), show_sidebar_temp ? sidebar_temp_str : tr("OK")}, warning_color};
  }
  setProperty("tempStatus", QVariant::fromValue(tempStatus));

  ItemStatus pandaStatus = {{tr("VEHICLE"), tr("ONLINE")}, good_color};
  if (s.scene.pandaType == cereal::PandaState::PandaType::UNKNOWN) {
    pandaStatus = {{tr("NO"), tr("PANDA")}, danger_color};
  } else if (s.scene.started && !sm["liveLocationKalman"].getLiveLocationKalman().getGpsOK()) {
    pandaStatus = {{tr("GPS"), tr("SEARCH")}, warning_color};
  }
  setProperty("pandaStatus", QVariant::fromValue(pandaStatus));
  
  ItemStatus sunnylinkStatus;
  auto last_sunnylink_ping = std::strtol(params.get("LastSunnylinkPingTime").c_str(), nullptr, 10);
  auto current_nanos = nanos_since_boot();
  auto elapsed_sunnylink_ping = current_nanos - last_sunnylink_ping;
  auto sunnylink_enabled = params.getBool("SunnylinkEnabled");
  if (!sunnylink_enabled) {
    sunnylinkStatus = ItemStatus{{tr("SUNNYLINK"), tr("DISABLED")}, disabled_color};
  } else if (last_sunnylink_ping == 0) {
    sunnylinkStatus = ItemStatus{{tr("SUNNYLINK"), tr("OFFLINE")}, warning_color};
  } else {
    if (static_cast<double>(elapsed_sunnylink_ping) < 80e9) {
      sunnylinkStatus = ItemStatus{{tr("SUNNYLINK"), tr("ONLINE")}, good_color};
    }
    else {
      LOGE("Sunnylink is offline, last ping: [%ld]. Current time: [%ld], diff: [%ld]", last_sunnylink_ping, current_nanos, elapsed_sunnylink_ping);
      sunnylinkStatus = ItemStatus{{tr("SUNNYLINK"), tr("ERROR")}, danger_color};
    }
  }
  setProperty("sunnylinkStatus", QVariant::fromValue(sunnylinkStatus));
}

void Sidebar::paintEvent(QPaintEvent *event) {
  QPainter p(this);
  p.setPen(Qt::NoPen);
  p.setRenderHint(QPainter::Antialiasing);

  p.fillRect(rect(), QColor(57, 57, 57));

  // buttons
  p.setOpacity(settings_pressed ? 0.65 : 1.0);
  p.drawPixmap(settings_btn.x(), settings_btn.y(), settings_img);
  p.setOpacity(onroad && flag_pressed ? 0.65 : 1.0);
  p.drawPixmap(home_btn.x(), home_btn.y(), onroad ? flag_img : home_img);
  p.setOpacity(1.0);

  // network
  int x = 58;
  const QColor gray(0x54, 0x54, 0x54);
  for (int i = 0; i < 5; ++i) {
    p.setBrush(i < net_strength ? Qt::white : gray);
    p.drawEllipse(x, 196, 27, 27);
    x += 37;
  }

  p.setFont(InterFont(35));
  p.setPen(QColor(0xff, 0xff, 0xff));
  const QRect r = QRect(50, 247, 100, 50);
  p.drawText(r, Qt::AlignCenter, net_type);

  // metrics
  drawMetric(p, temp_status.first, temp_status.second, 310);
  drawMetric(p, panda_status.first, panda_status.second, 440);
  drawMetric(p, connect_status.first, connect_status.second, 570);
  drawMetric(p, sunnylink_status.first, sunnylink_status.second, 700);
}
