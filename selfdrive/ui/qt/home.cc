#include "selfdrive/ui/qt/home.h"

#include <QDateTime>
#include <QHBoxLayout>
#include <QMouseEvent>
#include <QVBoxLayout>
#include <QProcess>
#include <QSoundEffect>

#include "selfdrive/common/params.h"
#include "selfdrive/common/swaglog.h"
#include "selfdrive/common/timing.h"
#include "selfdrive/common/util.h"
#include "selfdrive/ui/qt/widgets/drive_stats.h"
#include "selfdrive/ui/qt/widgets/setup.h"

// HomeWindow: the container for the offroad and onroad UIs

HomeWindow::HomeWindow(QWidget* parent) : QWidget(parent) {
  QHBoxLayout *layout = new QHBoxLayout(this);
  layout->setMargin(0);
  layout->setSpacing(0);

  sidebar = new Sidebar(this);
  layout->addWidget(sidebar);
  QObject::connect(this, &HomeWindow::update, sidebar, &Sidebar::updateState);
  QObject::connect(sidebar, &Sidebar::openSettings, this, &HomeWindow::openSettings);

  slayout = new QStackedLayout();
  layout->addLayout(slayout);

  onroad = new OnroadWindow(this);
  slayout->addWidget(onroad);

  QObject::connect(this, &HomeWindow::update, onroad, &OnroadWindow::update);
  QObject::connect(this, &HomeWindow::offroadTransitionSignal, onroad, &OnroadWindow::offroadTransitionSignal);

  home = new OffroadHome();
  slayout->addWidget(home);
  QObject::connect(this, &HomeWindow::openSettings, home, &OffroadHome::refresh);

  driver_view = new DriverViewWindow(this);
  connect(driver_view, &DriverViewWindow::done, [=] {
    showDriverView(false);
  });
  slayout->addWidget(driver_view);

  setLayout(layout);
}

void HomeWindow::offroadTransition(bool offroad) {
  if (offroad) {
    slayout->setCurrentWidget(home);
  } else {
    slayout->setCurrentWidget(onroad);
  }
  sidebar->setVisible(offroad);
  emit offroadTransitionSignal(offroad);
}

void HomeWindow::showDriverView(bool show) {
  if (show) {
    emit closeSettings();
    slayout->setCurrentWidget(driver_view);
  } else {
    slayout->setCurrentWidget(home);
  }
  sidebar->setVisible(show == false);
}

