#pragma once
#include "selfdrive/ui/qt/offroad_home.h"

#ifdef ENABLE_MAPS
#include "selfdrive/ui/qt/maps/map_settings.h"
#endif


class OffroadHomeSP : public OffroadHome {
  Q_OBJECT

public:
  void replaceLeftWidget();
  explicit OffroadHomeSP(QWidget* parent = 0);

private:
  static void replaceWidget(QWidget* old_widget, QWidget* new_widget);
  Params params;
  bool custom_mapbox;
};