/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"

#include <tuple>
#include <vector>

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/device_panel.h"
#include "selfdrive/ui/sunnypilot/qt/network/networking.h"
#include "selfdrive/ui/sunnypilot/sunnypilot_main.h"

TogglesPanelSP::TogglesPanelSP(SettingsWindow *parent) : TogglesPanel(parent) {
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "OpenpilotEnabledToggle",
      tr("Enable sunnypilot"),
      tr("Use the sunnypilot system for adaptive cruise control and lane keep driver assistance. Your attention is required at all times to use this feature. Changing this setting takes effect when the car is powered off."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "ExperimentalLongitudinalEnabled",
      tr("openpilot Longitudinal Control (Alpha)"),
      QString("<b>%1</b><br><br>%2")
      .arg(tr("WARNING: sunnypilot longitudinal control is in alpha for this car and will disable Automatic Emergency Braking (AEB)."))
      .arg(tr("On this car, sunnypilot defaults to the car's built-in ACC instead of openpilot's longitudinal control. "
              "Enable this to switch to sunnypilot longitudinal control. Enabling Experimental mode is recommended when enabling sunnypilot longitudinal control alpha.")),
      "../assets/offroad/icon_blank.png",
    },
    {
      "CustomStockLong",
      tr("Custom Stock Longitudinal Control"),
      tr("When enabled, sunnypilot will attempt to control stock longitudinal control with ACC button presses.\nThis feature must be used along with SLC, and/or V-TSC, and/or M-TSC."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "ExperimentalMode",
      tr("Experimental Mode"),
      "",
      "../assets/offroad/icon_blank.png",
    },
    {
      "DynamicExperimentalControl",
      tr("Enable Dynamic Experimental Control"),
      tr("Enable toggle to allow the model to determine when to use sunnypilot ACC or sunnypilot End to End Longitudinal."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DynamicPersonality",
      tr("Enable Dynamic Personality"),
      tr("Enable this to allow sunnypilot to dynamically adjust following distance and reaction based on your \"Driving Personality\" setting. "
        "Instead of predefined settings for each personality, every personality now adapts dynamically according to your speed and the distance to the lead car."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DisengageOnAccelerator",
      tr("Disengage on Accelerator Pedal"),
      tr("When enabled, pressing the accelerator pedal will disengage openpilot."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "IsLdwEnabled",
      tr("Enable Lane Departure Warnings"),
      tr("Receive alerts to steer back into the lane when your vehicle drifts over a detected lane line without a turn signal activated while driving over 31 mph (50 km/h)."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "AlwaysOnDM",
      tr("Always-On Driver Monitoring"),
      tr("Enable driver monitoring even when sunnypilot is not engaged."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "RecordFront",
      tr("Record and Upload Driver Camera"),
      tr("Upload data from the driver facing camera and help improve the driver monitoring algorithm."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DisableOnroadUploads",
      tr("Disable Onroad Uploads"),
      tr("Disable uploads completely when onroad. Necessary to avoid high data usage when connected to Wi-Fi hotspot. "
         "Turn on this feature if you are looking to utilize map-based features, such as Speed Limit Control (SLC) and Map-based Turn Speed Control (MTSC)."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "IsMetric",
      tr("Use Metric System"),
      tr("Display speed in km/h instead of mph."),
      "../assets/offroad/icon_blank.png",
    },
#ifdef ENABLE_MAPS
    {
      "NavSettingTime24h",
      tr("Show ETA in 24h Format"),
      tr("Use 24h format instead of am/pm"),
      "../assets/offroad/icon_blank.png",
    },
    {
      "NavSettingLeftSide",
      tr("Show Map on Left Side of UI"),
      tr("Show map on left side when in split screen view."),
      "../assets/offroad/icon_blank.png",
    },
#endif
  };


  std::vector<QString> longi_button_texts{tr("Aggressive"), tr("Moderate"), tr("Standard"), tr("Relaxed")};
  long_personality_setting = new ButtonParamControlSP("LongitudinalPersonality", tr("Driving Personality"),
                                          tr("Standard is recommended. In moderate/aggressive mode, sunnypilot will follow lead cars closer and be more aggressive with the gas and brake. "
                                             "In relaxed mode sunnypilot will stay further away from lead cars. On supported cars, you can cycle through these personalities with "
                                             "your steering wheel distance button."),
                                          "",
                                          longi_button_texts,
                                          380);
  long_personality_setting->showDescription();

  // accel controller
  std::vector<QString> accel_personality_texts{tr("Sport"), tr("Normal"), tr("Eco"), tr("Stock")};
  accel_personality_setting = new ButtonParamControlSP("AccelPersonality", tr("Acceleration Personality"),
                                          tr("Normal is recommended. In sport mode, sunnypilot will provide aggressive acceleration for a dynamic driving experience. "
                                             "In eco mode, sunnypilot will apply smoother and more relaxed acceleration. On supported cars, you can cycle through these "
                                             "acceleration personality within Onroad Settings on the driving screen."),
                                          "",
                                          accel_personality_texts);
  accel_personality_setting->showDescription();

  // set up uiState update for personality setting
  QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &TogglesPanelSP::updateState);

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);

    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);

    addItem(toggle);
    toggles[param.toStdString()] = toggle;

    // insert longitudinal personality after NDOG toggle
    if (param == "DisengageOnAccelerator") {
      addItem(long_personality_setting);
      addItem(accel_personality_setting);
    }
  }

  // Toggles with confirmation dialogs
  //toggles["ExperimentalMode"]->setActiveIcon("../assets/img_experimental.svg");
  toggles["ExperimentalMode"]->setConfirmation(true, true);
  toggles["ExperimentalLongitudinalEnabled"]->setConfirmation(true, false);
  toggles["CustomStockLong"]->setConfirmation(true, false);

  connect(toggles["ExperimentalLongitudinalEnabled"], &ToggleControlSP::toggleFlipped, [=]() {
    updateToggles();
  });
  connect(toggles["CustomStockLong"], &ToggleControlSP::toggleFlipped, [=]() {
    updateToggles();
  });

  param_watcher = new ParamWatcher(this);

  QObject::connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    updateToggles();
  });
}

void TogglesPanelSP::updateState(const UIStateSP &s) {
  const SubMaster &sm = *(s.sm);

  if (sm.updated("controlsState")) {
    auto personality = sm["controlsState"].getControlsState().getPersonality();
    if (personality != s.scene.personality && s.scene.started && isVisible()) {
      long_personality_setting->setCheckedButton(static_cast<int>(personality));
    }
    uiStateSP()->scene.personality = personality;
  }

  if (sm.updated("controlsStateSP")) {
    auto accel_personality = sm["controlsStateSP"].getControlsStateSP().getAccelPersonality();
    if (accel_personality != s.scene.accel_personality && s.scene.started && isVisible()) {
      accel_personality_setting->setCheckedButton(static_cast<int>(accel_personality));
    }
    uiStateSP()->scene.accel_personality = accel_personality;
  }
}

void TogglesPanelSP::showEvent(QShowEvent *event) {
  updateToggles();
}

void TogglesPanelSP::updateToggles() {
  param_watcher->addParam("LongitudinalPersonality");

  if (!isVisible()) return;

  auto experimental_mode_toggle = toggles["ExperimentalMode"];
  auto op_long_toggle = toggles["ExperimentalLongitudinalEnabled"];
  auto custom_stock_long_toggle = toggles["CustomStockLong"];
  auto dec_toggle = toggles["DynamicExperimentalControl"];
  auto dynamic_personality_toggle = toggles["DynamicPersonality"];
  const QString e2e_description = QString("%1<br>"
                                          "<h4>%2</h4><br>"
                                          "%3<br>"
                                          "<h4>%4</h4><br>"
                                          "%5<br>")
                                  .arg(tr("openpilot defaults to driving in <b>chill mode</b>. Experimental mode enables <b>alpha-level features</b> that aren't ready for chill mode. Experimental features are listed below:"))
                                  .arg(tr("End-to-End Longitudinal Control"))
                                  .arg(tr("Let the driving model control the gas and brakes. sunnypilot will drive as it thinks a human would, including stopping for red lights and stop signs. "
                                          "Since the driving model decides the speed to drive, the set speed will only act as an upper bound. This is an alpha quality feature; "
                                          "mistakes should be expected."))
                                  .arg(tr("New Driving Visualization"))
                                  .arg(tr("The driving visualization will transition to the road-facing wide-angle camera at low speeds to better show some turns. The Experimental mode logo will also be shown in the top right corner."));

  const bool is_release = params.getBool("IsReleaseBranch");
  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    if (!CP.getExperimentalLongitudinalAvailable() || is_release) {
      params.remove("ExperimentalLongitudinalEnabled");
    }
    op_long_toggle->setVisible(CP.getExperimentalLongitudinalAvailable() && !is_release);

    if (!CP.getCustomStockLongAvailable()) {
      params.remove("CustomStockLong");
    }
    custom_stock_long_toggle->setVisible(CP.getCustomStockLongAvailable());

    if (hasLongitudinalControl(CP)) {
      // normal description and toggle
      experimental_mode_toggle->setEnabled(true);
      experimental_mode_toggle->setDescription(e2e_description);
      long_personality_setting->setEnabled(true);
      accel_personality_setting->setEnabled(true);
      op_long_toggle->setEnabled(true);
      custom_stock_long_toggle->setEnabled(false);
      params.remove("CustomStockLong");
      dec_toggle->setEnabled(true);
      dynamic_personality_toggle->setEnabled(true);
    } else if (custom_stock_long_toggle->isToggled()) {
      op_long_toggle->setEnabled(false);
      experimental_mode_toggle->setEnabled(false);
      long_personality_setting->setEnabled(false);
      accel_personality_setting->setEnabled(false);
      params.remove("ExperimentalLongitudinalEnabled");
      params.remove("ExperimentalMode");
    } else {
      // no long for now
      experimental_mode_toggle->setEnabled(false);
      long_personality_setting->setEnabled(false);
      accel_personality_setting->setEnabled(false);
      params.remove("ExperimentalMode");

      const QString unavailable = tr("Experimental mode is currently unavailable on this car since the car's stock ACC is used for longitudinal control.");

      QString long_desc = unavailable + " " + \
                          tr("openpilot longitudinal control may come in a future update.");
      if (CP.getExperimentalLongitudinalAvailable()) {
        if (is_release) {
          long_desc = unavailable + " " + tr("An alpha version of sunnypilot longitudinal control can be tested, along with Experimental mode, on non-release branches.");
        } else {
          long_desc = tr("Enable the sunnypilot longitudinal control (alpha) toggle to allow Experimental mode.");
        }
      }
      experimental_mode_toggle->setDescription("<b>" + long_desc + "</b><br><br>" + e2e_description);

      op_long_toggle->setEnabled(CP.getExperimentalLongitudinalAvailable() && !is_release);
      custom_stock_long_toggle->setEnabled(CP.getCustomStockLongAvailable());
      dec_toggle->setEnabled(false);
      dynamic_personality_toggle->setEnabled(false);
      params.remove("DynamicExperimentalControl");
      params.remove("DynamicPersonality");
    }

    experimental_mode_toggle->refresh();
    op_long_toggle->refresh();
    custom_stock_long_toggle->refresh();
    dec_toggle->refresh();
    dynamic_personality_toggle->refresh();
  } else {
    experimental_mode_toggle->setDescription(e2e_description);
    op_long_toggle->setVisible(false);
    custom_stock_long_toggle->setVisible(false);
    dec_toggle->setVisible(false);
    dynamic_personality_toggle->setVisible(false);
  }
}

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
  DevicePanelSP *device = new DevicePanelSP(this);
  QObject::connect(device, &DevicePanelSP::reviewTrainingGuide, this, &SettingsWindow::reviewTrainingGuide);
  QObject::connect(device, &DevicePanelSP::showDriverView, this, &SettingsWindow::showDriverView);

  TogglesPanelSP *toggles = new TogglesPanelSP(this);
  QObject::connect(this, &SettingsWindow::expandToggleDescription, toggles, &TogglesPanel::expandToggleDescription);

  QList<PanelInfo> panels = {
    PanelInfo("   " + tr("Device"), device, "../assets/navigation/icon_home.svg"),
    PanelInfo("   " + tr("Network"), new NetworkingSP(this), "../assets/offroad/icon_network.png"),
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

    ScrollViewSP *panel_frame = new ScrollViewSP(panel, this);
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
  ScrollViewSP *buttons_scrollview  = new ScrollViewSP(buttons_widget, this);
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
    QStackedWidget, ScrollViewSP {
      background-color: black;
      border-radius: 30px;
    }
  )");
}
