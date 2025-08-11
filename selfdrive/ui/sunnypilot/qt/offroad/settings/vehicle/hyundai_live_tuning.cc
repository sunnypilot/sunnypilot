/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/hyundai_live_tuning.h"


struct ParamConfig {
  QString param, title, desc, defaultValue;
  float minVal = 0.0f, maxVal, step = 0.01f;
};

// Clipping limits on all tuning params to prevent unsafe values.
static const std::vector<ParamConfig> PARAM_CONFIGS = {
  {"LongTuningAccelMax", QObject::tr("Acceleration Max"), QObject::tr("Acceleration limit (m/s^2)"), "2.00", 0.5f, 2.0f, 0.1f},
  {"LongTuningVEgoStopping", QObject::tr("Stopping Threshold"), QObject::tr("Velocity threshold for stopping behavior (m/s)"), "0.25", 0.05f, 0.5f, 0.01f},
  {"LongTuningStoppingDecelRate", QObject::tr("Stopping Decel Rate"), QObject::tr("Deceleration rate when stopping (m/s^2)"), "0.40", 0.01f, 0.8f, 0.01f},
  {"LongTuningMinUpperJerk", QObject::tr("Min Upper Jerk"), QObject::tr("Minimum accel jerk limit (m/s^3)"), "0.50", 0.5f, 3.0f, 0.1f},
  {"LongTuningMinLowerJerk", QObject::tr("Min Lower Jerk"), QObject::tr("Minimum braking jerk limit (m/s^3)"), "0.50", 0.5f, 8.0f, 0.1f},
  {"LongTuningJerkLimits", QObject::tr("Dynamic Tune Jerk Max"), QObject::tr("Maximum lower jerk limit the tune cannot exceed (m/s^3)"), "4.00", 2.0f, 8.0f, 0.1f},
};

QWidget* createButtonWidget(const QString &text, std::function<void()> callback, bool isPushButton = false) {
  QWidget *widget = new QWidget(); QHBoxLayout *layout = new QHBoxLayout(widget);
  QAbstractButton *btn = isPushButton ? (QAbstractButton*)new PushButtonSP(text) : (QAbstractButton*)new QPushButton(text);
  if (!isPushButton) { btn->setFixedSize(250, 100); btn->setStyleSheet("QPushButton{padding:0;border-radius:20px;font-size:35px;font-weight:500;color:#E4E4E4;background-color:#393939;}QPushButton:pressed{background-color:#4a4a4a;}"); }
  QObject::connect(btn, &QAbstractButton::clicked, callback); layout->addWidget(btn, 0, Qt::AlignLeft); layout->addStretch();
  return widget;
}

HyundaiLiveTuning::HyundaiLiveTuning(QWidget *parent) : QWidget(parent) {
  main_layout = new QVBoxLayout(this); main_layout->setContentsMargins(0, 0, 0, 0); main_layout->setSpacing(0);
  list = new ListWidgetSP(this, false);
  list->addItem(createButtonWidget(tr("Back"), [=]() { emit backPress(); }));
  list->addItem(createButtonWidget(tr("Reset to defaults"), [=]() { resetToDefaults(); }, true));
  for (const auto &config : PARAM_CONFIGS) createFloatControl(config.param, config.title, config.desc, config.minVal, config.maxVal, config.step);
  main_layout->addWidget(new ScrollViewSP(list, this));
}

