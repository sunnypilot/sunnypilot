/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/navigation_panel.h"

NavigationPanel::NavigationPanel(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 25, 50, 25);

  list = new ListWidget(this, false);
  scroller = new ScrollViewSP(list, this);
  main_layout->addWidget(scroller);

  // Mapbox Token
  mapbox_token = new ButtonControl(tr("Mapbox Token"), tr("Edit"), tr("Enter your Mapbox API token"));
  QObject::connect(mapbox_token, &ButtonControl::clicked, [=]() {
    QString current = QString::fromStdString(params.get("MapboxToken"));
    QString token = InputDialog::getText(tr("Enter Mapbox Token"), this, "", false, -1, current);
    if (!token.isEmpty()) {
      params.put("MapboxToken", token.toStdString());
      refresh();
    }
  });
  list->addItem(mapbox_token);

  // Mapbox Route
  mapbox_route = new ButtonControl(tr("Mapbox Route"), tr("Edit"), tr("Enter Mapbox route data"));
  QObject::connect(mapbox_route, &ButtonControl::clicked, [=]() {
    QString current = QString::fromStdString(params.get("MapboxRoute"));
    QString route = InputDialog::getText(tr("Enter Mapbox Route"), this, "", false, -1, current);
    if (!route.isEmpty()) {
      params.put("MapboxRoute", route.toStdString());
      refresh();
    }
  });
  list->addItem(mapbox_route);

  // Allow Navigation
  allow_navigation = new ParamControlSP("AllowNavigation", tr("Allow Navigation"), tr("Enable navigation features and start navigationd"), "", this);
  QObject::connect(allow_navigation, &ParamControlSP::toggleFlipped, this, &NavigationPanel::updateNavigationVisibility);
  list->addItem(allow_navigation);

  // Mapbox Recompute
  mapbox_recompute = new ParamControlSP("MapboxRecompute", tr("Mapbox Recompute"), tr("Enable automatic route recomputation"), "", this);
  list->addItem(mapbox_recompute);

  // Nav Allowed
  nav_allowed = new ParamControlSP("NavAllowed", tr("Navigation Allowed"), tr("Allow navigation features"), "", this);
  list->addItem(nav_allowed);

  // Nav Events
  nav_events = new ParamControlSP("NavEvents", tr("Navigation Events"), tr("Enable navigation event notifications"), "", this);
  list->addItem(nav_events);
}

void NavigationPanel::updateNavigationVisibility(bool state) {
  mapbox_recompute->setVisible(state);
  nav_allowed->setVisible(state);
  nav_events->setVisible(state);
}

void NavigationPanel::showEvent(QShowEvent *event) {
  refresh();
}

void NavigationPanel::refresh() {
  allow_navigation->refresh();

  bool nav_enabled = allow_navigation->isToggled();
  updateNavigationVisibility(nav_enabled);

  QString token = QString::fromStdString(params.get("MapboxToken"));
  mapbox_token->setValue(token.isEmpty() ? tr("Not set") : token);

  QString route = QString::fromStdString(params.get("MapboxRoute"));
  mapbox_route->setValue(route.isEmpty() ? tr("Not set") : route);

  mapbox_recompute->refresh();
  nav_allowed->refresh();
  nav_events->refresh();
}
