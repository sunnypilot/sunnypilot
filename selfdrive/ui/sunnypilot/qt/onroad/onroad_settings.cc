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

#include "selfdrive/ui/sunnypilot/qt/onroad/onroad_settings.h"

#include <map>
#include <string>
#include <utility>

#include <QApplication>

#include "common/util.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnypilot/speed_limit_policy_settings.h"

OnroadSettings::OnroadSettings(bool closeable, QWidget *parent) : QFrame(parent) {
  setContentsMargins(0, 0, 0, 0);
  setAttribute(Qt::WA_NoMousePropagation);

  auto *frame = new QVBoxLayout(this);
  frame->setContentsMargins(40, 40, 40, 25);
  frame->setSpacing(0);

  auto *heading_frame = new QHBoxLayout;
  heading_frame->setContentsMargins(0, 0, 0, 0);
  heading_frame->setSpacing(32);
  {
    if (closeable) {
      auto *close_btn = new QPushButton("←");
      close_btn->setStyleSheet(R"(
        QPushButton {
          color: #FFFFFF;
          font-size: 100px;
          padding-bottom: 8px;
          border 1px grey solid;
          border-radius: 70px;
          background-color: #292929;
          font-weight: 500;
        }
        QPushButton:pressed {
          background-color: #3B3B3B;
        }
      )");
      close_btn->setFixedSize(140, 140);
      QObject::connect(close_btn, &QPushButton::clicked, [=]() { emit closeSettings(); });
      // TODO: read map_on_left from ui state
      heading_frame->addWidget(close_btn);
    }

    auto *heading = new QVBoxLayout;
    heading->setContentsMargins(0, 0, 0, 0);
    heading->setSpacing(16);
    {
      auto *title = new QLabel(tr("ONROAD OPTIONS"), this);
      title->setStyleSheet("color: #FFFFFF; font-size: 54px; font-weight: 600;");
      heading->addWidget(title);
    }
    heading_frame->addLayout(heading, 1);
  }
  frame->addLayout(heading_frame);
  frame->addSpacing(32);

  QWidget *options_container = new QWidget(this);
  options_layout = new QVBoxLayout(options_container);
  options_layout->setContentsMargins(0, 32, 0, 32);
  options_layout->setSpacing(20);

  // Gap Adjust Cruise
  options_layout->addWidget(gac_widget = new OptionWidget(this));
  QObject::connect(gac_widget, &OptionWidget::updateParam, this, &OnroadSettings::changeGapAdjustCruise);

  // Acceleration Personality
  options_layout->addWidget(ap_widget = new OptionWidget(this));
  QObject::connect(ap_widget, &OptionWidget::updateParam, this, &OnroadSettings::changeAccelerationPersonality);

  // Dynamic Personality
  options_layout->addWidget(dynamic_personality_widget = new OptionWidget(this));
  QObject::connect(dynamic_personality_widget, &OptionWidget::updateParam, this, &OnroadSettings::changeDynamicPersonality);

  // Dynamic Lane Profile
  options_layout->addWidget(dlp_widget = new OptionWidget(this));
  QObject::connect(dlp_widget, &OptionWidget::updateParam, this, &OnroadSettings::changeDynamicLaneProfile);

  // Dynamic Experimental Control
  options_layout->addWidget(dec_widget = new OptionWidget(this));
  QObject::connect(dec_widget, &OptionWidget::updateParam, this, &OnroadSettings::changeDynamicExperimentalControl);

  // Speed Limit Control
  options_layout->addWidget(slc_widget = new OptionWidget(this));
  QObject::connect(slc_widget, &OptionWidget::updateParam, this, &OnroadSettings::changeSpeedLimitControl);

  options_layout->addStretch();

  ScrollViewSP *options_scroller = new ScrollViewSP(options_container, this);
  options_scroller->setFrameShape(QFrame::NoFrame);
  frame->addWidget(options_scroller);

  auto *subtitle_frame = new QHBoxLayout;
  subtitle_frame->setContentsMargins(0, 0, 0, 0);
  {
    auto *subtitle_heading = new QVBoxLayout;
    subtitle_heading->setContentsMargins(0, 0, 0, 0);
    {
      auto *subtitle = new QLabel(tr("<b>ONROAD SETTINGS | SUNNYPILOT</b>"), this);
      subtitle->setStyleSheet("color: #A0A0A0; font-size: 34px; font-weight: 300;");
      subtitle_heading->addWidget(subtitle, 0, Qt::AlignCenter);
    }
    subtitle_frame->addLayout(subtitle_heading, 1);
  }
  frame->addSpacing(25);
  frame->addLayout(subtitle_frame);

  setStyleSheet("OnroadSettings { background-color: #333333; }");

  param_watcher = new ParamWatcher(this);

  QObject::connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    refresh();
  });

  refresh();
}

