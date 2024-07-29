/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

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
  inline std::vector<std::tuple<QString, QString, QString, QString>>
  getLocationsFromURL(const QUrl &url, const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    // Initialize an empty vector to hold the locations
    std::vector<std::tuple<QString, QString, QString, QString>> locations;

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
      return std::get < 0 > (lhs) < std::get < 0 > (rhs);  // Compare full names
    });
    // Optionally, you can now add defaultName entry at the beginning
    locations.insert(locations.begin(), std::tuple_cat(customLocation, std::make_tuple("", "")));
    return locations;
  }

  inline std::vector<std::tuple<QString, QString, QString, QString>>
  getLocationsFromURL(const QString &url, const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    return getLocationsFromURL(QUrl(url), customLocation);
  }

  inline std::vector<std::tuple<QString, QString, QString, QString>>
  getOsmLocations(const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    return getLocationsFromURL("https://raw.githubusercontent.com/pfeiferj/openpilot-mapd/main/nation_bounding_boxes.json", customLocation);
  }

  inline std::vector<std::tuple<QString, QString, QString, QString>>
  getUsStatesLocations(const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    return getLocationsFromURL("https://raw.githubusercontent.com/pfeiferj/openpilot-mapd/main/us_states_bounding_boxes.json", customLocation);
  }
};
