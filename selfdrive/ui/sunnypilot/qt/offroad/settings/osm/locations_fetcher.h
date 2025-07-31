/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <algorithm>  // for std::sort
#include <deque>
#include <vector>
#include <tuple>

#include <QDir>
#include <QJsonObject>

#include "selfdrive/ui/sunnypilot/qt/common/json_fetcher.h"

static const std::tuple<QString, QString> defaultLocation = std::make_tuple("== None ==", "");

// New class LocationsFetcher that handles web requests and JSON parsing
class LocationsFetcher {
public:
  inline std::vector<std::tuple<QString, QString, QString, QString> >
  getLocationsFromURL(const QUrl &url, const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    // Initialize an empty vector to hold the locations
    std::vector<std::tuple<QString, QString, QString, QString> > locations;

    JsonFetcher fetcher;
    QJsonObject json = fetcher.getJsonFromURL(url.toString());

    for (auto it = json.begin(); it != json.end(); ++it) {
      QString code = it.key();
      QJsonObject obj = it.value().toObject();
      QString fullName = obj["full_name"].toString();

      locations.push_back(std::make_tuple(fullName, code, QString(), QString()));
    }
    // Sort locations by full name
    std::sort(locations.begin(), locations.end(), [](const auto &lhs, const auto &rhs) {
      return std::get<0>(lhs) < std::get<0>(rhs); // Compare full names
    });
    // Optionally, you can now add defaultName entry at the beginning
    locations.insert(locations.begin(), std::tuple_cat(customLocation, std::make_tuple("", "")));
    return locations;
  }

  inline std::vector<std::tuple<QString, QString, QString, QString> >
  getLocationsFromURL(const QString &url, const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    return getLocationsFromURL(QUrl(url), customLocation);
  }

  inline std::vector<std::tuple<QString, QString, QString, QString> >
  getOsmLocations(const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    return getLocationsFromURL( "https://raw.githubusercontent.com/pfeiferj/openpilot-mapd/main/nation_bounding_boxes.json", customLocation);
  }

  inline std::vector<std::tuple<QString, QString, QString, QString> >
  getUsStatesLocations(const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    return getLocationsFromURL( "https://raw.githubusercontent.com/pfeiferj/openpilot-mapd/main/us_states_bounding_boxes.json", customLocation);
  }
};
