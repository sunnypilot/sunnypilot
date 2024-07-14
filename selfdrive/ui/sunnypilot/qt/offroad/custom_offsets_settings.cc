#include "selfdrive/ui/sunnypilot/qt/offroad/custom_offsets_settings.h"

CustomOffsetsSettings::CustomOffsetsSettings(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidgetSP *list = new ListWidgetSP(this, false);

  // Controls: Camera Offset (cm)
  camera_offset = new CameraOffset();
  connect(camera_offset, &OptionControlSP::updateLabels, camera_offset, &CameraOffset::refresh);
  camera_offset->showDescription();
  list->addItem(camera_offset);

  // Controls: Path Offset (cm)
  path_offset = new PathOffset();
  connect(path_offset, &OptionControlSP::updateLabels, path_offset, &PathOffset::refresh);
  path_offset->showDescription();
  list->addItem(path_offset);

  main_layout->addWidget(new ScrollView(list, this));
}

// Camera Offset Value
CameraOffset::CameraOffset() : OptionControlSP (
  "CameraOffset",
  tr("Camera Offset - Laneful Only"),
  tr("Hack to trick vehicle to be left or right biased in its lane. Decreasing the value will make the car keep more left, increasing will make it keep more right. Changes take effect immediately. Default: +4 cm"),
  "../assets/offroad/icon_blank.png",
  {-20, 20}) {

  refresh();
}

void CameraOffset::refresh() {
  QString option = QString::fromStdString(params.get("CameraOffset"));
  QString unit = tr(" cm");
  if (option.toInt() >= 0) {
    option = "+" + option;
  }
  setLabel(option + unit);
}

// Path Offset Value
PathOffset::PathOffset() : OptionControlSP (
  "PathOffset",
  tr("Path Offset"),
  tr("Hack to trick the model path to be left or right biased of the lane. Decreasing the value will shift the model more left, increasing will shift the model more right. Changes take effect immediately."),
  "../assets/offroad/icon_blank.png",
  {-10, 10}) {

  refresh();
}

void PathOffset::refresh() {
  QString option = QString::fromStdString(params.get("PathOffset"));
  QString unit = tr(" cm");
  if (option.toInt() >= 0) {
    option = "+" + option;
  }
  setLabel(option + unit);
}
