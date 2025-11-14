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
  mapbox_token = new ButtonControl(tr("Mapbox token"), tr("Edit"), tr("Enter your mapbox public token"));
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
  mapbox_route = new ButtonControl(tr("Mapbox route"), tr("Edit"), tr(""));
  QObject::connect(mapbox_route, &ButtonControl::clicked, [=]() {
    QString current = QString::fromStdString(params.get("MapboxRoute"));
    QString route = InputDialog::getText(tr("Enter Mapbox Route"), this, "", false, -1, current);
    if (!route.isEmpty()) {
      params.put("MapboxRoute", route.toStdString());
      refresh();
    }
  });
  list->addItem(mapbox_route);

  // Clear Route
  clear_route = new ButtonControl(tr("Clear current route"), tr("Clear"), tr(""));
  QObject::connect(clear_route, &ButtonControl::clicked, [=]() {
    params.remove("MapboxRoute");
    refresh();
  });
  list->addItem(clear_route);

  // Favs selector
  favorites_selector = new MultiButtonControlSP("Favorites", "Select favorite route", "", {"Home", "Work", "Favs"}, 470);
  QObject::connect(favorites_selector, &MultiButtonControlSP::buttonClicked, [=](int id) {
    QString favs_str = QString::fromStdString(params.get("MapboxFavorites"));
    QJsonDocument doc = QJsonDocument::fromJson(favs_str.toUtf8());
    QJsonObject obj = doc.object();
    QString route;
    if (id == 0) route = obj["home"].toString();
    else if (id == 1) route = obj["work"].toString();
    else if (id == 2) {
      QJsonObject favorites_obj = obj["favorites"].toObject();
      if (favorites_obj.isEmpty()) {
        ConfirmationDialog::alert(tr("No custom favorites set"), this);
        return;
      }
      QStringList favNames = favorites_obj.keys();
      const QString selected = MultiOptionDialog::getSelection(tr("Select Favorite"), favNames, "", this);
      if (!selected.isEmpty()) {
        route = favorites_obj[selected].toString();
      }
    }
    if (!route.isEmpty()) {
      params.put("MapboxRoute", route.toStdString());
      refresh();
    }
  });
  list->addItem(favorites_selector);

  struct FavInfo {
    QString key;
    QString title;
    QString desc;
  };
  std::vector<FavInfo> favs = {
    {"home", tr("Set Home"), tr("")},
    {"work", tr("Set Work"), tr("")}
  };
  set_buttons.resize(favs.size());
  for (size_t i = 0; i < favs.size(); ++i) {
    const auto& fav = favs[i];
    set_buttons[i] = new ButtonControl(fav.title, tr("Set"), fav.desc);
    QObject::connect(set_buttons[i], &ButtonControl::clicked, [this, fav]() {
      QString favs_str = QString::fromStdString(params.get("MapboxFavorites"));
      QJsonDocument doc = QJsonDocument::fromJson(favs_str.toUtf8());
      QJsonObject obj = doc.object();
      QString current = obj[fav.key].toString();
      QString route = InputDialog::getText(tr("Set %1 Route").arg(fav.title.mid(4)), this, "", false, -1, current);  // mid(4) to remove "Set "
      if (!route.isEmpty()) {
        obj[fav.key] = route;
        QJsonDocument new_doc(obj);
        params.put("MapboxFavorites", new_doc.toJson(QJsonDocument::Compact).toStdString());
        refresh();
      }
    });
    list->addItem(set_buttons[i]);
  }

  add_fav = new ButtonControl(tr("Add Favorite"), tr("Add"), tr("Add a new custom favorite"));
  QObject::connect(add_fav, &ButtonControl::clicked, [=]() {
    QString name = InputDialog::getText(tr("Favorite Name"), this, "", false, -1, "");
    if (name.isEmpty()) return;

    QString route = InputDialog::getText(tr("Favorite Route"), this, "", false, -1, "");
    if (route.isEmpty()) return;

    QString favs_str = QString::fromStdString(params.get("MapboxFavorites"));
    QJsonDocument doc = QJsonDocument::fromJson(favs_str.toUtf8());
    QJsonObject obj = doc.object();
    QJsonObject favorites_obj = obj["favorites"].toObject();
    favorites_obj[name] = route;
    obj["favorites"] = favorites_obj;
    QJsonDocument new_doc(obj);
    params.put("MapboxFavorites", new_doc.toJson(QJsonDocument::Compact).toStdString());
    refresh();
  });
  list->addItem(add_fav);

  remove_fav = new ButtonControl(tr("Remove Favorite"), tr("Remove"), tr("Remove a custom favorite"));
  QObject::connect(remove_fav, &ButtonControl::clicked, [=]() {
    QString favs_str = QString::fromStdString(params.get("MapboxFavorites"));
    QJsonDocument doc = QJsonDocument::fromJson(favs_str.toUtf8());
    QJsonObject obj = doc.object();
    QJsonObject favorites_obj = obj["favorites"].toObject();
    if (favorites_obj.isEmpty()) {
      ConfirmationDialog::alert(tr("No custom favorites to remove"), this);
      return;
    }
    QStringList favNames = favorites_obj.keys();
    const QString selected = MultiOptionDialog::getSelection(tr("Remove Favorite"), favNames, "", this);
    if (!selected.isEmpty()) {
      favorites_obj.remove(selected);
      obj["favorites"] = favorites_obj;
      QJsonDocument new_doc(obj);
      params.put("MapboxFavorites", new_doc.toJson(QJsonDocument::Compact).toStdString());
      refresh();
    }
  });
  list->addItem(remove_fav);

  // Dumb params
  allow_navigation = new ParamControlSP("AllowNavigation", tr("Allow navigation"), tr("Enable navigation features and start navigationd"), "", this);
  QObject::connect(allow_navigation, &ParamControlSP::toggleFlipped, this, &NavigationPanel::updateNavigationVisibility);
  list->addItem(allow_navigation);

  mapbox_recompute = new ParamControlSP("MapboxRecompute", tr("Mapbox recompute"), tr("Enable automatic route recomputation"), "", this);
  list->addItem(mapbox_recompute);

  nav_allowed = new ParamControlSP("NavDesiresAllowed", tr("Navigation allowed"), tr("Allow navigation to automatically take turns"), "", this);
  list->addItem(nav_allowed);
}

void NavigationPanel::updateNavigationVisibility(bool state) {
  mapbox_recompute->setVisible(state);
  nav_allowed->setVisible(state);
  favorites_selector->setVisible(state);
  for (auto btn : set_buttons) {
    btn->setVisible(state);
  }
  add_fav->setVisible(state);
  remove_fav->setVisible(state);
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
}
