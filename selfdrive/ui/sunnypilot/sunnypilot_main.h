#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/display_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/sunnypilot_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/vehicle_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/visuals_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/trips_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/monitoring_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/osm_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/software_settings_sp.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/sunnylink_settings.h"


inline void ReplaceWidget(QWidget* old_widget, QWidget* new_widget)
{
    old_widget->parentWidget()->layout()->replaceWidget(old_widget, new_widget);
    delete old_widget;
}
