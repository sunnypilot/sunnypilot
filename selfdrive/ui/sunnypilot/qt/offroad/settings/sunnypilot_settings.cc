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

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnypilot_settings.h"

#include <tuple>
#include <vector>

#include "common/model.h"

SunnypilotPanel::SunnypilotPanel(QWidget *parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);

  ListWidgetSP *list = new ListWidgetSP(this, false);
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "EnableMads",
      tr("Enable M.A.D.S."),
      tr("Enable the beloved M.A.D.S. feature. Disable toggle to revert back to stock openpilot engagement/disengagement."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "VisionCurveLaneless",
      tr("Laneless for Curves in \"Auto\" Mode"),
      tr("While in Auto Lane, switch to Laneless for current/future curves."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "EnableSlc",
      tr("Speed Limit Control (SLC)"),
      tr("When you engage ACC, you will be prompted to set the cruising speed to the speed limit of the road adjusted by the Offset and Source Policy specified, or the current driving speed. "
         "The maximum cruising speed will always be the MAX set speed."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "TurnVisionControl",
      tr("Enable Vision-based Turn Speed Control (V-TSC)"),
      tr("Use vision path predictions to estimate the appropriate speed to drive through turns ahead."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "TurnSpeedControl",
      tr("Enable Map Data Turn Speed Control (M-TSC) (Beta)"),
      tr("Use curvature information from map data to define speed limits to take turns ahead."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "ReverseAccChange",
      tr("ACC +/-: Long Press Reverse"),
      QString("%1<br>"
              "<h4>%2</h4><br>"
              "<h4>%3</h4><br>")
      .arg(tr("Change the ACC +/- buttons behavior with cruise speed change in sunnypilot."))
      .arg(tr("Disabled (Stock): Short=1, Long = 5 (imperial) / 10 (metric)"))
      .arg(tr("Enabled: Short = 5 (imperial) / 10 (metric), Long=1")),
      "../assets/offroad/icon_blank.png",
    },
    {
      "CustomOffsets",
      tr("Custom Offsets"),
      "",
      "../assets/offroad/icon_blank.png",
    },
    {
      "NNFF",
      tr("Neural Network Lateral Control (NNLC)"),
      "",
      "../assets/offroad/icon_blank.png",
    },
    {
      "EnforceTorqueLateral",
      tr("Enforce Torque Lateral Control"),
      tr("Enable this to enforce sunnypilot to steer with Torque lateral control."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "TorqueLateralJerk",
      tr("Lateral Jerk with Torque Lateral Control (Alpha)"),
      tr("Utilizes limited lateral jerk control for improved steering response, leveraging stock torque lateral controller capabilities. Designed to mimic NNLC behavior without training models or data collection."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "LiveTorque",
      tr("Enable Self-Tune"),
      tr("Enables self-tune for Torque lateral control for platforms that do not use Torque lateral control by default."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "LiveTorqueRelaxed",
      tr("Less Restrict Settings for Self-Tune (Beta)"),
      tr("Less strict settings when using Self-Tune. This allows torqued to be more forgiving when learning values."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "CustomTorqueLateral",
      tr("Enable Custom Tuning"),
      tr("Enables custom tuning for Torque lateral control. Modifying FRICTION and LAT_ACCEL_FACTOR below will override the offline values indicated in the YAML files within \"selfdrive/torque_data\". "
         "The values will also be used live when \"Override Self-Tune\" toggle is enabled."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "TorquedOverride",
      tr("Manual Real-Time Tuning"),
      tr("Enforces the torque lateral controller to use the fixed values instead of the learned values from Self-Tune. Enabling this toggle overrides Self-Tune values."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "QuietDrive",
      tr("Quiet Drive 🤫"),
      tr("sunnypilot will display alerts but only play the most important warning sounds. This feature can be toggled while the car is on."),
      "../assets/offroad/icon_blank.png",
    },
    {
      "EndToEndLongAlertLight",
      tr("Green Traffic Light Chime (Beta)"),
      QString("%1<br>"
              "<h4>%2</h4><br>")
              .arg(tr("A chime will play when the traffic light you are waiting for turns green and you have no vehicle in front of you. "
                      "If you are waiting behind another vehicle, the chime will play once the vehicle advances unless ACC is engaged."))
              .arg(tr("Note: This chime is only designed as a notification. It is the driver's responsibility to observe their environment and make decisions accordingly.")),
      "../assets/offroad/icon_blank.png",
    },
    {
      "EndToEndLongAlertLead",
      tr("Lead Vehicle Departure Alert"),
      QString("%1<br>"
              "<h4>%2</h4><br>")
              .arg(tr("Enable this will notify when the leading vehicle drives away."))
              .arg(tr("Note: This chime is only designed as a notification. It is the driver's responsibility to observe their environment and make decisions accordingly.")),
      "../assets/offroad/icon_blank.png",
    }
  };

  // M.A.D.S. Settings
  SubPanelButton *madsSettings = new SubPanelButton(tr("Customize M.A.D.S."));
  madsSettings->setObjectName("mads_btn");
  // Set margin on the outside of the button
  QVBoxLayout* madsSettingsLayout = new QVBoxLayout;
  madsSettingsLayout->setContentsMargins(0, 0, 0, 30);
  madsSettingsLayout->addWidget(madsSettings);
  connect(madsSettings, &QPushButton::clicked, [=]() {
    scrollView->setLastScrollPosition();
    main_layout->setCurrentWidget(mads_settings);
  });

  mads_settings = new MadsSettings(this);
  connect(mads_settings, &MadsSettings::backPress, [=]() {
    scrollView->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);
  });

  // Lane Change Settings
  SubPanelButton *laneChangeSettings = new SubPanelButton(tr("Customize Lane Change"));
  laneChangeSettings->setObjectName("lane_change_btn");
  // Set margin on the outside of the button
  QVBoxLayout* laneChangeSettingsLayout = new QVBoxLayout;
  laneChangeSettingsLayout->setContentsMargins(0, 0, 0, 30);
  laneChangeSettingsLayout->addWidget(laneChangeSettings);
  connect(laneChangeSettings, &QPushButton::clicked, [=]() {
    scrollView->setLastScrollPosition();
    main_layout->setCurrentWidget(lane_change_settings);
  });

  lane_change_settings = new LaneChangeSettings(this);
  connect(lane_change_settings, &LaneChangeSettings::backPress, [=]() {
    scrollView->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);
  });

  // Custom Offsets Settings
  SubPanelButton *customOffsetsSettings = new SubPanelButton(tr("Customize Offsets"));
  customOffsetsSettings->setObjectName("custom_offsets_btn");
  // Set margin on the outside of the button
  QVBoxLayout* customOffsetsSettingsLayout = new QVBoxLayout;
  customOffsetsSettingsLayout->setContentsMargins(0, 0, 0, 30);
  customOffsetsSettingsLayout->addWidget(customOffsetsSettings);
  connect(customOffsetsSettings, &QPushButton::clicked, [=]() {
    scrollView->setLastScrollPosition();
    main_layout->setCurrentWidget(custom_offsets_settings);
  });

  custom_offsets_settings = new CustomOffsetsSettings(this);
  connect(custom_offsets_settings, &CustomOffsetsSettings::backPress, [=]() {
    scrollView->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);
  });

  // SLC. Settings
  slcSettings = new SubPanelButton(tr("Customize Speed Limit Control"), 980, this);
  slcSettings->setObjectName("slc_btn");
  // Set margin on the outside of the button
  QVBoxLayout* slcSettingsLayout = new QVBoxLayout;
  slcSettingsLayout->setContentsMargins(0, 0, 0, 30);
  slcSettingsLayout->addWidget(slcSettings);
  connect(slcSettings, &QPushButton::clicked, [=]() {
    scrollView->setLastScrollPosition();
    main_layout->setCurrentWidget(slc_settings);
  });

  slc_settings = new SlcSettings(this);
  connect(slc_settings, &SlcSettings::backPress, [=]() {
    scrollView->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);
  });

  // Speed Limit Warning Settings
  slwSettings = new SubPanelButton(tr("Customize Warning"), 720, this);
  slwSettings->setObjectName("slw_btn");
  connect(slwSettings, &QPushButton::clicked, [=]() {
    scrollView->setLastScrollPosition();
    main_layout->setCurrentWidget(slw_settings);
  });

  slw_settings = new SpeedLimitWarningSettings(this);
  connect(slw_settings, &SpeedLimitWarningSettings::backPress, [=]() {
    scrollView->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);
  });

  // Speed Limit Warning Settings
  slpSettings = new SubPanelButton(tr("Customize Source"), 720, this);
  slpSettings->setObjectName("slp_btn");
  connect(slpSettings, &QPushButton::clicked, [=]() {
    scrollView->setLastScrollPosition();
    main_layout->setCurrentWidget(slp_settings);
  });

  slp_settings = new SpeedLimitPolicySettings(this);
  connect(slp_settings, &SpeedLimitPolicySettings::backPress, [=]() {
    scrollView->restoreScrollPosition();
    main_layout->setCurrentWidget(sunnypilotScreen);
  });

  // Speed Limit Warning and Speed Limit Policy in the same horizontal space
  QHBoxLayout *warning_policy_layout = new QHBoxLayout;
  warning_policy_layout->setContentsMargins(0, 0, 0, 30);
  warning_policy_layout->addWidget(slwSettings);
  warning_policy_layout->addSpacing(10);
  warning_policy_layout->addWidget(slpSettings);
  warning_policy_layout->setAlignment(Qt::AlignLeft);

  // toggle names to trigger updateToggles() when toggleFlipped
  std::vector<std::string> updateTogglesNames{
    "EnforceTorqueLateral", "CustomTorqueLateral", "LiveTorque", "TorquedOverride", "NNFF"
  };

  // toggle for offroadTransition when going onroad/offroad
  std::vector<std::string> toggleOffroad{
    "EnableMads", "EnforceTorqueLateral", "CustomTorqueLateral", "LiveTorqueRelaxed", "NNFF"
  };

  // Controls: Torque - FRICTION
  friction = new TorqueFriction();
  connect(friction, &OptionControlSP::updateLabels, friction, &TorqueFriction::refresh);

  // Controls: Torque - LAT_ACCEL_FACTOR
  lat_accel_factor = new TorqueMaxLatAccel();
  connect(lat_accel_factor, &OptionControlSP::updateLabels, lat_accel_factor, &TorqueMaxLatAccel::refresh);

  std::vector<QString> dlp_settings_texts{tr("Laneful"), tr("Laneless"), tr("Auto")};
  dlp_settings = new ButtonParamControlSP(
    "DynamicLaneProfile", tr("Dynamic Lane Profile"), "",
    "",
    dlp_settings_texts,
    340);
  dlp_settings->showDescription();

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);

    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;

    if (param == "EnableMads") {
      list->addItem(madsSettingsLayout);

      list->addItem(horizontal_line());

      // Controls: Dynamic Lane Profile group
      list->addItem(dlp_settings);
    }

    if (param == "VisionCurveLaneless") {
      list->addItem(laneChangeSettingsLayout);
      list->addItem(horizontal_line());

      list->addItem(new LabelControlSP(tr("Speed Limit Assist")));
    }

    if (param == "EnableSlc") {
      list->addItem(slcSettingsLayout);

      list->addItem(warning_policy_layout);
      list->addItem(horizontal_line());
    }

    if (param == "ReverseAccChange") {
      list->addItem(horizontal_line());
    }

    if (param == "CustomOffsets") {
      list->addItem(customOffsetsSettingsLayout);
      list->addItem(horizontal_line());
    }

    if (param == "TorquedOverride") {
      // Control: FRICTION
      list->addItem(friction);

      // Controls: LAT_ACCEL_FACTOR
      list->addItem(lat_accel_factor);

      list->addItem(horizontal_line());
    }
  }

  connect(toggles["NNFF"], &ToggleControlSP::toggleFlipped, [=](bool state) {
    if (state) {
      toggles["EnforceTorqueLateral"]->setEnabled(false);
      params.putBool("EnforceTorqueLateral", false);
      toggles["EnforceTorqueLateral"]->refresh();
    } else {
      toggles["NNFF"]->hideDescription();

      toggles["EnforceTorqueLateral"]->setEnabled(true);
      toggles["EnforceTorqueLateral"]->refresh();
    }
  });

  connect(toggles["EnforceTorqueLateral"], &ToggleControlSP::toggleFlipped, [=](bool state) {
    if (state) {
      toggles["NNFF"]->setEnabled(false);
      params.putBool("NNFF", false);
      toggles["NNFF"]->refresh();
    } else {
      toggles["NNFF"]->setEnabled(true);
      toggles["NNFF"]->refresh();
    }
  });

  // trigger updateToggles() when toggleFlipped
  for (const auto& updateToggleName : updateTogglesNames) {
    if (toggles.find(updateToggleName) != toggles.end()) {
      connect(toggles[updateToggleName], &ToggleControlSP::toggleFlipped, [=](bool state) {
        updateToggles();
      });
    }
  }

  // trigger offroadTransition when going onroad/offroad
  for (const auto& offroadName : toggleOffroad) {
    if (toggles.find(offroadName) != toggles.end()) {
      connect(uiStateSP(), &UIStateSP::offroadTransition, [=](bool offroad) {
        toggles[offroadName]->setEnabled(offroad);
      });
    }
  }

  toggles["EnableMads"]->setConfirmation(true, false);
  toggles["EndToEndLongAlertLight"]->setConfirmation(true, false);
  toggles["CustomOffsets"]->showDescription();

  connect(toggles["EnableMads"], &ToggleControlSP::toggleFlipped, mads_settings, &MadsSettings::updateToggles);
  connect(toggles["EnableMads"], &ToggleControlSP::toggleFlipped, [=](bool state) {
    madsSettings->setEnabled(state);
  });
  madsSettings->setEnabled(toggles["EnableMads"]->isToggled());

  connect(toggles["EnableSlc"], &ToggleControlSP::toggleFlipped, slc_settings, &SlcSettings::updateToggles);
  connect(toggles["EnableSlc"], &ToggleControlSP::toggleFlipped, [=](bool state) {
    slcSettings->setEnabled(state);
    slcSettings->setVisible(state);
  });
  slcSettings->setEnabled(toggles["EnableSlc"]->isToggled());
  slcSettings->setVisible(toggles["EnableSlc"]->isToggled());

  connect(toggles["CustomOffsets"], &ToggleControlSP::toggleFlipped, [=](bool state) {
    customOffsetsSettings->setEnabled(state);
  });
  customOffsetsSettings->setEnabled(toggles["CustomOffsets"]->isToggled());

  // update "FRICTION" and "LAT_ACCEL_FACTOR" titles when going onroad/offroad
  connect(uiStateSP(), &UIStateSP::offroadTransition, [=](bool offroad) {
    friction->setEnabled(offroad || toggles["TorquedOverride"]->isToggled());
    lat_accel_factor->setEnabled(offroad || toggles["TorquedOverride"]->isToggled());

    friction->refresh();
    lat_accel_factor->refresh();
  });

  // update "FRICTION" and "LAT_ACCEL_FACTOR" titles when TorquedOverride is flipped
  connect(toggles["TorquedOverride"], &ToggleControlSP::toggleFlipped, [=](bool state) {
    friction->setEnabled(params.getBool("IsOffroad") || state);
    lat_accel_factor->setEnabled(params.getBool("IsOffroad") || state);

    friction->setTitle("FRICTION - " + (state ? tr("Real-time and Offline") : tr("Offline Only")));
    lat_accel_factor->setTitle("LAT_ACCEL_FACTOR - " + (state ? ("Real-time and Offline") : tr("Offline Only")));

    friction->refresh();
    lat_accel_factor->refresh();
  });

  param_watcher = new ParamWatcher(this);

  QObject::connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    updateToggles();
  });

  sunnypilotScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(sunnypilotScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  scrollView = new ScrollViewSP(list, this);
  vlayout->addWidget(scrollView, 1);
  main_layout->addWidget(sunnypilotScreen);
  main_layout->addWidget(mads_settings);
  main_layout->addWidget(lane_change_settings);
  main_layout->addWidget(custom_offsets_settings);
  main_layout->addWidget(slc_settings);
  main_layout->addWidget(slw_settings);
  main_layout->addWidget(slp_settings);

  setStyleSheet(R"(
    #back_btn {
      font-size: 50px;
      margin: 0px;
      padding: 15px;
      border-width: 0;
      border-radius: 30px;
      color: #dddddd;
      background-color: #393939;
    }
    #back_btn:pressed {
      background-color:  #4a4a4a;
    }
  )");

  main_layout->setCurrentWidget(sunnypilotScreen);
}

