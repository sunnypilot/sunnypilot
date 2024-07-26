#pragma once

#include "selfdrive/ui/qt/maps/map_helpers.h"

#define MAPBOX_TOKEN MAPBOX_TOKEN_SP
#define MAPS_HOST MAPS_HOST_SP

#include "common/params.h"

const QString MAPBOX_TOKEN = QString::fromStdString(Params().get("CustomMapboxTokenSk")) != "" ?
                             QString::fromStdString(Params().get("CustomMapboxTokenSk")) : util::getenv("MAPBOX_TOKEN").c_str();
const QString MAPS_HOST = util::getenv("MAPS_HOST", MAPBOX_TOKEN.isEmpty() ? "https://maps.comma.ai" : "https://api.mapbox.com").c_str();
