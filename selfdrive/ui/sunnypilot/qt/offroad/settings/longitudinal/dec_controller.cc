/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/dec_controller.h"

DecControllerSubpanel::DecControllerSubpanel(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(0, 0, 0, 0);

  ListWidgetSP *list = new ListWidgetSP(this, false);
  ScrollViewSP *scroll = new ScrollViewSP(list, this);
  main_layout->addWidget(scroll);

  PanelBackButton *back_btn = new PanelBackButton();
  back_btn->setStyleSheet(R"(
    QPushButton#back_btn {
      border: 4px solid #393939 !important;
      border-radius: 30px;
      font-size: 50px;
      margin: 0px;
      padding: 10px;
      color: #dddddd;
      background-color: #393939;
    }
    QPushButton#back_btn:pressed {
      background-color: #4a4a4a;
    }
  )");
  connect(back_btn, &QPushButton::clicked, this, &DecControllerSubpanel::backPress);
  list->addItem(back_btn);

  // Reset to Defaults
  QPushButton *reset_btn = new QPushButton(tr("Reset to Defaults"));
  reset_btn->setStyleSheet(R"(
    QPushButton {
      border-radius: 20px;
      font-size: 45px;
      font-weight: 500;
      height: 120px;
      margin: 20px 40px 20px 40px;
      color: #FFFFFF;
      background-color: #393939;
    }
    QPushButton:pressed {
      background-color: #4a4a4a;
    }
  )");
  list->addItem(reset_btn);

  connect(reset_btn, &QPushButton::clicked, [=]() {
    params.put("DynamicExperimentalStandstill", "1");
    params.put("DynamicExperimentalModelSlowDown", "1");
    params.put("DynamicExperimentalFCW", "1");
    params.put("DynamicExperimentalHasLead", "0");
    params.put("DynamicExperimentalSlowerLead", "0");
    params.put("DynamicExperimentalStoppedLead", "0");
    params.put("DynamicExperimentalDistanceBased", "0");
    params.put("DynamicExperimentalDistanceValue", "30");
    params.put("DynamicExperimentalSpeedBased", "0");
    params.put("DynamicExperimentalSpeedValue", "25");
    params.put("DynamicExperimentalSlowness", "0");
    params.put("DynamicExperimentalFollowLead", "0");

    std::vector<ParamControlSP*> toggles = {standstillControl, modelSlowDownControl, followLeadControl, fcwControl, hasLeadControl, slowerLeadControl, stoppedLeadControl, distanceBasedControl, speedBasedControl, slownessControl};
    for (auto toggle : toggles) {
      if (toggle) toggle->refresh();
    }
    emit distanceValueControl->updateLabels();
    emit speedValueControl->updateLabels();
    updateToggles();
  });

  auto add_toggle = [&](ParamControlSP *&ptr, const char *param, const QString &title, const QString &desc, const char *default_val) {
    ptr = new ParamControlSP(param, title, desc, "../assets/offroad/icon_blank.png");
    list->addItem(ptr);
  };

  auto create_indented_container = [&](QWidget *widget) {
    QWidget *container = new QWidget();
    QHBoxLayout *layout = new QHBoxLayout(container);
    layout->setContentsMargins(40, 0, 0, 0);
    layout->setAlignment(Qt::AlignLeft);
    layout->addWidget(widget, 0, Qt::AlignLeft);
    list->addItem(container);
    return container;
  };

  auto add_value_control = [&](OptionControlSP *&ptr, const char *param, const QString &title, const QString &desc, int min, int max, int step, const char *unit, ParamControlSP *toggle, const char *parent_param, const char *default_val) {
    ptr = new OptionControlSP(param, title, desc, "../assets/offroad/icon_blank.png", {min, max}, step, false, nullptr);
    QWidget *container = create_indented_container(ptr);

    connect(ptr, &OptionControlSP::updateLabels, [=]() {
      auto param_value = params.get(param);
      ptr->setLabel(QString::fromStdString(param_value) + " " + unit);
    });
    auto initial = params.get(param);
    ptr->setLabel(QString::fromStdString(initial) + " " + unit);

    connect(toggle, &ParamControlSP::toggleFlipped, [=](bool enabled) {
      container->setVisible(enabled);
    });
    container->setVisible(params.getBool(parent_param));
  };

  add_toggle(fcwControl, "DynamicExperimentalFCW", tr("FCW Detection"), tr("Use blended mode when FCW is detected in the road ahead."), "1");
  add_toggle(standstillControl, "DynamicExperimentalStandstill", tr("Enable at Standstill"), tr("Use blended mode when the vehicle is at a standstill."), "1");
  add_toggle(followLeadControl, "DynamicExperimentalFollowLead", tr("Follow Lead Vehicle"), tr(""), "0");
  add_toggle(modelSlowDownControl, "DynamicExperimentalModelSlowDown", tr("Model Slow Down Detection"), tr(""), "1");
  add_toggle(slownessControl, "DynamicExperimentalSlowness", tr("Below Cruise Speed Detection"), tr(""), "0");
  add_toggle(hasLeadControl, "DynamicExperimentalHasLead", tr("Lead Vehicle Detection"), tr("Use blended mode when a lead vehicle is detected and significantly slowing."), "0");

  auto add_child_button = [&](ParamControlSP *&ptr, const char *param, const QString &title) {
    ptr = new ParamControlSP(param, title, tr(""), "../assets/offroad/icon_blank.png");
    QWidget *container = create_indented_container(ptr);

    connect(hasLeadControl, &ParamControlSP::toggleFlipped, [=](bool enabled) {
      container->setVisible(enabled);
    });
    container->setVisible(params.getBool("DynamicExperimentalHasLead"));
  };

  add_child_button(slowerLeadControl, "DynamicExperimentalSlowerLead", tr("Significantly Slower Lead Detection"));
  add_child_button(stoppedLeadControl, "DynamicExperimentalStoppedLead", tr("Stopped Lead Detection"));

  // Distance-based DEC
  add_toggle(distanceBasedControl, "DynamicExperimentalDistanceBased", tr("Distance-Based Switching"), tr("Use blended mode when the distance to the lead vehicle is below the specified threshold."), "0");
  add_value_control(distanceValueControl, "DynamicExperimentalDistanceValue", tr("Distance Threshold"), tr("Distance from lead vehicle in meters below which blended mode will be used."), 10, 100, 5, "m", distanceBasedControl, "DynamicExperimentalDistanceBased", "30.0");

  // Speed-based DEC
  add_toggle(speedBasedControl, "DynamicExperimentalSpeedBased", tr("Speed-Based Switching"), tr("Use blended mode when the vehicle speed is below the specified threshold."), "0");
  add_value_control(speedValueControl, "DynamicExperimentalSpeedValue", tr("Speed Threshold"), tr("Speed in km/h below which blended mode will be used."), 0, 80, 5, "km/h", speedBasedControl, "DynamicExperimentalSpeedBased", "26.0");

  connect(distanceBasedControl, &ParamControlSP::toggleFlipped, this, &DecControllerSubpanel::updateToggles);
  connect(speedBasedControl, &ParamControlSP::toggleFlipped, this, &DecControllerSubpanel::updateToggles);
  connect(modelSlowDownControl, &ParamControlSP::toggleFlipped, this, &DecControllerSubpanel::updateToggles);
  connect(slownessControl, &ParamControlSP::toggleFlipped, this, &DecControllerSubpanel::updateToggles);
  connect(followLeadControl, &ParamControlSP::toggleFlipped, this, &DecControllerSubpanel::updateToggles);
  connect(hasLeadControl, &ParamControlSP::toggleFlipped, this, &DecControllerSubpanel::updateToggles);

  updateToggles();
  showAllDescriptions();
}

