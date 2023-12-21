#include "selfdrive/ui/qt/offroad/sunnypilot/models_fetcher.h"

ModelsFetcher::ModelsFetcher(QObject* parent) : QObject(parent) {
  manager = new QNetworkAccessManager(this);
}

void ModelsFetcher::download(const QUrl& url, const QString& filename, const QString& destinationPath) {
  if (!QDir(destinationPath).exists() && !QDir().mkpath(destinationPath)) {
    LOGE("Failed to create directory: [%s]", destinationPath.toStdString().c_str());
  }
  const QNetworkRequest request(url);
  QNetworkReply* reply = manager->get(request);
  connect(reply, &QNetworkReply::downloadProgress, this, &ModelsFetcher::onDownloadProgress);
  connect(reply, &QNetworkReply::finished, this, [this, reply, destinationPath, filename]() {
    onFinished(reply, destinationPath, filename);
  });
}

QString extractFileName(const QString& contentDisposition) {
  const QString filenameTag = "filename=";
  const int idx = contentDisposition.indexOf(filenameTag);
  if (idx < 0) {
    return QString();
  }

  QString filename = contentDisposition.mid(idx + filenameTag.length());
  if (filename.startsWith("\"") && filename.endsWith("\"")) {
    return filename.mid(1, filename.size() - 2);
  }

  return filename;
}

void ModelsFetcher::onFinished(QNetworkReply* reply, const QString& destinationPath, const QString& filename) {
  // Handle download error
  if (reply->error()) {
    return;
  }

  const QByteArray data = reply->readAll();

  QString finalFilename = filename;
  if (finalFilename.isEmpty()) {
    finalFilename = extractFileName(reply->header(QNetworkRequest::ContentDispositionHeader).toString());
  }

  QString finalPath = QDir(destinationPath).filePath(finalFilename);

  // handle file open error
  QFile file(finalPath);
  if (!file.open(QIODevice::WriteOnly)) {
    return;
  }

  file.write(data);
  file.close();

  emit downloadComplete(data);
}

void ModelsFetcher::onDownloadProgress(qint64 bytesReceived, qint64 bytesTotal) {
  const double progress = (bytesReceived * 100.0) / bytesTotal;
  emit downloadProgress(progress);
}

std::vector<Model> ModelsFetcher::getModelsFromURL(const QUrl&url) {
  std::vector<Model> models;
  JsonFetcher fetcher;
  QJsonObject json = fetcher.getJsonFromURL(url.toString());
  for (auto it = json.begin(); it != json.end(); ++it) {
    models.push_back(Model(it.value().toObject()));
  }
  return models;
}

std::vector<Model> ModelsFetcher::getModelsFromURL(const QString&url) {
  return getModelsFromURL(QUrl(url));
}

std::vector<Model> ModelsFetcher::getModelsFromURL() {
  return getModelsFromURL("https://docs.sunnypilot.ai/models.json");
}
