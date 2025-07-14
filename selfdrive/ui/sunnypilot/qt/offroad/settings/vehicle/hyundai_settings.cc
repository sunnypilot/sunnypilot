/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/hyundai_settings.h"


HyundaiSettings::HyundaiSettings(QWidget *parent) : BrandSettingsInterface(parent) {
  QWidget *stackedWidget = new QWidget();
  main_layout = new QStackedLayout(stackedWidget);
  settingsScreen = new QWidget();
  QVBoxLayout *settingsLayout = new QVBoxLayout(settingsScreen);
  settingsLayout->setContentsMargins(0, 0, 0, 0);
  settingsLayout->addWidget(list);

  longitudinalTuningToggle = new ButtonParamControlSP("HyundaiLongitudinalTuning", tr("Longitudinal Tuning"), "", "", {tr("Off"), tr("Dynamic"), tr("Predictive")}, 500);
  connect(longitudinalTuningToggle, &ButtonParamControlSP::buttonClicked, this, &HyundaiSettings::updateSettings);
  list->addItem(longitudinalTuningToggle);
  longitudinalTuningToggle->showDescription();

  customTuningToggle = new ParamControlSP("LongTuningCustomToggle", tr("Custom Tuning Override"), customTuningToggleDescription(), "");
  connect(customTuningToggle, &ParamControlSP::toggleFlipped, this, [this](bool state) {
    if (state && !ConfirmationDialog::alert(customTuningWarningMsg(), this)) {
      customTuningToggle->refresh();
      return;
    }
    updateSettings();
  });
  list->addItem(customTuningToggle);
  customTuningToggle->showDescription();

  customTuningButtonWidget = new QWidget();
  QHBoxLayout *buttonLayout = new QHBoxLayout(customTuningButtonWidget);
  buttonLayout->setContentsMargins(0, 0, 0, 0);
  PushButtonSP *customTuningBtn = new PushButtonSP(tr("Customize Tune"));
  connect(customTuningBtn, &PushButtonSP::clicked, this, [this]() {
    if (!liveTuningWidget) {
      liveTuningWidget = new HyundaiLiveTuning(this);
      connect(liveTuningWidget, &HyundaiLiveTuning::backPress, this, [this]() {
        main_layout->setCurrentWidget(settingsScreen);
        emit liveTuningClosed();
      });
      main_layout->addWidget(liveTuningWidget);
    }
    main_layout->setCurrentWidget(liveTuningWidget);
    emit liveTuningOpened();
  });
  buttonLayout->addWidget(customTuningBtn, 0, Qt::AlignLeft);
  buttonLayout->addStretch();
  list->addItem(customTuningButtonWidget);
  customTuningButtonWidget->setVisible(false);

  main_layout->addWidget(settingsScreen);
  main_layout->setCurrentWidget(settingsScreen);
  layout()->addWidget(stackedWidget);
}

void HyundaiSettings::updateSettings() {
  auto longitudinal_tuning_param = std::atoi(params.get("HyundaiLongitudinalTuning").c_str());
  bool custom_tuning_enabled = params.getBool("LongTuningCustomToggle");
  uint32_t sp_flags = 0;

  auto cp_bytes = params.get("CarParamsPersistent");
  auto cp_sp_bytes = params.get("CarParamsSPPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    has_longitudinal_control = hasLongitudinalControl(CP);
  } else {
    has_longitudinal_control = false;
  }

  if (!cp_sp_bytes.empty()) {
    AlignedBuffer aligned_buf_sp;
    capnp::FlatArrayMessageReader cmsg_sp(aligned_buf_sp.align(cp_sp_bytes.data(), cp_sp_bytes.size()));
    cereal::CarParamsSP::Reader CP_SP = cmsg_sp.getRoot<cereal::CarParamsSP>();

    sp_flags = CP_SP.getFlags();
  }

  LongitudinalTuningOption longitudinal_tuning_option = (longitudinal_tuning_param == 2) ? LongitudinalTuningOption::PREDICTIVE :
                                                        (longitudinal_tuning_param == 1) ? LongitudinalTuningOption::DYNAMIC :
                                                        LongitudinalTuningOption::OFF;

  bool longitudinal_tuning_disabled = !has_longitudinal_control;
  QString longitudinal_tuning_description = longitudinalTuningDescription(longitudinal_tuning_option);
  if (longitudinal_tuning_disabled) {
    longitudinal_tuning_description = toggleDisableMsg(offroad, has_longitudinal_control);
  }
  longitudinalTuningToggle->setDescription(longitudinal_tuning_description);
  longitudinalTuningToggle->showDescription();

  bool tuning_available = !longitudinal_tuning_disabled && longitudinal_tuning_option != LongitudinalTuningOption::OFF;
  customTuningToggle->setEnabled(tuning_available);

  if (customTuningButtonWidget) {
    customTuningButtonWidget->setVisible(custom_tuning_enabled && tuning_available);
  }

  if (custom_tuning_enabled && tuning_available) {
    customTuningToggle->hideDescription();
  } else {
    QString desc = tuning_available ? customTuningToggleDescription() :
                   longitudinal_tuning_disabled ? toggleDisableMsg(offroad, has_longitudinal_control) :
                   customTuningDisabledMsg();
    customTuningToggle->setDescription(desc);
    customTuningToggle->showDescription();
  }

  if (!offroad) {
    if (sp_flags & (16 | 32)) {  // HyundaiFlagsSP.LONG_TUNING_DYNAMIC | HyundaiFlagsSP.LONG_TUNING_PREDICTIVE
      longitudinalTuningToggle->setEnableSelectedButtons(!longitudinal_tuning_disabled, {1, 2});
    } else {
      longitudinalTuningToggle->setEnableSelectedButtons(!longitudinal_tuning_disabled);
    }
  } else {
    longitudinalTuningToggle->setEnabled(!longitudinal_tuning_disabled);
  }
}