void DecControllerSubpanel::showAllDescriptions() {
  standstillControl->showDescription();
  modelSlowDownControl->showDescription();
  slownessControl->showDescription();
  followLeadControl->showDescription();
  fcwControl->showDescription();
  hasLeadControl->showDescription();
  distanceBasedControl->showDescription();
  speedBasedControl->showDescription();
  distanceValueControl->showDescription();
  speedValueControl->showDescription();
}

void DecControllerSubpanel::updateToggles() {
  bool distanceBasedEnabled = params.getBool("DynamicExperimentalDistanceBased");
  bool speedBasedEnabled = params.getBool("DynamicExperimentalSpeedBased");
  bool modelSlowDownEnabled = params.getBool("DynamicExperimentalModelSlowDown");
  bool slownessEnabled = params.getBool("DynamicExperimentalSlowness");
  bool followLeadEnabled = params.getBool("DynamicExperimentalFollowLead");
  bool hasLeadEnabled = params.getBool("DynamicExperimentalHasLead");
  bool followLeadActive = followLeadEnabled && modelSlowDownEnabled && slownessEnabled;
  bool allowFollowLead = modelSlowDownEnabled && slownessEnabled;

  followLeadControl->setEnabled(modelSlowDownEnabled && slownessEnabled);
  modelSlowDownControl->setEnabled(!followLeadActive);
  slownessControl->setEnabled(!followLeadActive);

  slowerLeadControl->setVisible(hasLeadEnabled);
  stoppedLeadControl->setVisible(hasLeadEnabled);

  // Set descriptions based on state
  if (followLeadActive) {
    followLeadControl->setDescription(tr("Currently active. Prefers ACC with weighted confidence when following a lead vehicle for normal scenarios. If the model wants to slowdown significantly, it will still trigger blended mode."));
    modelSlowDownControl->setDescription(tr("Disabled when Follow Lead Vehicle is active. Follow Lead mode overrides this when a lead vehicle is present (except during imminent slowdown scenarios)."));
    slownessControl->setDescription(tr("Disabled when Follow Lead Vehicle is active. Follow Lead mode overrides this when a lead vehicle is present."));
  } else if (allowFollowLead) {
    followLeadControl->setDescription(tr("When enabled, prefers ACC mode when following a lead vehicle for normal scenarios. Model wants to stop now situations still trigger blended mode."));
  } else {
    followLeadControl->setDescription(tr("Model slow down detection and below cruise speed detection must be enabled to use this mode."));
  }
  // Set default descriptions for model controls when not overridden
  if (!followLeadActive) {
    modelSlowDownControl->setDescription(tr("Use blended mode when the model detects a slow down scenario ahead."));
    slownessControl->setDescription(tr("Use blended mode when driving significantly slower than the set cruise speed."));
  }
  // Set visibility of option controls based on their parent
  distanceValueControl->setVisible(distanceBasedEnabled);
  speedValueControl->setVisible(speedBasedEnabled);
}

void DecControllerSubpanel::showEvent(QShowEvent *event) {
  QWidget::showEvent(event);
  updateToggles();
  showAllDescriptions();
}