void HyundaiLiveTuning::createFloatControl(const QString &param, const QString &title, const QString &desc, float min_val, float max_val, float step) {
  QWidget *widget = new QWidget(); QHBoxLayout *layout = new QHBoxLayout(widget); layout->setSpacing(20);
  QVBoxLayout *text_layout = new QVBoxLayout(); QLabel *title_label = new QLabel(title); title_label->setStyleSheet("font-size: 50px; font-weight: 400;");
  QLabel *desc_label = new QLabel(desc); desc_label->setStyleSheet("font-size: 40px; color: grey;"); desc_label->setWordWrap(true);
  text_layout->addWidget(title_label); text_layout->addWidget(desc_label); layout->addLayout(text_layout, 1);

  QPushButton *minus_btn = new QPushButton("-"); QLabel *value_label = new QLabel("0.00"); QPushButton *plus_btn = new QPushButton("+");
  QString btn_style = "QPushButton{padding:0;border-radius:8px;font-size:40px;font-weight:600;color:#E4E4E4;background-color:#393939;}QPushButton:pressed{background-color:#4a4a4a;}QPushButton:disabled{color:#33E4E4E4;background-color:#2a2a2a;}";
  minus_btn->setFixedSize(120, 80); minus_btn->setStyleSheet(btn_style); plus_btn->setFixedSize(120, 80); plus_btn->setStyleSheet(btn_style);
  value_label->setAlignment(Qt::AlignCenter); value_label->setStyleSheet("font-size: 35px; font-weight: 500; min-width: 100px; color: #E4E4E4;");
  layout->addWidget(minus_btn); layout->addWidget(value_label); layout->addWidget(plus_btn);

  QTimer *plusTimer = new QTimer(widget), *minusTimer = new QTimer(widget);
  std::string param_str = param.toStdString(); QString current_value = QString::fromStdString(params.get(param_str));
  float current_float = current_value.isEmpty() ? 0.0f : current_value.toFloat();
  if (current_float == 0.0f) {
    auto it = std::find_if(PARAM_CONFIGS.begin(), PARAM_CONFIGS.end(), [&param](const ParamConfig &c) { return c.param == param; });
    if (it != PARAM_CONFIGS.end()) { current_float = it->defaultValue.toFloat(); params.put(param_str, QString::number(current_float, 'f', 2).toStdString()); }
  }
  value_label->setText(QString::number(current_float, 'f', 2));
  auto updateValue = [=](float delta) {
    float current = QString::fromStdString(params.get(param_str)).toFloat(), new_value = qMax(min_val, qMin(max_val, current + delta));
    params.put(param_str, QString::number(new_value, 'f', 2).toStdString()); value_label->setText(QString::number(new_value, 'f', 2));
    minus_btn->setEnabled(new_value > min_val); plus_btn->setEnabled(new_value < max_val);
  };
  connect(plus_btn, &QPushButton::clicked, [=]() { updateValue(step); });
  connect(minus_btn, &QPushButton::clicked, [=]() { updateValue(-step); });

  connect(plus_btn, &QPushButton::pressed, [=]() { QTimer::singleShot(300, plus_btn, [=]() { if (plus_btn->isDown()) plusTimer->start(100); });});
  connect(plus_btn, &QPushButton::released, plusTimer, &QTimer::stop);
  connect(plusTimer, &QTimer::timeout, [=]() { updateValue(step); });

  connect(minus_btn, &QPushButton::pressed, [=]() {QTimer::singleShot(300, minus_btn, [=]() { if (minus_btn->isDown()) minusTimer->start(100); });});
  connect(minus_btn, &QPushButton::released, minusTimer, &QTimer::stop);
  connect(minusTimer, &QTimer::timeout, [=]() { updateValue(-step); });
  minus_btn->setEnabled(current_float > min_val); plus_btn->setEnabled(current_float < max_val);
  list->addItem(widget); spinner_controls[param.toStdString()] = value_label;
}

void HyundaiLiveTuning::updateToggles() {
  for (const auto &pair : spinner_controls) {
    QString param_value = QString::fromStdString(params.get(pair.first));
    if (!param_value.isEmpty()) pair.second->setText(QString::number(param_value.toFloat(), 'f', 2));
  }
}

void HyundaiLiveTuning::resetToDefaults() {
  for (const auto &config : PARAM_CONFIGS) params.put(config.param.toStdString(), config.defaultValue.toStdString());
  updateToggles();
}

void HyundaiLiveTuning::showEvent(QShowEvent *event){
  updateToggles();
}
