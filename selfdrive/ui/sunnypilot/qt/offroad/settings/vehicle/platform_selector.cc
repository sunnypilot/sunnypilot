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
        refresh(offroad);
      }
    } else {
      params.remove("CarPlatform");
      params.remove("CarPlatformName");
      refresh(offroad);
    }
  });

  refresh(offroad);
}

void PlatformSelector::refresh(bool _offroad) {
  QString platform_param = QString::fromStdString(params.get("CarPlatform"));
  if (platform_param.length()) {
    setValue(QString::fromStdString(params.get("CarPlatformName")));
    setText("REMOVE");
  } else {
    setValue("");
    setText("SEARCH");
  }
  setEnabled(true);

  offroad = _offroad;
}

QMap<QString, QVariantMap> PlatformSelector::loadPlatformList() {
  QMap<QString, QVariantMap> platforms;

  std::string json_data = util::read_file("../../sunnypilot/selfdrive/car/car_list.json").c_str();

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
      platform_data["make"] = attributes.value("make").toString();
      platform_data["model"] = attributes.value("model").toString();
      platform_data["platform"] = attributes.value("platform").toString();
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
  QStringList tokens = normalized_query.split(" ", QString::SkipEmptyParts);

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

    if (search_year != -1) {
      QVariantList year_list = platform_data["year"].toList();
      bool year_match = false;
      for (const QVariant &year_var : year_list) {
        int year = year_var.toString().toInt();
        if (year == search_year) {
          year_match = true;
          break;
        }
      }
      if (!year_match) continue;
    }

    QString normalized_make = platform_data["make"].toString().normalized(QString::NormalizationForm_KD).toLower();
    QString normalized_model = platform_data["model"].toString().normalized(QString::NormalizationForm_KD).toLower();
    normalized_make.remove(QRegExp("[^a-zA-Z0-9\\s]"));
    normalized_model.remove(QRegExp("[^a-zA-Z0-9\\s]"));

    bool all_terms_match = true;
    for (const QString &term : search_terms) {
      QString normalized_term = term.normalized(QString::NormalizationForm_KD).toLower();
      normalized_term.remove(QRegExp("[^a-zA-Z0-9\\s]"));

      bool term_matched = false;

      if (normalized_make.contains(normalized_term, Qt::CaseInsensitive)) {
        term_matched = true;
      }

      if (!term_matched) {
        if (term.contains(QRegExp("[a-z]\\d|\\d[a-z]", Qt::CaseInsensitive))) {
          QString clean_model = normalized_model;
          QString clean_term = normalized_term;
          clean_model.remove(" ");
          clean_term.remove(" ");
          if (clean_model.contains(clean_term, Qt::CaseInsensitive)) {
            term_matched = true;
          }
        } else {
          if (normalized_model.contains(normalized_term, Qt::CaseInsensitive)) {
            term_matched = true;
          }
        }
      }

      if (!term_matched) {
        all_terms_match = false;
        break;
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
    QVariantMap platform_data = platforms[selected_platform];

    const QString offroad_msg = offroad ? tr("This setting will take effect immediately.") :
                                          tr("This setting will take effect once the device enters offroad state.");
    const QString msg = QString("<b>%1</b><br><br>%2")
                        .arg(selected_platform)
                        .arg(offroad_msg);

    QString content("<body><h2 style=\"text-align: center;\">" + tr("Vehicle Selector") + "</h2><br>"
                    "<p style=\"text-align: center; margin: 0 128px; font-size: 50px;\">" + msg + "</p></body>");

    if (ConfirmationDialog(content, tr("Confirm"), tr("Cancel"), true, this).exec()) {
      params.put("CarPlatform", platform_data["platform"].toString().toStdString());
      params.put("CarPlatformName", selected_platform.toStdString());
    }
  }
}