void SunnypilotPanel::showEvent(QShowEvent *event) {
  updateToggles();
}

void SunnypilotPanel::hideEvent(QHideEvent *event) {
  main_layout->setCurrentWidget(sunnypilotScreen);
}

void SunnypilotPanel::updateToggles() {
  param_watcher->addParam("DynamicLaneProfile");
  param_watcher->addParam("IsOffroad");
  param_watcher->addParam("EnableSlc");

  if (!isVisible()) {
    return;
  }

  // TODO: SP: use upstream's setCheckedButton
  dlp_settings->setButton("DynamicLaneProfile");

  // toggle VisionCurveLaneless when DynamicLaneProfile == 2/Auto
  auto dynamic_lane_profile_param = QString::fromStdString(params.get("DynamicLaneProfile"));
  toggles["VisionCurveLaneless"]->setEnabled(dynamic_lane_profile_param == "2");
  toggles["VisionCurveLaneless"]->refresh();

  bool custom_driving_model_valid = params.getBool("CustomDrivingModel");
  auto driving_model_generation = QString::fromStdString(params.get("DrivingModelGeneration"));
  bool model_use_lateral_planner = custom_driving_model_valid && driving_model_generation == "1";
  auto driving_model_name = custom_driving_model_valid && driving_model_generation != "0" ? QString::fromStdString(params.get("DrivingModelName")) : CURRENT_MODEL;
  QString driving_model_text = QString("<font color='yellow'>" + driving_model_name + "</font>");
  dlp_settings->setEnabled(model_use_lateral_planner);
  toggles["VisionCurveLaneless"]->setVisible(model_use_lateral_planner);
  QString dlp_incompatible_desc = "<font color='yellow'>" + tr("Dynamic Lane Profile is not available with the current Driving Model") + " [</font>" + driving_model_text + "<font color='yellow'>]</font>";

  toggles["CustomOffsets"]->setEnabled(model_use_lateral_planner);
  QString custom_offsets_incompatible_desc = "<font color='yellow'>" + tr("Custom Offsets is not available with the current Driving Model") + " [</font>" + driving_model_text + "<font color='yellow'>]</font>";

  auto enforce_torque_lateral = toggles["EnforceTorqueLateral"];
  auto custom_torque_lateral = toggles["CustomTorqueLateral"];
  auto live_torque = toggles["LiveTorque"];
  auto live_torque_relaxed = toggles["LiveTorqueRelaxed"];
  auto torqued_override = toggles["TorquedOverride"];
  auto nnff_toggle = toggles["NNFF"];

  auto custom_stock_long_param = params.getBool("CustomStockLong");
  auto enable_slc_param = params.getBool("EnableSlc");
  auto v_tsc = toggles["TurnVisionControl"];
  auto m_tsc = toggles["TurnSpeedControl"];
  auto reverse_acc = toggles["ReverseAccChange"];
  auto slc_toggle = toggles["EnableSlc"];

  auto is_offroad = params.getBool("IsOffroad");

  // NNLC/NNFF
  QString nnff_available_desc = tr("NNLC is currently not available on this platform.");
  QString nnff_fuzzy_desc = tr("Match: \"Exact\" is ideal, but \"Fuzzy\" is fine too. Reach out to the sunnypilot team in the following channel at the sunnypilot Discord server if there are any issues: ")
                               + "<font color='white'><b>#tuning-nnlc</b></font>";
  QString nnff_status_init = "<font color='yellow'>⚠️ " + tr("Start the car to check car compatibility") + "</font>";
  QString nnff_not_loaded = "<font color='yellow'>⚠️ " + tr("NNLC Not Loaded") + "</font>";
  QString nnff_loaded = "<font color=#00ff00>✅ " + tr("NNLC Loaded") + "</font>";
  auto _car_model = QString::fromStdString(params.get("NNFFCarModel"));

  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    // NNLC/NNFF
    {
      if (CP.getSteerControlType() == cereal::CarParams::SteerControlType::ANGLE) {
        enforce_torque_lateral->setEnabled(false);
        params.remove("EnforceTorqueLateral");

        nnff_toggle->setDescription(nnffDescriptionBuilder(nnff_available_desc));
        nnff_toggle->setEnabled(false);
        params.remove("NNFF");
      } else if (nnff_toggle->isToggled()) {
        if (CP.getLateralTuning().which() == cereal::CarParams::LateralTuning::TORQUE) {
          QString nn_model_name = QString::fromStdString(CP.getLateralTuning().getTorque().getNnModelName());
          QString nn_fuzzy = CP.getLateralTuning().getTorque().getNnModelFuzzyMatch() ? tr("Fuzzy") : tr("Exact");

          nnff_toggle->setDescription(nnffDescriptionBuilder(
            (nn_model_name == "")     ? nnff_status_init :
            (nn_model_name == "mock") ? (nnff_not_loaded + "<br>" + tr("Reach out to the sunnypilot team in the following channel at the sunnypilot Discord server and donate logs to get NNLC loaded for your car: ")
                                         + "<font color='white'><b>#tuning-nnlc</b></font>") :
                                        (nnff_loaded + " | " + tr("Match") + " = " + nn_fuzzy + " | " + _car_model + "<br><br>" + nnff_fuzzy_desc)));
          enforce_torque_lateral->setEnabled(false);
        } else {
          nnff_toggle->setDescription(nnffDescriptionBuilder(nnff_status_init));
        }
      } else {
        nnff_toggle->setDescription(nnff_description);
      }
    }

    if (hasLongitudinalControl(CP) || custom_stock_long_param) {
      v_tsc->setEnabled(true);
      m_tsc->setEnabled(true);
      reverse_acc->setEnabled(true);
      slc_toggle->setEnabled(true);
      if (!slcSettings->isVisible() && enable_slc_param) {
        slcSettings->setVisible(true);
      }
    } else {
      v_tsc->setEnabled(false);
      m_tsc->setEnabled(false);
      reverse_acc->setEnabled(false);
      slc_toggle->setEnabled(false);
      params.remove("EnableSlc");
      slcSettings->setEnabled(false);
    }

    enforce_torque_lateral->refresh();
    slc_toggle->refresh();
    nnff_toggle->refresh();
    m_tsc->refresh();
  } else {
    v_tsc->setEnabled(false);
    m_tsc->setEnabled(false);
    reverse_acc->setEnabled(false);
    slc_toggle->setEnabled(false);
    slcSettings->setEnabled(false);

    nnff_toggle->setDescription(nnff_toggle->isToggled() ? nnffDescriptionBuilder(nnff_status_init) : nnff_description);
  }

  if (nnff_toggle->getDescription() != nnff_description) {
    nnff_toggle->showDescription();
  }

  // toggle names to update when EnforceTorqueLateral is flipped
  std::vector<std::string> torqueLateralGroup{"CustomTorqueLateral", "TorqueLateralJerk", "LiveTorque", "LiveTorqueRelaxed", "TorquedOverride"};
  for (const auto& torqueLateralToggle : torqueLateralGroup) {
    if (toggles.find(torqueLateralToggle) != toggles.end()) {
      if (nnff_toggle->isToggled()) {
        toggles[torqueLateralToggle]->setVisible(false);
        toggles[torqueLateralToggle]->setEnabled(false);
      }
    }
  }

  for (const auto& torqueLateralToggle : torqueLateralGroup) {
    if (toggles.find(torqueLateralToggle) != toggles.end()) {
      toggles[torqueLateralToggle]->setVisible(enforce_torque_lateral->isToggled());
      toggles[torqueLateralToggle]->setEnabled(enforce_torque_lateral->isToggled());
    }
  }

  if (enforce_torque_lateral->isToggled()) {
    live_torque_relaxed->setVisible(live_torque->isToggled());
    torqued_override->setVisible(custom_torque_lateral->isToggled());
  } else {
    params.putBool("LiveTorque", false);
    params.putBool("CustomTorqueLateral", false);
  }

  // toggle names to update when CustomTorqueLateral is flipped
  std::vector<AbstractControlSP_SELECTOR*> customTorqueGroup{friction, lat_accel_factor};
  for (const auto& customTorqueControl : customTorqueGroup) {
    customTorqueControl->setVisible(!(nnff_toggle->isToggled() || !custom_torque_lateral->isToggled()));
    customTorqueControl->setEnabled(!(nnff_toggle->isToggled() || !custom_torque_lateral->isToggled()));
  }

  toggles["CustomTorqueLateral"]->setEnabled(is_offroad);
  toggles["LiveTorque"]->setEnabled(is_offroad);
  toggles["LiveTorqueRelaxed"]->setEnabled(is_offroad);

  toggles["CustomOffsets"]->setDescription((model_use_lateral_planner ? "" : custom_offsets_incompatible_desc + "<br><br>") + custom_offsets_description);
  dlp_settings->setDescription((model_use_lateral_planner ? "" : dlp_incompatible_desc + "<br><br>") + dlp_description);
}

