#include "selfdrive/ui/qt/offroad/sunnypilot/lane_change_settings.h"

LaneChangeSettings::LaneChangeSettings(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidget *list = new ListWidget(this, false);
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "BelowSpeedPause",
      tr("Pause Lateral Below Speed with Blinker"),
      tr("Enable this toggle to pause lateral actuation with blinker when traveling below the desired speed selected below."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "AutoLaneChangeBsmDelay",
      tr("Auto Lane Change: Delay with Blind Spot"),
      tr("Toggle to enable a delay timer for seamless lane changes when blind spot monitoring (BSM) detects a obstructing vehicle, ensuring safe maneuvering."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "RoadEdge",
      tr("Block Lane Change: Road Edge Detection"),
      tr("Enable this toggle to block lane change when road edge is detected on the stalk actuated side."),
      "../assets/offroad/icon_blank.png",
    }
  };

  // Controls: Auto Lane Change Timer
  auto_lane_change_timer = new AutoLaneChangeTimer();
  auto_lane_change_timer->setUpdateOtherToggles(true);
  auto_lane_change_timer->showDescription();
  connect(auto_lane_change_timer, &SPOptionControl::updateLabels, auto_lane_change_timer, &AutoLaneChangeTimer::refresh);
  connect(auto_lane_change_timer, &AutoLaneChangeTimer::updateOtherToggles, this, &LaneChangeSettings::updateToggles);
  list->addItem(auto_lane_change_timer);

  // Pause Lateral Below Speed w/ Blinker
  pause_lateral_speed = new PauseLateralSpeed();
  pause_lateral_speed->showDescription();
  connect(pause_lateral_speed, &SPOptionControl::updateLabels, pause_lateral_speed, &PauseLateralSpeed::refresh);

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControl(param, title, desc, icon, this);

    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "BelowSpeedPause") {
      list->addItem(pause_lateral_speed);
    }

    // trigger offroadTransition when going onroad/offroad
    connect(uiState(), &UIState::offroadTransition, toggle, &ParamControl::setEnabled);
  }

  connect(toggles["BelowSpeedPause"], &ToggleControl::toggleFlipped, [=](bool state) {
    pause_lateral_speed->setEnabled(state);
    pause_lateral_speed->setVisible(state);
  });
  pause_lateral_speed->setEnabled(toggles["BelowSpeedPause"]->isToggled());
  pause_lateral_speed->setVisible(toggles["BelowSpeedPause"]->isToggled());

  main_layout->addWidget(new ScrollView(list, this));
}

void LaneChangeSettings::showEvent(QShowEvent *event) {
  updateToggles();
}

void LaneChangeSettings::updateToggles() {
  if (!isVisible()) {
    return;
  }

  auto auto_lane_change_bsm_delay_toggle = toggles["AutoLaneChangeBsmDelay"];
  auto auto_lane_change_timer_param = QString::fromStdString(params.get("AutoLaneChangeTimer"));

  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    if (!CP.getEnableBsm()) {
      params.remove("AutoLaneChangeBsmDelay");
    }
    auto_lane_change_bsm_delay_toggle->setEnabled(CP.getEnableBsm() && auto_lane_change_timer_param != "0");

    auto_lane_change_bsm_delay_toggle->refresh();
  } else {
    auto_lane_change_bsm_delay_toggle->setEnabled(false);
  }
}

// Auto Lane Change Timer (ALCT)
AutoLaneChangeTimer::AutoLaneChangeTimer() : SPOptionControl (
  "AutoLaneChangeTimer",
  tr("Auto Lane Change Timer"),
  tr("Set a timer to delay the auto lane change operation when the blinker is used. No nudge on the steering wheel is required to auto lane change if a timer is set.\nPlease use caution when using this feature. Only use the blinker when traffic and road conditions permit."),
  "../assets/offroad/icon_blank.png",
  {0, 5}) {

  refresh();
}

void AutoLaneChangeTimer::refresh() {
  QString option = QString::fromStdString(params.get("AutoLaneChangeTimer"));
  QString second = tr("s");
  if (option == "0") {
    setLabel(tr("Nudge"));
  } else if (option == "1") {
    setLabel(tr("Nudgeless"));
  } else if (option == "2") {
    setLabel("0.5 " + second);
  } else if (option == "3") {
    setLabel("1 " + second);
  } else if (option == "4") {
    setLabel("1.5 " + second);
  } else {
    setLabel("2 " + second);
  }
}

PauseLateralSpeed::PauseLateralSpeed() : SPOptionControl (
  "PauseLateralSpeed",
  "",
  tr("Pause lateral actuation with blinker when traveling below the desired speed selected. Default is 20 MPH or 32 km/h."),
  "../assets/offroad/icon_blank.png",
  {0, 255},
  5) {

  refresh();
}

void PauseLateralSpeed::refresh() {
  QString option = QString:: fromStdString(params.get("PauseLateralSpeed"));
  bool is_metric = params.getBool("IsMetric");

  if (option == "0") {
    setLabel(tr("Default"));
  } else {
    setLabel(option + " " + (is_metric ? tr("km/h") : tr("mph")));
  }
}
