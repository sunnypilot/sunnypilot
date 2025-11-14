/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <QJsonDocument>
#include <QJsonObject>
#include <vector>

#include "selfdrive/ui/qt/offroad/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

class NavigationPanel : public QWidget {
  Q_OBJECT

public:
  explicit NavigationPanel(QWidget* parent = nullptr);
  void showEvent(QShowEvent *event) override;
  void refresh();

public slots:
  void updateNavigationVisibility(bool state);

private:
  Params params;
  ListWidget* list;
  ScrollViewSP* scroller;
  ParamControlSP* allow_navigation;
  ButtonControl* mapbox_token;
  ButtonControl* mapbox_route;
  ButtonControl* clear_route;
  ParamControlSP* mapbox_recompute;
  ParamControlSP* nav_allowed;
  MultiButtonControlSP* favorites_selector;
  std::vector<ButtonControl*> set_buttons;
  ButtonControl* add_fav;
  ButtonControl* remove_fav;
};
