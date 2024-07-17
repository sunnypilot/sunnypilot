#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnypilot_sub_panel/sp_priv_speed_limit_policy_settings.h"

SpeedLimitPolicySettings::SpeedLimitPolicySettings(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidgetSP *list = new ListWidgetSP(this, false);

  speed_limit_policy = new ButtonParamControlSP(
    "SpeedLimitControlPolicy",
    tr("Speed Limit Source Policy"),
    "",
    "../assets/offroad/icon_blank.png",
    speed_limit_policy_texts,
    250);
  speed_limit_policy->showDescription();
  connect(speed_limit_policy, &ButtonParamControlSP::buttonToggled, this, &SpeedLimitPolicySettings::updateToggles);
  list->addItem(speed_limit_policy);

  param_watcher = new ParamWatcher(this);

  QObject::connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    updateToggles();
  });

  main_layout->addWidget(new ScrollViewSP(list, this));
}

void SpeedLimitPolicySettings::showEvent(QShowEvent *event) {
  updateToggles();
}

void SpeedLimitPolicySettings::updateToggles() {
  param_watcher->addParam("SpeedLimitControlPolicy");

  if (!isVisible()) {
    return;
  }

  // TODO: SP: use upstream's setCheckedButton
  speed_limit_policy->setButton("SpeedLimitControlPolicy");

  speed_limit_policy->setDescription(speedLimitPolicyDescriptionBuilder("SpeedLimitControlPolicy", speed_limit_policy_descriptions));
}
