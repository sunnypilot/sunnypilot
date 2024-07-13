#include "selfdrive/ui/sunnypilot/qt/offroad/sp_priv_settings.h"

#include "selfdrive/ui/qt/network/networking.h"
#include "selfdrive/ui/sunnypilot/sunnypilot_main.h"

SettingsWindowSP::SettingsWindowSP(QWidget *parent) : SettingsWindow(parent) {

  // setup two main layouts
  sidebar_widget = new QWidget;
  QVBoxLayout *sidebar_layout = new QVBoxLayout(sidebar_widget);
  panel_widget = new QStackedWidget();

  // setup layout for close button
  QVBoxLayout *close_btn_layout = new QVBoxLayout;
  close_btn_layout->setContentsMargins(0, 0, 0, 20);

  // close button
  QPushButton *close_btn = new QPushButton(tr("×"));
  close_btn->setStyleSheet(R"(
    QPushButton {
      font-size: 140px;
      padding-bottom: 20px;
      border-radius: 76px;
      background-color: #292929;
      font-weight: 400;
    }
    QPushButton:pressed {
      background-color: #3B3B3B;
    }
  )");
  close_btn->setFixedSize(152, 152);
  close_btn_layout->addWidget(close_btn, 0, Qt::AlignLeft);
  QObject::connect(close_btn, &QPushButton::clicked, this, &SettingsWindow::closeSettings);

  // setup buttons widget
  QWidget *buttons_widget = new QWidget;
  QVBoxLayout *buttons_layout = new QVBoxLayout(buttons_widget);
  buttons_layout->setMargin(0);
  buttons_layout->addSpacing(10);

  // setup panels
  DevicePanel *device = new DevicePanel(this);
  QObject::connect(device, &DevicePanel::reviewTrainingGuide, this, &SettingsWindow::reviewTrainingGuide);
  QObject::connect(device, &DevicePanel::showDriverView, this, &SettingsWindow::showDriverView);

  TogglesPanel *toggles = new TogglesPanel(this);
  QObject::connect(this, &SettingsWindow::expandToggleDescription, toggles, &TogglesPanel::expandToggleDescription);

  QList<PanelInfo> panels = {
    PanelInfo("   " + tr("Device"), device, "../assets/navigation/icon_home.svg"),
    PanelInfo("   " + tr("Network"), new Networking(this), "../assets/offroad/icon_network.png"),
    PanelInfo("   " + tr("sunnylink"), new SunnylinkPanel(this), "../assets/offroad/icon_wifi_strength_full.svg"),
    PanelInfo("   " + tr("Toggles"), toggles, "../assets/offroad/icon_toggle.png"),
    PanelInfo("   " + tr("Software"), new SoftwarePanelSP(this), "../assets/offroad/icon_software.png"),
    PanelInfo("   " + tr("sunnypilot"), new SunnypilotPanel(this), "../assets/offroad/icon_openpilot.png"),
    PanelInfo("   " + tr("OSM"), new OsmPanel(this), "../assets/offroad/icon_map.png"),
    PanelInfo("   " + tr("Monitoring"), new MonitoringPanel(this), "../assets/offroad/icon_monitoring.png"),
    PanelInfo("   " + tr("Visuals"), new VisualsPanel(this), "../assets/offroad/icon_visuals.png"),
    PanelInfo("   " + tr("Display"), new DisplayPanel(this), "../assets/offroad/icon_display.png"),
    PanelInfo("   " + tr("Trips"), new TripsPanel(this), "../assets/offroad/icon_trips.png"),
    PanelInfo("   " + tr("Vehicle"), new VehiclePanel(this), "../assets/offroad/icon_vehicle.png"),
  };

  nav_btns = new QButtonGroup(this);
  for (auto &[name, panel, icon] : panels) {
    QPushButton *btn = new QPushButton(name);
    btn->setCheckable(true);
    btn->setChecked(nav_btns->buttons().size() == 0);
    btn->setIcon(QIcon(QPixmap(icon)));
    btn->setIconSize(QSize(70, 70));
    btn->setStyleSheet(R"(
      QPushButton {
        border-radius: 20px;
        width: 400px;
        height: 98px;
        color: #bdbdbd;
        border: none;
        background: none;
        font-size: 50px;
        font-weight: 500;
        text-align: left;
        padding-left: 22px;
      }
      QPushButton:checked {
        background-color: #696868;
        color: white;
      }
      QPushButton:pressed {
        color: #ADADAD;
      }
    )");
    btn->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Expanding);
    nav_btns->addButton(btn);
    buttons_layout->addWidget(btn, 0, Qt::AlignLeft | Qt::AlignBottom);

    const int lr_margin = (name != ("   " + tr("Network")) || (name != ("   " + tr("sunnypilot")))) ? 50 : 0;  // Network and sunnypilot panel handles its own margins
    panel->setContentsMargins(lr_margin, 25, lr_margin, 25);

    ScrollView *panel_frame = new ScrollView(panel, this);
    panel_widget->addWidget(panel_frame);

    QObject::connect(btn, &QPushButton::clicked, [=, w = panel_frame]() {
      btn->setChecked(true);
      panel_widget->setCurrentWidget(w);
    });
  }
  sidebar_layout->setContentsMargins(50, 50, 25, 50);

  // main settings layout, sidebar + main panel
  QHBoxLayout *main_layout = new QHBoxLayout(this);

  // add layout for close button
  sidebar_layout->addLayout(close_btn_layout);

  // add layout for buttons scrolling
  ScrollView *buttons_scrollview  = new ScrollView(buttons_widget, this);
  sidebar_layout->addWidget(buttons_scrollview);

  sidebar_widget->setFixedWidth(500);
  main_layout->addWidget(sidebar_widget);
  main_layout->addWidget(panel_widget);

  setStyleSheet(R"(
    * {
      color: white;
      font-size: 50px;
    }
    SettingsWindow {
      background-color: black;
    }
    QStackedWidget, ScrollView {
      background-color: black;
      border-radius: 30px;
    }
  )");
}
