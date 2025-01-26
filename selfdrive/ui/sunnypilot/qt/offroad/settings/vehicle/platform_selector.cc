/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/platform_selector.h"

#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonValue>
#include <QMap>

PlatformSelector::PlatformSelector() : ButtonControl(tr("Vehicle"), "", "") {
  QObject::connect(this, &ButtonControl::clicked, [=]() {
    if (text() == tr("SEARCH")) {
      QString query = InputDialog::getText(tr("Search your vehicle"), this, tr("Enter model year (e.g., 2021) and model name (Toyota Corolla):"), false);
      if (query.length() > 0) {
        setText(tr("SEARCHING"));
        setEnabled(false);
        searchPlatforms(query);
        refresh();
      }
    } else {
      params.remove("CarPlatform");
      params.remove("CarPlatformName");
      refresh();
    }
  });

  refresh();
}

void PlatformSelector::refresh() {
  QString platform_param = QString::fromStdString(params.get("CarPlatform"));
  if (platform_param.length()) {
    setValue(QString::fromStdString(params.get("CarPlatformName")));
    setText("REMOVE");
  } else {
    setValue("");
    setText("SEARCH");
  }
  setEnabled(true);
}

QMap<QString, QVariantMap> PlatformSelector::loadPlatformList() {
  QMap<QString, QVariantMap> platforms;

  std::string json_data = util::read_file("../../sunnypilot/selfdrive/car/car_list_extra.json").c_str();

  if (json_data.empty()) {
    return platforms;
  }

  QJsonParseError json_error;
  QJsonDocument doc = QJsonDocument::fromJson(QString::fromStdString(json_data).toUtf8(), &json_error);
  if (doc.isNull()) {
    return platforms;
  }

  if (doc.isObject()) {
    QJsonObject obj = doc.object();
    for (const QString &key : obj.keys()) {
      QJsonObject attributes = obj.value(key).toObject();
      QVariantMap platform_data;

      QJsonArray yearArray = attributes.value("year").toArray();
      QVariantList yearList;
      for (const QJsonValue &year : yearArray) {
        yearList.append(year.toString());
      }

      platform_data["year"] = yearList;
      platform_data["model"] = attributes.value("model").toString();
      platform_data["package"] = attributes.value("package").toString();

      platforms[key] = platform_data;
    }
  }

  return platforms;
}

void PlatformSelector::searchPlatforms(const QString &query) {
  if (query.isEmpty()) {
    return;
  }

  QMap<QString, QVariantMap> platforms = loadPlatformList();
  QSet<QString> matched_cars;

  QString normalized_query = query.simplified().toLower();
  QStringList tokens = normalized_query.split(" ", Qt::SkipEmptyParts);

  int search_year = -1;
  QStringList search_terms;

  for (const QString &token : tokens) {
    bool ok;
    int year = token.toInt(&ok);
    if (ok && year >= 1900 && year <= 2100) {
      search_year = year;
    } else {
      search_terms << token;
    }
  }

  for (auto it = platforms.constBegin(); it != platforms.constEnd(); ++it) {
    QString platform_name = it.key();
    QVariantMap platform_data = it.value();
    QVariantList year_list = platform_data["year"].toList();

    if (search_year != -1) {
      bool year_match = false;
      for (const QVariant &year_var : year_list) {
        int year = year_var.toString().toInt();
        if (year == search_year) {
          year_match = true;
          break;
        }
      }
      if (!year_match) {
        continue;
      }
    }

    bool all_terms_match = true;
    QString platform_search = platform_name.toLower();

    // Normalize platform name for searching (remove diacritical marks)
    QString normalized_platform = platform_search.normalized(QString::NormalizationForm_KD);
    normalized_platform.remove(QRegExp("[^a-zA-Z0-9\\s]"));

    for (const QString &term : search_terms) {
      QString normalized_term = term.normalized(QString::NormalizationForm_KD);
      normalized_term.remove(QRegExp("[^a-zA-Z0-9\\s]"));

      if (term.contains(QRegExp("[a-z]\\d|\\d[a-z]", Qt::CaseInsensitive))) {
        QString clean_platform = normalized_platform;
        QString clean_term = normalized_term;
        clean_platform.remove(" ");
        clean_term.remove(" ");
        if (!clean_platform.contains(clean_term, Qt::CaseInsensitive)) {
          all_terms_match = false;
          break;
        }
      } else {
        QRegExp wordMatch(QString("\\b%1\\b").arg(QRegExp::escape(normalized_term)), Qt::CaseInsensitive);
        if (!normalized_platform.contains(wordMatch)) {
          all_terms_match = false;
          break;
        }
      }
    }

    if (all_terms_match) {
      matched_cars.insert(platform_name);
    }
  }

  QStringList results = QStringList(matched_cars.begin(), matched_cars.end());
  results.sort();

  if (results.isEmpty()) {
    ConfirmationDialog::alert(tr("No vehicles found for query: %1").arg(query), this);
    return;
  }

  QString selected_platform = MultiOptionDialog::getSelection(tr("Select a vehicle"), results, "", this);

  if (!selected_platform.isEmpty()) {
    params.put("CarPlatform", selected_platform.toStdString());
    params.put("CarPlatformName", selected_platform.toStdString());
  }
}
