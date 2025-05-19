/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/mads_settings.h"

#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

MadsSettings::MadsSettings(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton *back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidget *list = new ListWidget(this, false);
  // Main cruise
  madsMainCruiseToggle = new ParamControl(
    "MadsMainCruiseAllowed",
    tr("Toggle with Main Cruise"),
    tr("Note: For vehicles without LFA/LKAS button, disabling this will prevent lateral control engagement."),
    "");
  list->addItem(madsMainCruiseToggle);

  // Unified Engagement Mode
  madsUnifiedEngagementModeToggle = new ParamControl(
    "MadsUnifiedEngagementMode",
    tr("Unified Engagement Mode (UEM)"),
    QString("%1<br>"
            "<h4>%2</h4>")
    .arg(tr("Engage lateral and longitudinal control with cruise control engagement."))
    .arg(tr("Note: Once lateral control is engaged via UEM, it will remain engaged until it is manually disabled via the MADS button or car shut off.")),
    "");
  list->addItem(madsUnifiedEngagementModeToggle);

  // Steering Mode On Brake
  madsSteeringMode = new ButtonParamControl("MadsSteeringMode", tr("Steering Mode on Brake Pedal"), "", "", madsSteeringModeTexts(), 500);
  QObject::connect(madsSteeringMode, &ButtonParamControl::buttonToggled, [=] {
    updateToggles(offroad);
  });
  list->addItem(madsSteeringMode);
  madsSteeringMode->showDescription();

  QObject::connect(uiState(), &UIState::offroadTransition, this, &MadsSettings::updateToggles);

  main_layout->addWidget(new ScrollViewSP(list, this));
}

void MadsSettings::showEvent(QShowEvent *event) {
  updateToggles(offroad);
}

void MadsSettings::updateToggles(bool _offroad) {
  auto mads_steering_mode_param = std::atoi(params.get("MadsSteeringMode").c_str());

  auto steering_mode = static_cast<MadsSteeringMode>(
    std::clamp(mads_steering_mode_param, static_cast<int>(MadsSteeringMode::REMAIN_ACTIVE), static_cast<int>(MadsSteeringMode::DISENGAGE))
  );

  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    if (CP.getBrand() == "rivian" || CP.getBrand() == "tesla") {
      params.put("MadsSteeringMode", std::to_string(static_cast<int>(MadsSteeringMode::DISENGAGE)));
      madsSteeringModeValues = convertMadsSteeringModeValues({MadsSteeringMode::DISENGAGE});
      madsSteeringMode->setDescription(madsSteeringModeDescriptionBuilder(STATUS_DISENGAGE_ONLY, madsSteeringModeDescription(steering_mode)));
    } else {
      madsSteeringMode->setDescription(madsSteeringModeDescription(steering_mode));
    }
  } else {
    madsSteeringMode->setDescription(madsSteeringModeDescriptionBuilder(STATUS_CHECK_COMPATIBILITY, madsSteeringModeDescription(steering_mode)));
  }

  madsSteeringMode->setEnableSelectedButtons(_offroad, madsSteeringModeValues);
  madsSteeringMode->showDescription();

  offroad = _offroad;
}
