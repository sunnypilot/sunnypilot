#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/display_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnypilot_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/visuals_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/trips_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/monitoring_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/osm_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/software_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnylink_settings.h"


inline void ReplaceWidget(QWidget* old_widget, QWidget* new_widget) {
  if (old_widget && old_widget->parentWidget() && old_widget->parentWidget()->layout()) {
    old_widget->parentWidget()->layout()->replaceWidget(old_widget, new_widget);
    old_widget->hide();
    old_widget->deleteLater();
  }
}
