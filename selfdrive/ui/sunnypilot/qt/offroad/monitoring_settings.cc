#include "selfdrive/ui/sunnypilot/qt/offroad/monitoring_settings.h"

MonitoringPanel::MonitoringPanel(QWidget *parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);

  ListWidget *list = new ListWidget(this, false);
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "HandsOnWheelMonitoring",
      tr("Enable Hands on Wheel Monitoring"),
      tr("Monitor and alert when driver is not keeping the hands on the steering wheel."),
      "../assets/offroad/icon_blank.png",
    }
  };

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControlSP(param, title, desc, icon, this);

    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  monitoringScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(monitoringScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  vlayout->addWidget(new ScrollView(list, this), 1);
  main_layout->addWidget(monitoringScreen);
}