void OnroadSettings::changeDynamicLaneProfile() {
  UISceneSP &scene = uiStateSP()->scene;
  bool can_change = scene.driving_model_generation == cereal::ModelGeneration::ONE;
  if (can_change) {
    scene.dynamic_lane_profile++;
    scene.dynamic_lane_profile = scene.dynamic_lane_profile > 2 ? 0 : scene.dynamic_lane_profile;
    params.put("DynamicLaneProfile", std::to_string(scene.dynamic_lane_profile));
  }
  refresh();
}

void OnroadSettings::changeGapAdjustCruise() {
  UISceneSP &scene = uiStateSP()->scene;
  const auto cp = (*uiStateSP()->sm)["carParams"].getCarParams();
  bool can_change = hasLongitudinalControl(cp);
  if (can_change) {
    scene.longitudinal_personality--;
    scene.longitudinal_personality = scene.longitudinal_personality < 0 ? 3 : scene.longitudinal_personality;
    params.put("LongitudinalPersonality", std::to_string(scene.longitudinal_personality));
  }
  refresh();
}

void OnroadSettings::changeAccelerationPersonality() {
  UISceneSP &scene = uiStateSP()->scene;
  const auto cp = (*uiStateSP()->sm)["carParams"].getCarParams();
  bool can_change = hasLongitudinalControl(cp);
  if (can_change) {
    scene.longitudinal_accel_personality--;
    scene.longitudinal_accel_personality = scene.longitudinal_accel_personality < 0 ? 3 : scene.longitudinal_accel_personality;
    params.put("AccelPersonality", std::to_string(scene.longitudinal_accel_personality));
  }
  refresh();
}

void OnroadSettings::changeDynamicPersonality() {
  UISceneSP &scene = uiStateSP()->scene;
  const auto cp = (*uiStateSP()->sm)["carParams"].getCarParams();
  bool can_change = hasLongitudinalControl(cp);
  if (can_change) {
    scene.dynamic_personality = !scene.dynamic_personality;
    params.putBool("DynamicPersonality", scene.dynamic_personality);
  }
  refresh();
}

void OnroadSettings::changeDynamicExperimentalControl() {
  UISceneSP &scene = uiStateSP()->scene;
  const auto cp = (*uiStateSP()->sm)["carParams"].getCarParams();
  bool can_change = hasLongitudinalControl(cp);
  if (can_change) {
    scene.dynamic_experimental_control = !scene.dynamic_experimental_control;
    params.putBool("DynamicExperimentalControl", scene.dynamic_experimental_control);
  }
  refresh();
}

void OnroadSettings::changeSpeedLimitControl() {
  UISceneSP &scene = uiStateSP()->scene;
  const auto cp = (*uiStateSP()->sm)["carParams"].getCarParams();
  bool can_change = hasLongitudinalControl(cp) || !cp.getPcmCruiseSpeed();
  int max_policy = SpeedLimitPolicySettings::speed_limit_policy_texts.size() - 1;

  if (can_change) {
    if (!scene.speed_limit_control_enabled) {
      // If EnableSlc is OFF, set it to ON and reset SpeedLimitControlPolicy
      scene.speed_limit_control_enabled = true;
      scene.speed_limit_control_policy = 0;
    } else if (scene.speed_limit_control_policy < max_policy) {
      // If EnableSlc is already ON then increase SpeedLimitControlPolicy till it reaches 6
      scene.speed_limit_control_policy++;
    } else {
      // Once we cycle through all SpeedLimitControlPolicy, set EnableSlc to OFF and reset SpeedLimitControlPolicy
      scene.speed_limit_control_enabled = false;
      scene.speed_limit_control_policy = 0;
    }
    params.putBool("EnableSlc", scene.speed_limit_control_enabled);
    params.put("SpeedLimitControlPolicy", std::to_string(scene.speed_limit_control_policy));
  }
  refresh();
}

void OnroadSettings::showEvent(QShowEvent *event) {
  refresh();
}

