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
  madsMainCruiseToggle = new ParamControl("MadsMainCruiseAllowed", tr("Toggle with Main Cruise"), "", "");
  list->addItem(madsMainCruiseToggle);

  // Unified Engagement Mode
  madsUnifiedEngagementModeToggle = new ParamControl("MadsUnifiedEngagementMode", tr("Unified Engagement Mode (UEM)"), "", "");
  list->addItem(madsUnifiedEngagementModeToggle);

  // Steering Mode On Brake
  madsSteeringMode = new ButtonParamControl("MadsSteeringMode", tr("Steering Mode on Brake Pedal"), "", "", madsSteeringModeTexts(), 500);
  QObject::connect(madsSteeringMode, &ButtonParamControl::buttonClicked, [=] {
    updateToggles(offroad);
  });
  list->addItem(madsSteeringMode);

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
  auto cp_sp_bytes = params.get("CarParamsSPPersistent");
  if (!cp_bytes.empty() && !cp_sp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    AlignedBuffer aligned_buf_sp;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    capnp::FlatArrayMessageReader cmsg_sp(aligned_buf_sp.align(cp_sp_bytes.data(), cp_sp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();
    cereal::CarParamsSP::Reader CP_SP = cmsg_sp.getRoot<cereal::CarParamsSP>();

    if (madsLimitedSettings(CP, CP_SP)) {
      params.remove("MadsMainCruiseAllowed");
      params.putBool("MadsUnifiedEngagementMode", true);
      params.put("MadsSteeringMode", std::to_string(static_cast<int>(MadsSteeringMode::DISENGAGE)));

      madsMainCruiseToggle->setEnabled(false);
      madsMainCruiseToggle->setDescription(madsDescriptionBuilder(DEFAULT_TO_OFF, MADS_MAIN_CRUISE_BASE_DESC));
      madsMainCruiseToggle->showDescription();

      madsUnifiedEngagementModeToggle->setEnabled(false);
      madsUnifiedEngagementModeToggle->setDescription(madsDescriptionBuilder(DEFAULT_TO_ON, MADS_UNIFIED_ENGAGEMENT_MODE_BASE_DESC));
      madsUnifiedEngagementModeToggle->showDescription();

      madsSteeringModeValues = convertMadsSteeringModeValues({MadsSteeringMode::DISENGAGE});
      madsSteeringMode->setDescription(madsDescriptionBuilder(STATUS_DISENGAGE_ONLY, madsSteeringModeDescription(steering_mode)));
    } else {
      madsMainCruiseToggle->setEnabled(true);
      madsMainCruiseToggle->setDescription(MADS_MAIN_CRUISE_BASE_DESC);

      madsUnifiedEngagementModeToggle->setEnabled(true);
      madsUnifiedEngagementModeToggle->setDescription(MADS_UNIFIED_ENGAGEMENT_MODE_BASE_DESC);

      madsSteeringModeValues = convertMadsSteeringModeValues(getMadsSteeringModeValues());
      madsSteeringMode->setDescription(madsSteeringModeDescription(steering_mode));
    }
  } else {
    madsMainCruiseToggle->setEnabled(false);
    madsMainCruiseToggle->setDescription(madsDescriptionBuilder(STATUS_CHECK_COMPATIBILITY, MADS_MAIN_CRUISE_BASE_DESC));
    madsMainCruiseToggle->showDescription();

    madsUnifiedEngagementModeToggle->setEnabled(false);
    madsUnifiedEngagementModeToggle->setDescription(madsDescriptionBuilder(STATUS_CHECK_COMPATIBILITY, MADS_UNIFIED_ENGAGEMENT_MODE_BASE_DESC));
    madsUnifiedEngagementModeToggle->showDescription();

    madsSteeringModeValues = {};
    madsSteeringMode->setDescription(madsDescriptionBuilder(STATUS_CHECK_COMPATIBILITY, madsSteeringModeDescription(steering_mode)));
  }

  madsSteeringMode->setEnableSelectedButtons(_offroad, madsSteeringModeValues);
  madsSteeringMode->showDescription();

  offroad = _offroad;
}
