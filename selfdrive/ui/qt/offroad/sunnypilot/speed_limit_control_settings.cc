#include "selfdrive/ui/qt/offroad/sunnypilot/speed_limit_control_settings.h"

SlcSettings::SlcSettings(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidget *list = new ListWidget(this, false);

  std::vector<QString> speed_limit_offset_settings_texts{tr("Default"), tr("Fixed"), tr("Percentage")};
  speed_limit_offset_settings = new ButtonParamControl(
    "SpeedLimitOffsetType", tr("Offset"), tr("Set speed limit slightly higher than actual speed limit for a more natural drive."),
    "../assets/offroad/icon_blank.png",
    speed_limit_offset_settings_texts,
    380
  );
  list->addItem(speed_limit_offset_settings);

  slvo = new SpeedLimitValueOffset();
  connect(slvo, &SPOptionControl::updateLabels, slvo, &SpeedLimitValueOffset::refresh);
  list->addItem(slvo);

  connect(speed_limit_offset_settings, &ButtonParamControl::buttonToggled, this, &SlcSettings::updateToggles);
  connect(speed_limit_offset_settings, &ButtonParamControl::buttonToggled, slvo, &SpeedLimitValueOffset::refresh);

  speed_limit_control_policy = new ButtonParamControl(
    "SpeedLimitControlPolicy",
    tr("Speed Limit Control Policy"),
    "",
    "../assets/offroad/icon_blank.png",
    speed_limit_control_policy_texts,
    250
  );
  speed_limit_control_policy->showDescription();
  connect(speed_limit_control_policy, &ButtonParamControl::buttonToggled, this, &SlcSettings::updateToggles);
  list->addItem(speed_limit_control_policy);

  param_watcher = new ParamWatcher(this);

  QObject::connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    updateToggles();
  });

  main_layout->addWidget(new ScrollView(list, this));
}

void SlcSettings::showEvent(QShowEvent *event) {
  updateToggles();
}

void SlcSettings::updateToggles() {
  param_watcher->addParam("SpeedLimitControlPolicy");

  if (!isVisible()) {
    return;
  }

  speed_limit_control_policy->setButton("SpeedLimitControlPolicy");

  auto cp_bytes = params.get("CarParamsPersistent");
  auto custom_stock_long_param = params.getBool("CustomStockLong");
  auto speed_limit_control = params.getBool("EnableSlc");

  speed_limit_control_policy->setDescription(slcDescriptionBuilder("SpeedLimitControlPolicy", speed_limit_control_policy_descriptions));

  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    if (hasLongitudinalControl(CP) || custom_stock_long_param) {
      speed_limit_offset_settings->setEnabled(speed_limit_control);
      speed_limit_control_policy->setEnabled(true);
      slvo->setEnabled(speed_limit_control && QString::fromStdString(params.get("SpeedLimitOffsetType")) != "0");
    } else {
      slvo->setEnabled(false);
      speed_limit_control_policy->setEnabled(false);
      speed_limit_offset_settings->setEnabled(false);
    }
  } else {
    slvo->setEnabled(false);
    speed_limit_control_policy->setEnabled(false);
    speed_limit_offset_settings->setEnabled(false);
  }
}

// Speed Limit Control Custom Offset
SpeedLimitValueOffset::SpeedLimitValueOffset() : SPOptionControl (
  "SpeedLimitValueOffset",
  "",
  "",
  "../assets/offroad/icon_blank.png",
  {-30, 30}) {

  refresh();
}

void SpeedLimitValueOffset::refresh() {
  QString option = QString::fromStdString(params.get("SpeedLimitValueOffset"));
  QString offset_type = QString::fromStdString(params.get("SpeedLimitOffsetType"));
  bool is_metric = params.getBool("IsMetric");
  QString unit = "";

  if (option.toInt() >= 0) {
    option = "+" + option;
  }

  if (offset_type == "0") {
    option = "";
    unit = "N/A";
  } else if (offset_type == "1") {
    unit = is_metric ? " km/h" : " mph";
  } else if (offset_type == "2") {
    unit = " %";
  }
  setLabel(option + unit);
}
