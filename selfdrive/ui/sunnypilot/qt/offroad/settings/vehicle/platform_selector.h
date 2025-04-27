/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <QJsonDocument>

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"

class PlatformSelector : public ButtonControl {
  Q_OBJECT

public:
  PlatformSelector();
  static QVariant getPlatformBundle(const QString &key) {
    QString platform_bundle = QString::fromStdString(Params().get("CarPlatformBundle"));
    if (!platform_bundle.isEmpty()) {
      QJsonDocument json = QJsonDocument::fromJson(platform_bundle.toUtf8());
      if (!json.isNull() && json.isObject()) {
        return json.object().value(key).toVariant();
      }
    }
    return {};
}

public slots:
  void refresh(bool _offroad);

private:
  void searchPlatforms(const QString &query);
  void setPlatform(const QString &platform = "");
  QMap<QString, QVariantMap> platforms;

  Params params;
  bool offroad;
};
