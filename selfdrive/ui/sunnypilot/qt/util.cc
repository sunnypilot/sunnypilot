/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/util.h"
#include "selfdrive/ui/qt/util.h"

#include <string>
#include <vector>

#include <QDir>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLayoutItem>
#include <QPainterPath>
#include <QVariant>

#include "system/hardware/hw.h"

std::optional<QString> getParamIgnoringDefault(const std::string &param_name, const std::string &default_value) {
  std::string value = Params().get(param_name);

  if (!value.empty() && value != default_value)
    return QString::fromStdString(value);

  return {};
}

QString getUserAgent(bool sunnylink) {
  return (sunnylink ? "sunnypilot-" : "openpilot-") + getVersion();
}

std::optional<QString> getSunnylinkDongleId() {
  return getParamIgnoringDefault("SunnylinkDongleId", "UnregisteredDevice");
}

QMap<QString, QVariantMap> loadPlatformList() {
  QMap<QString, QVariantMap> _platforms;

  std::string json_data = util::read_file("../../sunnypilot/selfdrive/car/car_list.json");

  if (json_data.empty()) {
    return _platforms;
  }

  QJsonParseError json_error{};
  QJsonDocument doc = QJsonDocument::fromJson(QString::fromStdString(json_data).toUtf8(), &json_error);
  if (doc.isNull()) {
    return _platforms;
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
      platform_data["brand"] = attributes.value("brand").toString();
      platform_data["model"] = attributes.value("model").toString();
      platform_data["platform"] = attributes.value("platform").toString();
      platform_data["package"] = attributes.value("package").toString();

      _platforms[key] = platform_data;
    }
  }

  return _platforms;
}

/**
 * @brief Searches a list of strings for elements containing all search terms in a query.
 *
 * The search is case-insensitive and normalizes both the query and the list elements
 * using Unicode KD normalization before comparison.  Non-alphanumeric characters are
 * removed from the search terms before comparison.
 *
 * @param query The search query string.  Multiple words can be separated by spaces.
 * @param list The source list of strings to search.
 * @return A list of strings from the input list that contain all of the search terms.
 */
QStringList searchFromList(const QString &query, const QStringList &list) {
  if (query.isEmpty()) {
    return list;
  }

  QStringList search_terms = query.simplified().toLower().replace(QRegularExpression("[^a-zA-Z0-9\\s]"), " ").split(" ", QString::SkipEmptyParts);
  QStringList search_results;

  for (const QString &element : list) {
    if (std::all_of(search_terms.begin(), search_terms.end(), [&](const QString &term) {
          QString normalized_term = term.normalized(QString::NormalizationForm_KD).toLower();
          QString normalized_element = element.normalized(QString::NormalizationForm_KD).toLower();
          return normalized_element.contains(normalized_term, Qt::CaseInsensitive);
        })) {
      search_results << element;
    }
  }
  return search_results;
}

std::optional<cereal::Event::Reader> loadCerealEvent(Params& params, const std::string& _param) {
  std::string bytes = params.get(_param);

  try {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(bytes.data(), bytes.size()));
    return cmsg.getRoot<cereal::Event>();
  } catch (kj::Exception& e) {
    qInfo() << "invalid " << QString::fromStdString(_param) << ":" << e.getDescription().cStr();
    return std::nullopt;
  }
}

bool hasIntelligentCruiseButtonManagement(const cereal::CarParamsSP::Reader &car_params_sp) {
  return car_params_sp.getIntelligentCruiseButtonManagementAvailable() && Params().getBool("IntelligentCruiseButtonManagement");
}
