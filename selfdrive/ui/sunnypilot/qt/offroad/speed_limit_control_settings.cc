#include "selfdrive/ui/sunnypilot/qt/offroad/speed_limit_control_settings.h"

SlcSettings::SlcSettings(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidget *list = new ListWidget(this, false);

  std::vector<QString> speed_limit_engage_texts{tr("Auto"), tr("User Confirm")};
  speed_limit_engage_settings = new ButtonParamControl(
    "SpeedLimitEngageType", tr("Engage Mode"),
    "",
    "../assets/offroad/icon_blank.png",
    speed_limit_engage_texts,
    440
  );
  speed_limit_engage_settings->showDescription();
  list->addItem(speed_limit_engage_settings);

  std::vector<QString> speed_limit_offset_settings_texts{tr("Default"), tr("Fixed"), tr("Percentage")};
  speed_limit_offset_settings = new ButtonParamControl(
    "SpeedLimitOffsetType", tr("Limit Offset"), tr("Set speed limit slightly higher than actual speed limit for a more natural drive."),
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
  param_watcher->addParam("SpeedLimitEngageType");

  if (!isVisible()) {
    return;
  }

  if (QString::fromStdString(params.get("SpeedLimitEngageType")) == "2") {
    params.put("SpeedLimitEngageType", "1");
  }

  // TODO: SP: use upstream's setCheckedButton
  speed_limit_engage_settings->setButton("SpeedLimitEngageType");

  auto cp_bytes = params.get("CarParamsPersistent");
  auto custom_stock_long_param = params.getBool("CustomStockLong");
  auto speed_limit_control = params.getBool("EnableSlc");

  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    const bool pcm_cruise_op_long = CP.getOpenpilotLongitudinalControl() && CP.getPcmCruise();

    if (hasLongitudinalControl(CP) || custom_stock_long_param) {
      speed_limit_offset_settings->setEnabled(speed_limit_control);
      slvo->setEnabled(speed_limit_control && QString::fromStdString(params.get("SpeedLimitOffsetType")) != "0");

      QString speed_limit_engage_condition_text = pcm_cruise_op_long ? tr("This platform defaults to <b>Auto</b> mode. <b>User Confirm</b> mode is not supported on this platform.") + "<br><br>" : "";
      QString speed_limit_engage_condition_param = pcm_cruise_op_long ? "0" : "SpeedLimitEngageType";
      if (pcm_cruise_op_long) {
        speed_limit_engage_settings->setDisabledSelectedButton("1");  // "User Confirm" disabled
      }
      speed_limit_engage_settings->setDescription(speed_limit_engage_condition_text + slcDescriptionBuilder(speed_limit_engage_condition_param, speed_limit_engage_descriptions));
    } else {
      slvo->setEnabled(false);
      speed_limit_offset_settings->setEnabled(false);
      speed_limit_engage_settings->setEnabled(false);
    }
  } else {
    slvo->setEnabled(false);
    speed_limit_offset_settings->setEnabled(false);
    speed_limit_engage_settings->setEnabled(false);
    speed_limit_engage_settings->setDescription(slcDescriptionBuilder("SpeedLimitEngageType", speed_limit_engage_descriptions));
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
    unit = " " + (is_metric ? tr("km/h") : tr("mph"));
  } else if (offset_type == "2") {
    unit = " %";
  }
  setLabel(option + unit);
}
