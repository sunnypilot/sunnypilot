/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/dab_settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"
#include <map>
#include <string>
#include <tuple>
#include <vector>

DabSettings::DabSettings(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidgetSP *list = new ListWidgetSP(this, false);
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "DABPhantomGate",
      tr("Filter Phantom Brakes"),
      tr("!!INDEV Filter out phantom braking events."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DABCurvGate",
      tr("Slow for Curves"),
      tr("!!INDEV Slow down for curves."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DABLeadGate",
      tr("Enable Lead Gate"),
      tr("."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DABTTSGate",
      tr("Enable TTS Gate"),
      tr("."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "DABSlowLeadGate",
      tr("Slow Lead Gate"),
      tr("Disable boost when radar sees slow traffic far ahead."),
      "../assets/offroad/icon_blank.png",
    },
  };

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);
    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  main_layout->addWidget(new ScrollViewSP(list, this));
}

void DabSettings::showEvent(QShowEvent *event) {
  updateToggles();
}

void DabSettings::updateToggles() {
  if (!isVisible()) {
    return;
  }

  auto dab_mode_param = std::atoi(params.get("DynamicAcceleration").c_str());
  bool dab_enabled = dab_mode_param > 0;

  //auto dynamic_accel_toggle = toggles["DynamicAcceleration"];
  auto phantom_gate_toggle = toggles.count("DABPhantomGate") ? toggles["DABPhantomGate"] : nullptr;
  auto curv_gate_toggle = toggles.count("DABCurvGate") ? toggles["DABCurvGate"] : nullptr;

  auto lead_gate_toggle = toggles.count("DABLeadGate") ? toggles["DABLeadGate"] : nullptr;
  auto tts_gate_toggle = toggles.count("DABTTSGate") ? toggles["DABTTSGate"] : nullptr;
  auto slow_lead_gate_toggle = toggles.count("DABSlowLeadGate") ? toggles["DABSlowLeadGate"] : nullptr;

  if (phantom_gate_toggle) {
    phantom_gate_toggle->setEnabled(dab_enabled);
    phantom_gate_toggle->refresh();
  }

  if (curv_gate_toggle) {
    curv_gate_toggle->setEnabled(dab_enabled);
    curv_gate_toggle->refresh();
  }

  if (lead_gate_toggle) {
    lead_gate_toggle->setEnabled(dab_enabled);
    lead_gate_toggle->refresh();
  }

  if (tts_gate_toggle) {
    tts_gate_toggle->setEnabled(dab_enabled);
    tts_gate_toggle->refresh();
  }

  if (slow_lead_gate_toggle) {
    slow_lead_gate_toggle->setEnabled(dab_enabled);
    slow_lead_gate_toggle->refresh();
  }
}