void OnroadSettings::refresh() {
  param_watcher->addParam("DynamicLaneProfile");
  param_watcher->addParam("LongitudinalPersonality");
  param_watcher->addParam("AccelPersonality");
  param_watcher->addParam("DynamicPersonality");
  param_watcher->addParam("DynamicExperimentalControl");
  param_watcher->addParam("EnableSlc");

  UISceneSP &scene = uiStateSP()->scene;
  // Update live params on Feature Status on camera view
  scene.dynamic_lane_profile = std::atoi(params.get("DynamicLaneProfile").c_str());
  scene.longitudinal_personality = std::atoi(params.get("LongitudinalPersonality").c_str());
  scene.longitudinal_accel_personality = std::atoi(params.get("AccelPersonality").c_str());
  scene.dynamic_personality = params.getBool("DynamicPersonality");
  scene.dynamic_experimental_control = params.getBool("DynamicExperimentalControl");
  scene.speed_limit_control_enabled = params.getBool("EnableSlc");
  scene.speed_limit_control_policy = std::atoi(params.get("SpeedLimitControlPolicy").c_str());

  if (!isVisible()) return;

  setUpdatesEnabled(false);

  const auto cp = (*uiStateSP()->sm)["carParams"].getCarParams();

  // Dynamic Lane Profile
  dlp_widget->updateDynamicLaneProfile("DynamicLaneProfile");
  dlp_widget->setVisible(scene.driving_model_generation == cereal::ModelGeneration::ONE);

  // Gap Adjust Cruise
  gac_widget->updateGapAdjustCruise("LongitudinalPersonality");
  gac_widget->setVisible(hasLongitudinalControl(cp));

  // Acceleration Personality
  ap_widget->updateAccelerationPersonality("AccelPersonality");
  ap_widget->setVisible(hasLongitudinalControl(cp));

  // Dynamic Personality
  dynamic_personality_widget->updateDynamicPersonality("DynamicPersonality");
  dynamic_personality_widget->setVisible(hasLongitudinalControl(cp));

  // Dynamic Experimental Control
  dec_widget->updateDynamicExperimentalControl("DynamicExperimentalControl");
  dec_widget->setVisible(hasLongitudinalControl(cp));

  // Speed Limit Control
  slc_widget->updateSpeedLimitControl("EnableSlc");
  slc_widget->setVisible(hasLongitudinalControl(cp) || !cp.getPcmCruiseSpeed());

  setUpdatesEnabled(true);
}

