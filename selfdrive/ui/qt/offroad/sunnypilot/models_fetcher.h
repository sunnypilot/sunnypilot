#pragma once

#include <algorithm>  // for std::sort
#include <cassert>
#include <deque>
#include <QDir>
#include <QJsonObject>
#include <QTimer>

#include "common/swaglog.h"
#include "common/util.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/offroad/sunnypilot/json_fetcher.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "system/hardware/hw.h"

static const QString MODELS_PATH = Hardware::PC() ? QDir::homePath() + "/.comma/media/0/models/" : "/data/media/0/models/";

// New class ModelsFetcher with a new function that handles web requests and JSON parsing for the new JSON structure
class Model {

public:
  explicit Model(const QJsonObject&json) {
    displayName = json["display_name"].toString();
    fullName = json["full_name"].toString();
    fileName = json["file_name"].toString();
    downloadUri = json["download_uri"].toString();
    fullNameNav = json["full_name_nav"].toString();
    fileNameNav = json["file_name_nav"].toString();
    downloadUriNav = json["download_uri_nav"].toString();
    fullNameMetadata = json["full_name_metadata"].toString();
    fileNameMetadata = json["file_name_metadata"].toString();
    downloadUriMetadata = json["download_uri_metadata"].toString();
    index = json["index"].toString();
    environment = json["environment"].toString();
    generation = json["generation"].toString();
  }

  QJsonObject toJson() const {
    QJsonObject json;
    json["display_name"] = displayName;
    json["full_name"] = fullName;
    json["file_name"] = fileName;
    json["download_uri"] = downloadUri;
    json["full_name_nav"] = fullNameNav;
    json["file_name_nav"] = fileNameNav;
    json["download_uri_nav"] = downloadUriNav;
    json["full_name_metadata"] = fullNameMetadata;
    json["file_name_metadata"] = fileNameMetadata;
    json["download_uri_metadata"] = downloadUriMetadata;
    json["index"] = index;
    json["environment"] = environment;
    json["generation"] = generation;
    return json;
  }

  QString displayName;
  QString fullName;
  QString fileName;
  QString downloadUri;
  QString fullNameNav;
  QString fileNameNav;
  QString downloadUriNav;
  QString index;
  QString environment;
  QString generation;
  QString fullNameMetadata;
  QString fileNameMetadata;
  QString downloadUriMetadata;
};

class ModelsFetcher : public QObject {
  Q_OBJECT

public:
  explicit ModelsFetcher(QObject* parent = nullptr);
  void download(const QUrl&url, const QString& filename = "", const QString&destinationPath = MODELS_PATH);
  static std::vector<Model> getModelsFromURL(const QUrl&url);
  static std::vector<Model> getModelsFromURL(const QString&url);
  static std::vector<Model> getModelsFromURL();

signals:
  void downloadProgress(double percentage);
  void downloadComplete(const QByteArray&data);

private:
  void onDownloadProgress(qint64 bytesReceived, qint64 bytesTotal);
  void onFinished(QNetworkReply* reply, const QString&destinationPath, const QString&filename);

  QNetworkAccessManager* manager;
};