void HomeWindow::mousePressEvent(QMouseEvent* e) {
  // OPKR add map
  if (QUIState::ui_state.scene.started && map_overlay_btn.ptInRect(e->x(), e->y())) {
    QSoundEffect effect1;
    effect1.setSource(QUrl::fromLocalFile("/data/openpilot/selfdrive/assets/sounds/warning_1.wav"));
    //effect1.setLoopCount(1);
    //effect1.setLoopCount(QSoundEffect::Infinite);
    //effect1.setVolume(0.1);
    effect1.play();
    QProcess::execute("am start --activity-task-on-home com.opkr.maphack/com.opkr.maphack.MainActivity");
    QUIState::ui_state.scene.map_on_top = false;
    QUIState::ui_state.scene.map_on_overlay = !QUIState::ui_state.scene.map_on_overlay;
    return;
  }
  if (QUIState::ui_state.scene.started && !sidebar->isVisible() && !QUIState::ui_state.scene.map_on_top && map_btn.ptInRect(e->x(), e->y())) {
    QSoundEffect effect2;
    effect2.setSource(QUrl::fromLocalFile("/data/openpilot/selfdrive/assets/sounds/warning_1.wav"));
    //effect2.setLoopCount(1);
    //effect2.setLoopCount(QSoundEffect::Infinite);
    //effect2.setVolume(0.1);
    effect2.play();
    QProcess::execute("am start com.skt.tmap.ku/com.skt.tmap.activity.TmapNaviActivity");
    QUIState::ui_state.scene.map_on_top = true;
    Params().put("OpkrMapEnable", "1", 1);
    return;
  }
  // OPKR REC
  if (QUIState::ui_state.scene.started && !sidebar->isVisible() && !QUIState::ui_state.scene.map_on_top && !QUIState::ui_state.scene.comma_stock_ui && rec_btn.ptInRect(e->x(), e->y())) {
    QUIState::ui_state.scene.recording = !QUIState::ui_state.scene.recording;
    QUIState::ui_state.scene.touched = true;
    return;
  }
  // Laneless mode
  if (QUIState::ui_state.scene.started && !sidebar->isVisible() && !QUIState::ui_state.scene.map_on_top && QUIState::ui_state.scene.end_to_end && !QUIState::ui_state.scene.comma_stock_ui && laneless_btn.ptInRect(e->x(), e->y())) {
    QUIState::ui_state.scene.laneless_mode = QUIState::ui_state.scene.laneless_mode + 1;
    if (QUIState::ui_state.scene.laneless_mode > 2) {
      QUIState::ui_state.scene.laneless_mode = 0;
    }
    if (QUIState::ui_state.scene.laneless_mode == 0) {
      Params().put("LanelessMode", "0", 1);
    } else if (QUIState::ui_state.scene.laneless_mode == 1) {
      Params().put("LanelessMode", "1", 1);
    } else if (QUIState::ui_state.scene.laneless_mode == 2) {
      Params().put("LanelessMode", "2", 1);
    }
    return;
  }
  // Monitoring mode
  if (QUIState::ui_state.scene.started && !sidebar->isVisible() && !QUIState::ui_state.scene.map_on_top && monitoring_btn.ptInRect(e->x(), e->y())) {
    QUIState::ui_state.scene.monitoring_mode = !QUIState::ui_state.scene.monitoring_mode;
    if (QUIState::ui_state.scene.monitoring_mode) {
      Params().put("OpkrMonitoringMode", "1", 1);
    } else {
      Params().put("OpkrMonitoringMode", "0", 1);
    }
    return;
  }
  // // ML Button
  // if (QUIState::ui_state.scene.started && !sidebar->isVisible() && !QUIState::ui_state.scene.map_on_top && QUIState::ui_state.scene.model_long && !QUIState::ui_state.scene.comma_stock_ui && ml_btn.ptInRect(e->x(), e->y())) {
  //   QUIState::ui_state.scene.mlButtonEnabled = !QUIState::ui_state.scene.mlButtonEnabled;
  //   if (QUIState::ui_state.scene.mlButtonEnabled) {
  //     Params().put("ModelLongEnabled", "1", 1);
  //   } else {
  //     Params().put("ModelLongEnabled", "0", 1);
  //   }
  //   return;
  // }
  // Stock UI Toggle
  if (QUIState::ui_state.scene.started && !sidebar->isVisible() && !QUIState::ui_state.scene.map_on_top && stockui_btn.ptInRect(e->x(), e->y())) {
    QUIState::ui_state.scene.comma_stock_ui = !QUIState::ui_state.scene.comma_stock_ui;
    if (QUIState::ui_state.scene.comma_stock_ui) {
      Params().put("CommaStockUI", "1", 1);
    } else {
      Params().put("CommaStockUI", "0", 1);
    }
    return;
  }
  // Handle sidebar collapsing
  if (onroad->isVisible() && (!sidebar->isVisible() || e->x() > sidebar->width())) {

    // TODO: Handle this without exposing pointer to map widget
    // Hide map first if visible, then hide sidebar
    if (onroad->map != nullptr && onroad->map->isVisible()){
      onroad->map->setVisible(false);
    } else if (!sidebar->isVisible()) {
      sidebar->setVisible(true);
    } else {
      sidebar->setVisible(false);

      if (onroad->map != nullptr) onroad->map->setVisible(true);
    }
    QUIState::ui_state.sidebar_view = !QUIState::ui_state.sidebar_view;
  }

  QUIState::ui_state.scene.setbtn_count = 0;
  QUIState::ui_state.scene.homebtn_count = 0;
}