OptionWidget::OptionWidget(QWidget *parent) : QPushButton(parent) {
  setContentsMargins(0, 0, 0, 0);

  auto *frame = new QHBoxLayout(this);
  frame->setContentsMargins(32, 24, 32, 24);
  frame->setSpacing(32);

  icon = new QLabel(this);
  icon->setAlignment(Qt::AlignCenter);
  icon->setFixedSize(68, 68);
  icon->setObjectName("icon");
  frame->addWidget(icon);

  auto *inner_frame = new QVBoxLayout;
  inner_frame->setContentsMargins(0, 0, 0, 0);
  inner_frame->setSpacing(0);
  {
    title = new ElidedLabelSP(this);
    title->setAttribute(Qt::WA_TransparentForMouseEvents);
    inner_frame->addWidget(title);

    subtitle = new ElidedLabelSP(this);
    subtitle->setAttribute(Qt::WA_TransparentForMouseEvents);
    subtitle->setObjectName("subtitle");
    inner_frame->addWidget(subtitle);
  }
  frame->addLayout(inner_frame, 1);

  setFixedHeight(164);
  setStyleSheet(R"(
    OptionWidget { background-color: #202123; border-radius: 10px; }
    QLabel { color: #FFFFFF; font-size: 48px; font-weight: 400; }
    #icon { background-color: #3B4356; border-radius: 34px; }
    #subtitle { color: #9BA0A5; }

    /* pressed */
    OptionWidget:pressed { background-color: #18191B; }
  )");
  QObject::connect(this, &QPushButton::clicked, [this]() { emit updateParam(); });
}

void OptionWidget::updateDynamicLaneProfile(QString param) {
  auto icon_color = "#3B4356";
  auto title_text = "";
  auto subtitle_text = "Dynamic Lane Profile";
  auto dlp = atoi(params.get(param.toStdString()).c_str());

  if (dlp == 0) {
    title_text = "Laneful";
    icon_color = "#2020f8";
  } else if (dlp == 1) {
    title_text = "Laneless";
    icon_color = "#0df87a";
  } else if (dlp == 2) {
    title_text = "Auto";
    icon_color = "#0df8f8";
  }

  icon->setStyleSheet(QString("QLabel#icon { background-color: %1; border-radius: 34px; }").arg(icon_color));

  title->setText(title_text);
  subtitle->setText(subtitle_text);
  subtitle->setVisible(true);

  setStyleSheet(styleSheet());
}

void OptionWidget::updateGapAdjustCruise(QString param) {
  auto icon_color = "#3B4356";
  auto title_text = "";
  auto subtitle_text = "Driving Personality";
  auto lp = atoi(params.get(param.toStdString()).c_str());

  if (lp == 0) {
    title_text = "Aggressive";
    icon_color = "#ff4b4b";
  } else if (lp == 1) {
    title_text = "Moderate";
    icon_color = "#fcff4b";
  } else if (lp == 2) {
    title_text = "Standard";
    icon_color = "#4bff66";
  } else if (lp == 3) {
    title_text = "Relaxed";
    icon_color = "#6a0ac9";
  }

  icon->setStyleSheet(QString("QLabel#icon { background-color: %1; border-radius: 34px; }").arg(icon_color));

  title->setText(title_text);
  subtitle->setText(subtitle_text);
  subtitle->setVisible(true);

  setStyleSheet(styleSheet());
}

void OptionWidget::updateAccelerationPersonality(QString param) {
  auto icon_color = "#3B4356";
  auto title_text = "";
  auto subtitle_text = "Acceleration Personality";
  auto ap = atoi(params.get(param.toStdString()).c_str());

  if (ap == 0) {
    title_text = "Sport";
    icon_color = "#ff4b4b";
  } else if (ap == 1) {
    title_text = "Normal";
    icon_color = "#fcff4b";
  } else if (ap == 2) {
    title_text = "Eco";
    icon_color = "#4bff66";
  } else if (ap == 3) {
    title_text = "Stock";
    icon_color = "#6a0ac9";
  }

  icon->setStyleSheet(QString("QLabel#icon { background-color: %1; border-radius: 34px; }").arg(icon_color));

  title->setText(title_text);
  subtitle->setText(subtitle_text);
  subtitle->setVisible(true);

  setStyleSheet(styleSheet());
}

void OptionWidget::updateDynamicPersonality(QString param) {
  auto icon_color = "#3B4356";
  auto title_text = "";
  auto subtitle_text = "Dynamic Personality";
  auto dynamic_personality = atoi(params.get(param.toStdString()).c_str());

  if (dynamic_personality == 0) {
    title_text = "Disabled";
    icon_color = "#3B4356";
  } else if (dynamic_personality == 1) {
    title_text = "Enabled";
    icon_color = "#0df87a";
  }

  icon->setStyleSheet(QString("QLabel#icon { background-color: %1; border-radius: 34px; }").arg(icon_color));

  title->setText(title_text);
  subtitle->setText(subtitle_text);
  subtitle->setVisible(true);

  setStyleSheet(styleSheet());
}

void OptionWidget::updateDynamicExperimentalControl(QString param) {
  auto icon_color = "#3B4356";
  auto title_text = "";
  auto subtitle_text = "Dynamic Experimental";
  auto long_personality = atoi(params.get(param.toStdString()).c_str());

  if (long_personality == 0) {
    title_text = "Disabled";
    icon_color = "#3B4356";
  } else if (long_personality == 1) {
    title_text = "Enabled";
    icon_color = "#0df87a";
  }

  icon->setStyleSheet(QString("QLabel#icon { background-color: %1; border-radius: 34px; }").arg(icon_color));

  title->setText(title_text);
  subtitle->setText(subtitle_text);
  subtitle->setVisible(true);

  setStyleSheet(styleSheet());
}

void OptionWidget::updateSpeedLimitControl(QString param) {
  auto subtitle_text = "Speed Limit Control";
  std::string icon_color; // Declare icon_color here

  // Define the speed_limit_policy_texts
  const auto& speed_limit_policy_texts = SpeedLimitPolicySettings::speed_limit_policy_texts;

  auto enable_slc_status = atoi(params.get(param.toStdString()).c_str());
  auto speed_limit_control_policy_status = atoi(params.get("SpeedLimitControlPolicy").c_str());
  auto title_text = QString(speed_limit_policy_texts.at(speed_limit_control_policy_status)).replace("\n", " ");

  std::map<int, std::string> color_map = {
    {0, "#1f77b4"}, // Muted blue for "Nav Only"
    {1, "#2ca02c"}, // Cooked asparagus green for "Map Only"
    {2, "#d62728"}, // Brick red for "Car Only"
    {3, "#9467bd"}, // Muted purple for "Nav First"
    {4, "#8c564b"}, // Chestnut brown for "Map First"
    {5, "#e377c2"}, // Raspberry yogurt pink for "Car First"
    {6, "#FFA500"}, // Orange for "Combined"
  };

  if (enable_slc_status == 0) {
    title_text = "Disabled";
    icon_color = "#3B4356"; // Color for "Disabled status"
  } else if (enable_slc_status == 1) {
    title_text = title_text;
    icon_color = color_map[speed_limit_control_policy_status]; // Color for "Enabled status"
  }

  icon->setStyleSheet(QString("QLabel#icon { background-color: %1; border-radius: 34px; }").arg(icon_color.c_str()));
  title->setText(title_text);
  subtitle->setText(subtitle_text);
  subtitle->setVisible(true);

  setStyleSheet(styleSheet());
}
