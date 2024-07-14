#include "selfdrive/ui/sunnypilot/qt/offroad/speed_limit_warning_settings.h"

SpeedLimitWarningSettings::SpeedLimitWarningSettings(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidgetSP *list = new ListWidgetSP(this, false);

  std::vector<QString> speed_limit_warning_texts{tr("Off"), tr("Display"), tr("Chime")};
  speed_limit_warning_settings = new ButtonParamControlSP(
    "SpeedLimitWarningType", tr("Speed Limit Warning"),
    "",
    "../assets/offroad/icon_blank.png",
    speed_limit_warning_texts,
    380
  );
  speed_limit_warning_settings->showDescription();
  list->addItem(speed_limit_warning_settings);

  speed_limit_warning_flash = new ParamControlSP(
    "SpeedLimitWarningFlash",
    tr("Warning with speed limit flash"),
    tr("When Speed Limit Warning is enabled, the speed limit sign will alert the driver when the cruising speed is faster than then speed limit plus the offset."),
    "../assets/offroad/icon_blank.png"
  );
  list->addItem(speed_limit_warning_flash);

  std::vector<QString> speed_limit_warning_offset_settings_texts{tr("Default"), tr("Fixed"), tr("Percentage")};
  speed_limit_warning_offset_settings = new ButtonParamControlSP(
    "SpeedLimitWarningOffsetType", tr("Warning Offset"),
    tr("Select the desired offset to warn the driver when the vehicle is driving faster than the speed limit."),
    "../assets/offroad/icon_blank.png",
    speed_limit_warning_offset_settings_texts,
    380
  );
  list->addItem(speed_limit_warning_offset_settings);

  slwvo = new SpeedLimitWarningValueOffset();
  connect(slwvo, &OptionControlSP::updateLabels, slwvo, &SpeedLimitWarningValueOffset::refresh);
  list->addItem(slwvo);

  connect(speed_limit_warning_settings, &ButtonParamControlSP::buttonToggled, this, &SpeedLimitWarningSettings::updateToggles);

  connect(speed_limit_warning_offset_settings, &ButtonParamControlSP::buttonToggled, this, &SpeedLimitWarningSettings::updateToggles);
  connect(speed_limit_warning_offset_settings, &ButtonParamControlSP::buttonToggled, slwvo, &SpeedLimitWarningValueOffset::refresh);

  param_watcher = new ParamWatcher(this);

  QObject::connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    updateToggles();
  });

  main_layout->addWidget(new ScrollView(list, this));
}

void SpeedLimitWarningSettings::showEvent(QShowEvent *event) {
  updateToggles();
}

void SpeedLimitWarningSettings::updateToggles() {
  param_watcher->addParam("SpeedLimitWarningType");

  if (!isVisible()) {
    return;
  }

  auto speed_limit_warning_type_param = QString::fromStdString(params.get("SpeedLimitWarningType"));
  auto speed_limit_warning_offset_type_param = QString::fromStdString(params.get("SpeedLimitWarningOffsetType"));

  speed_limit_warning_settings->setDescription(speedLimitWarningDescriptionBuilder("SpeedLimitWarningType", speed_limit_warning_descriptions));
  speed_limit_warning_flash->setEnabled(speed_limit_warning_type_param != "0");
  if (speed_limit_warning_type_param == "0") {
    params.remove("SpeedLimitWarningFlash");
    speed_limit_warning_flash->refresh();
  }
  slwvo->setEnabled(QString::fromStdString(params.get("SpeedLimitWarningOffsetType")) != "0");

  speed_limit_warning_offset_settings->setEnabled(speed_limit_warning_type_param != "0");
  slwvo->setEnabled(speed_limit_warning_offset_type_param != "0");
}

// Speed Limit Control Custom Offset
SpeedLimitWarningValueOffset::SpeedLimitWarningValueOffset() : OptionControlSP (
  "SpeedLimitWarningValueOffset",
  "",
  "",
  "../assets/offroad/icon_blank.png",
  {-30, 30}) {

  refresh();
}

void SpeedLimitWarningValueOffset::refresh() {
  QString option = QString::fromStdString(params.get("SpeedLimitWarningValueOffset"));
  QString offset_type = QString::fromStdString(params.get("SpeedLimitWarningOffsetType"));
  bool is_metric = params.getBool("IsMetric");
  QString unit = "";

  if (option.toInt() >= 0) {
    option = "+" + option;
  }

  if (offset_type == "0") {
    option = "";
    unit = tr("N/A");
  } else if (offset_type == "1") {
    unit = " " + (is_metric ? tr("km/h") : tr("mph"));
  } else if (offset_type == "2") {
    unit = " %";
  }
  setLabel(option + unit);
}