TorqueFriction::TorqueFriction() : OptionControlSP(
  "TorqueFriction",
  tr("FRICTION"),
  tr("Adjust Friction for the Torque Lateral Controller. <b>Live</b>: Override self-tune values; <b>Offline</b>: Override self-tune offline values at car restart."),
  "../assets/offroad/icon_blank.png",
  {0, 50}) {

  refresh();
}

void TorqueFriction::refresh() {
  float torqueFrictionVal = QString::fromStdString(params.get("TorqueFriction")).toInt() * 0.01;
  setTitle("FRICTION - " + (params.getBool("TorquedOverride") ? tr("Real-time and Offline") : tr("Offline Only")));
  setLabel(QString::number(torqueFrictionVal));
}

TorqueMaxLatAccel::TorqueMaxLatAccel() : OptionControlSP(
  "TorqueMaxLatAccel",
  tr("LAT_ACCEL_FACTOR"),
  tr("Adjust Max Lateral Acceleration for the Torque Lateral Controller. <b>Live</b>: Override self-tune values; <b>Offline</b>: Override self-tune offline values at car restart."),
  "../assets/offroad/icon_blank.png",
  {1, 500}) {

  refresh();
}

void TorqueMaxLatAccel::refresh() {
  float torqueMaxLatAccelVal = QString::fromStdString(params.get("TorqueMaxLatAccel")).toInt() * 0.01;
  QString unit = "m/s²";
  setTitle("LAT_ACCEL_FACTOR - " + (params.getBool("TorquedOverride") ? tr("Real-time and Offline") : tr("Offline Only")));
  setLabel(QString::number(torqueMaxLatAccelVal) + " " + unit);
}