// OffroadHome: the offroad home page

OffroadHome::OffroadHome(QWidget* parent) : QFrame(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout();
  main_layout->setMargin(50);

  // top header
  QHBoxLayout* header_layout = new QHBoxLayout();

  date = new QLabel();
  date->setStyleSheet(R"(font-size: 55px;)");
  header_layout->addWidget(date, 0, Qt::AlignHCenter | Qt::AlignLeft);

  alert_notification = new QPushButton();
  alert_notification->setVisible(false);
  QObject::connect(alert_notification, &QPushButton::released, this, &OffroadHome::openAlerts);
  header_layout->addWidget(alert_notification, 0, Qt::AlignHCenter | Qt::AlignRight);

  std::string brand = Params().getBool("Passive") ? "대시캠" : "오픈파일럿";
  QLabel* version = new QLabel(QString::fromStdString(brand + " v" + Params().get("Version")));
  version->setStyleSheet(R"(font-size: 45px;)");
  header_layout->addWidget(version, 0, Qt::AlignHCenter | Qt::AlignRight);

  main_layout->addLayout(header_layout);

  // main content
  main_layout->addSpacing(25);
  center_layout = new QStackedLayout();

  QHBoxLayout* statsAndSetup = new QHBoxLayout();
  statsAndSetup->setMargin(0);

  DriveStats* drive = new DriveStats;
  drive->setFixedSize(800, 800);
  statsAndSetup->addWidget(drive);

  SetupWidget* setup = new SetupWidget;
  statsAndSetup->addWidget(setup);

  QWidget* statsAndSetupWidget = new QWidget();
  statsAndSetupWidget->setLayout(statsAndSetup);

  center_layout->addWidget(statsAndSetupWidget);

  alerts_widget = new OffroadAlert();
  QObject::connect(alerts_widget, &OffroadAlert::closeAlerts, this, &OffroadHome::closeAlerts);
  center_layout->addWidget(alerts_widget);
  center_layout->setAlignment(alerts_widget, Qt::AlignCenter);

  main_layout->addLayout(center_layout, 1);

  // set up refresh timer
  timer = new QTimer(this);
  QObject::connect(timer, &QTimer::timeout, this, &OffroadHome::refresh);
  timer->start(10 * 1000);

  setLayout(main_layout);
  setStyleSheet(R"(
    OffroadHome {
      background-color: black;
    }
    * {
     color: white;
    }
  )");
}

void OffroadHome::showEvent(QShowEvent *event) {
  refresh();
}

void OffroadHome::openAlerts() {
  center_layout->setCurrentIndex(1);
}

void OffroadHome::closeAlerts() {
  center_layout->setCurrentIndex(0);
}

void OffroadHome::refresh() {
  bool first_refresh = !date->text().size();
  if (!isVisible() && !first_refresh) {
    return;
  }

  date->setText(QDateTime::currentDateTime().toString("yyyy년 M월 d일"));

  // update alerts

  alerts_widget->refresh();
  if (!alerts_widget->alertCount && !alerts_widget->updateAvailable) {
    emit closeAlerts();
    alert_notification->setVisible(false);
    return;
  }

  if (alerts_widget->updateAvailable) {
    alert_notification->setText("업데이트");
  } else {
    int alerts = alerts_widget->alertCount;
    alert_notification->setText(QString::number(alerts) + " 경고" + (alerts == 1 ? "" : "S"));
  }

  if (!alert_notification->isVisible() && !first_refresh) {
    emit openAlerts();
  }
  alert_notification->setVisible(true);

  // Red background for alerts, blue for update available
  QString style = QString(R"(
    padding: 15px;
    padding-left: 30px;
    padding-right: 30px;
    border: 1px solid;
    border-radius: 5px;
    font-size: 40px;
    font-weight: 500;
    background-color: #E22C2C;
  )");
  if (alerts_widget->updateAvailable) {
    style.replace("#E22C2C", "#364DEF");
  }
  alert_notification->setStyleSheet(style);
}
