#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_display_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_sunnypilot_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_vehicle_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_visuals_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_trips_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_monitoring_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_osm_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_software_settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sp_priv_sunnylink_settings.h"


inline void ReplaceWidget(QWidget* old_widget, QWidget* new_widget)
{
    old_widget->parentWidget()->layout()->replaceWidget(old_widget, new_widget);
    delete old_widget;
}
