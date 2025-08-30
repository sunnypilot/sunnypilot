/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <algorithm>  // for std::sort
#include <cassert>
#include <deque>
#include <vector>

#include <QDir>
#include <QJsonObject>
#include <QTimer>

#include "common/swaglog.h"
#include "common/util.h"
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/sunnypilot/qt/common/json_fetcher.h"
#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#else
#include "selfdrive/ui/qt/widgets/controls.h"
#endif
#include "system/hardware/hw.h"

static const QString MODELS_PATH = Hardware::PC() ? QDir::homePath() + "/.comma/media/0/models/" : "/data/media/0/models/";

struct DownloadInfo {
  QString url;
  QString sha256;
};

// New class ModelsFetcher with a new function that handles web requests and JSON parsing for the new JSON structure
class Model {
public:
  explicit Model(const QJsonObject &json) {
    displayName = json["display_name"].toString();
    fullName = json["full_name"].toString();
    fileName = json["file_name"].toString();

    // Parse downloadUri as an object
    QJsonObject downloadUriObj = json["download_uri"].toObject();
    downloadUri.url = downloadUriObj["url"].toString();
    downloadUri.sha256 = downloadUriObj["sha256"].toString();

    fullNameNav = json["full_name_nav"].toString();
    fileNameNav = json["file_name_nav"].toString();

    // Parse downloadUriNav as an object
    QJsonObject downloadUriNavObj = json["download_uri_nav"].toObject();
    downloadUriNav.url = downloadUriNavObj["url"].toString();
    downloadUriNav.sha256 = downloadUriNavObj["sha256"].toString();

    fullNameMetadata = json["full_name_metadata"].toString();
    fileNameMetadata = json["file_name_metadata"].toString();

    // Parse downloadUriMetadata as an object
    QJsonObject downloadUriMetadataObj = json["download_uri_metadata"].toObject();
    downloadUriMetadata.url = downloadUriMetadataObj["url"].toString();
    downloadUriMetadata.sha256 = downloadUriMetadataObj["sha256"].toString();

    index = json["index"].toString();
    environment = json["environment"].toString();
    generation = json["generation"].toString();
  }

  // Method to convert model back to QJsonObject, if needed
  QJsonObject toJson() const {
    QJsonObject json;
    json["display_name"] = displayName;
    json["full_name"] = fullName;
    json["file_name"] = fileName;

    QJsonObject uriObj;
    uriObj["url"] = downloadUri.url;
    uriObj["sha256"] = downloadUri.sha256;
    json["download_uri"] = uriObj;

    QJsonObject uriNavObj;
    uriNavObj["url"] = downloadUriNav.url;
    uriNavObj["sha256"] = downloadUriNav.sha256;
    json["download_uri_nav"] = uriNavObj;

    QJsonObject uriMetadataObj;
    uriMetadataObj["url"] = downloadUriMetadata.url;
    uriMetadataObj["sha256"] = downloadUriMetadata.sha256;
    json["download_uri_metadata"] = uriMetadataObj;

    json["full_name_nav"] = fullNameNav;
    json["file_name_nav"] = fileNameNav;
    json["full_name_metadata"] = fullNameMetadata;
    json["file_name_metadata"] = fileNameMetadata;
    json["index"] = index;
    json["environment"] = environment;
    json["generation"] = generation;
    return json;
  }

  QString displayName;
  QString fullName;
  QString fileName;
  DownloadInfo downloadUri;
  DownloadInfo downloadUriNav;
  DownloadInfo downloadUriMetadata;

  QString fullNameNav;
  QString fileNameNav;
  QString fullNameMetadata;
  QString fileNameMetadata;
  QString index;
  QString environment;
  QString generation;
};

class ModelsFetcher : public QObject {
  Q_OBJECT

public:
  explicit ModelsFetcher(QObject *parent = nullptr);
  void download(const DownloadInfo &url, const QString &filename = "", const QString &destinationPath = MODELS_PATH);
  static std::vector<Model> getModelsFromURL(const QUrl &url);
  static std::vector<Model> getModelsFromURL(const QString &url);
  static std::vector<Model> getModelsFromURL();

signals:
  void downloadProgress(double percentage);
  void downloadComplete(const QByteArray &data, bool fromCache = false);
  void downloadFailed(const QString &filename);

private:
  //  static bool verifyFileHash(const QString& filePath, const QString& expectedHash);
  static QByteArray verifyFileHash(const QString &filePath, const QString &expectedHash, bool &hashMatches);
  void onDownloadProgress(qint64 bytesReceived, qint64 bytesTotal);
  void onFinished(QNetworkReply *reply, const QString &destinationPath, const QString &filename,
                  const QString &expectedHash);

  QNetworkAccessManager *manager;
};
