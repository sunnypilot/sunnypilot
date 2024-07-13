#include "selfdrive/ui/sunnypilot/qt/sp_priv_home.h"

#include <QHBoxLayout>
#include <QMouseEvent>
#include <QStackedWidget>
#include <QVBoxLayout>

#include "selfdrive/ui/qt/offroad/experimental_mode.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/prime.h"

#ifdef ENABLE_MAPS
#include "selfdrive/ui/qt/maps/map_settings.h"
#endif

// HomeWindowSP: the container for the offroad and onroad UIs
HomeWindowSP::HomeWindowSP(QWidget* parent) : HomeWindow(parent){    
  QObject::connect(onroad, &OnroadWindow::mapPanelRequested, this, [=] { sidebar->hide(); });
  QObject::connect(onroad, &OnroadWindow::onroadSettingsPanelRequested, this, [=] { sidebar->hide(); });
}

void HomeWindowSP::showMapPanel(bool show) {
  onroad->showMapPanel(show);
}

void HomeWindowSP::updateState(const UIState &s) { //OVERRIDE
  HomeWindow::updateState(s);

  uiState()->scene.map_visible = onroad->isMapVisible();
  uiState()->scene.onroad_settings_visible = onroad->isOnroadSettingsVisible();
}

void HomeWindowSP::mousePressEvent(QMouseEvent* e) {
  HomeWindow::mousePressEvent(e); // We call it first so that we could potentially override whatever was done by parent
  
  if (uiState()->scene.started) {
    if (uiState()->scene.onroadScreenOff != -2) {
      uiState()->scene.touched2 = true;
      QTimer::singleShot(500, []() { uiState()->scene.touched2 = false; });
    }
    if (uiState()->scene.button_auto_hide) {
      uiState()->scene.touch_to_wake = true;
      uiState()->scene.sleep_btn_fading_in = true;
      QTimer::singleShot(500, []() { uiState()->scene.touch_to_wake = false; });
    }
  }

  // TODO: a very similar, but not identical call is made by parent. Which made me question if I should override it here... 
  //  Will have to revisit later if this is not behaving as expected. 
  // Handle sidebar collapsing
  if ((onroad->isVisible() || body->isVisible()) && (!sidebar->isVisible() || e->x() > sidebar->width())) {
    if (onroad->wakeScreenTimeout()) {
      sidebar->setVisible(!sidebar->isVisible() && !onroad->isMapVisible());
    }
  }
}

// OffroadHome: the offroad home page
//
// OffroadHomeSP::OffroadHomePS(QWidget* parent) : QFrame(parent) {
//   QVBoxLayout* main_layout = new QVBoxLayout(this);
//   main_layout->setContentsMargins(40, 40, 40, 40);
//
//   // top header
//   QHBoxLayout* header_layout = new QHBoxLayout();
//   header_layout->setContentsMargins(0, 0, 0, 0);
//   header_layout->setSpacing(16);
//
//   update_notif = new QPushButton(tr("UPDATE"));
//   update_notif->setVisible(false);
//   update_notif->setStyleSheet("background-color: #364DEF;");
//   QObject::connect(update_notif, &QPushButton::clicked, [=]() { center_layout->setCurrentIndex(1); });
//   header_layout->addWidget(update_notif, 0, Qt::AlignHCenter | Qt::AlignLeft);
//
//   alert_notif = new QPushButton();
//   alert_notif->setVisible(false);
//   alert_notif->setStyleSheet("background-color: #E22C2C;");
//   QObject::connect(alert_notif, &QPushButton::clicked, [=] { center_layout->setCurrentIndex(2); });
//   header_layout->addWidget(alert_notif, 0, Qt::AlignHCenter | Qt::AlignLeft);
//
//   version = new ElidedLabel();
//   header_layout->addWidget(version, 0, Qt::AlignHCenter | Qt::AlignRight);
//
//   main_layout->addLayout(header_layout);
//
//   // main content
//   main_layout->addSpacing(25);
//   center_layout = new QStackedLayout();
//
//   QWidget *home_widget = new QWidget(this);
//   {
//     QHBoxLayout *home_layout = new QHBoxLayout(home_widget);
//     home_layout->setContentsMargins(0, 0, 0, 0);
//     home_layout->setSpacing(30);
//
//     // left: PrimeAdWidget
//     QStackedWidget *left_widget = new QStackedWidget(this);
//     QVBoxLayout *left_prime_layout = new QVBoxLayout();
//     QWidget *prime_user = new PrimeUserWidget();
//     prime_user->setStyleSheet(R"(
//     border-radius: 10px;
//     background-color: #333333;
//     )");
//     left_prime_layout->addWidget(prime_user);
//     left_prime_layout->addStretch();
//     left_widget->addWidget(new LayoutWidget(left_prime_layout));
//     left_widget->addWidget(new PrimeAdWidget);
//     left_widget->setStyleSheet("border-radius: 10px;");
//
//     left_widget->setCurrentIndex(uiState()->hasPrime() ? 0 : 1);
//     connect(uiState(), &UIState::primeChanged, [=](bool prime) {
//       left_widget->setCurrentIndex(prime ? 0 : 1);
//     });
//
//     home_layout->addWidget(left_widget, 1);
//
//     // right: ExperimentalModeButton, SetupWidget
//     QWidget* right_widget = new QWidget(this);
//     QVBoxLayout* right_column = new QVBoxLayout(right_widget);
//     right_column->setContentsMargins(0, 0, 0, 0);
//     right_widget->setFixedWidth(750);
//     right_column->setSpacing(30);
//
//     ExperimentalModeButton *experimental_mode = new ExperimentalModeButton(this);
//     QObject::connect(experimental_mode, &ExperimentalModeButton::openSettings, this, &OffroadHome::openSettings);
//     right_column->addWidget(experimental_mode, 1);
//
//     SetupWidget *setup_widget = new SetupWidget;
//     QObject::connect(setup_widget, &SetupWidget::openSettings, this, &OffroadHome::openSettings);
//     right_column->addWidget(setup_widget, 1);
//
//     home_layout->addWidget(right_widget, 1);
//   }
//   center_layout->addWidget(home_widget);
//
//   // add update & alerts widgets
//   update_widget = new UpdateAlert();
//   QObject::connect(update_widget, &UpdateAlert::dismiss, [=]() { center_layout->setCurrentIndex(0); });
//   center_layout->addWidget(update_widget);
//   alerts_widget = new OffroadAlert();
//   QObject::connect(alerts_widget, &OffroadAlert::dismiss, [=]() { center_layout->setCurrentIndex(0); });
//   center_layout->addWidget(alerts_widget);
//
//   main_layout->addLayout(center_layout, 1);
//
//   // set up refresh timer
//   timer = new QTimer(this);
//   timer->callOnTimeout(this, &OffroadHome::refresh);
//
//   setStyleSheet(R"(
//     * {
//       color: white;
//     }
//     OffroadHome {
//       background-color: black;
//     }
//     OffroadHome > QPushButton {
//       padding: 15px 30px;
//       border-radius: 5px;
//       font-size: 40px;
//       font-weight: 500;
//     }
//     OffroadHome > QLabel {
//       font-size: 55px;
//     }
//   )");
// }