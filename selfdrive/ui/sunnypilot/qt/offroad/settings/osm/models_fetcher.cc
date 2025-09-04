/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/osm/models_fetcher.h"

#include <QThread>

ModelsFetcher::ModelsFetcher(QObject *parent) : QObject(parent) {
  manager = new QNetworkAccessManager(this);
}

QByteArray ModelsFetcher::verifyFileHash(const QString &filePath, const QString &expectedHash, bool &hashMatches) {
  hashMatches = false; // Default to false
  QByteArray fileData;

  if (expectedHash.isEmpty()) {
    // If no hash is provided, assume verification isn't required but return the file data
    hashMatches = true;
  } else {
    QFile file(filePath);
    if (file.open(QIODevice::ReadOnly)) {
      QCryptographicHash hash(QCryptographicHash::Sha256); // Or your chosen algorithm
      fileData = file.readAll(); // Read the file data once
      hash.addData(fileData);
      file.close();

      QString currentHash = QString(hash.result().toHex());
      hashMatches = (currentHash == expectedHash);
    }
  }

  // Return the file data if hash matches or no hash was provided; empty otherwise
  return hashMatches ? fileData : QByteArray();
}


void ModelsFetcher::download(const DownloadInfo &downloadInfo, const QString &filename, const QString &destinationPath) {
  QString fullPath = destinationPath + "/" + filename;
  QFileInfo fileInfo(fullPath);
  bool hashMatches = false;
  QByteArray data = verifyFileHash(fullPath, downloadInfo.sha256, hashMatches);

  if (fileInfo.exists() && hashMatches) {
    // Hash matches or no hash provided, and we have the file data
    LOGD("File already downloaded and verified: %s", filename.toStdString().c_str());
    emit downloadProgress(100);
    emit downloadComplete(data, true); // Use the data returned from verifyFileHash
    return; // Exit early
  }

  // Proceed with download if file does not exist or hash verification failed
  QNetworkRequest request(downloadInfo.url);
  QNetworkReply *reply = manager->get(request);
  connect(reply, &QNetworkReply::downloadProgress, this, &ModelsFetcher::onDownloadProgress);
  connect(reply, &QNetworkReply::finished, this, [this, reply, destinationPath, filename, downloadInfo]() {
    onFinished(reply, destinationPath, filename, downloadInfo.sha256);
  });
}

QString extractFileName(const QString &contentDisposition) {
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

void ModelsFetcher::onFinished(QNetworkReply *reply, const QString &destinationPath, const QString &filename, const QString &expectedHash) {
  // Handle download error
  if (reply->error()) {
    return; // Possibly emit a signal or log an error as per your error handling policy
  }

  const QByteArray data = reply->readAll();

  QString finalFilename = filename;
  if (finalFilename.isEmpty()) {
    finalFilename = extractFileName(reply->header(QNetworkRequest::ContentDispositionHeader).toString());
  }

  QString finalPath = QDir(destinationPath).filePath(finalFilename);

  // Save the downloaded file
  QFile file(finalPath);
  //ensure if the path exists and if not create it 
  if (!QDir().mkpath(destinationPath)) {
    LOGE("Unable to create directory: %s", destinationPath.toStdString().c_str());
    emit downloadFailed(filename);
    return; // Stop further processing
  }

  //Retry the file open and write 3 times with a little delay between each retry
  for (int i = 0; i < 3; i++) {
    if (file.isOpen()) break;

    file.open(QIODevice::WriteOnly);
    if (!file.isOpen()) QThread::msleep(100);
  }

  // If the file is still not open, log an error and emit a failure signal
  if (!file.isOpen()) {
    LOGE("Unable to open file for writing: %s", finalPath.toStdString().c_str());
    emit downloadFailed(filename);
    return; // Stop further processing
  }

  file.write(data);
  file.close();

  bool hashMatches = false;
  verifyFileHash(finalPath, expectedHash, hashMatches);

  // Verify the file hash if expectedHash is provided
  if (!expectedHash.isEmpty() && !hashMatches) {
    LOGE("The downloaded file didn't pass the hash validation!: %s", filename.toStdString().c_str());
    // Hash verification failed, handle accordingly
    // This could involve deleting the file, logging an error, or emitting a failure signal
    QFile::remove(finalPath); // Example action: Remove the invalid file
    emit downloadFailed(filename);
    return; // Stop further processing
  }

  emit downloadComplete(data, false); // Emit your success signal
}

void ModelsFetcher::onDownloadProgress(qint64 bytesReceived, qint64 bytesTotal) {
  const double progress = (bytesReceived * 100.0) / bytesTotal;
  emit downloadProgress(progress);
}

std::vector<Model> ModelsFetcher::getModelsFromURL(const QUrl &url) {
  std::vector<Model> models;
  JsonFetcher fetcher;
  QJsonObject json = fetcher.getJsonFromURL(url.toString());
  for (auto it = json.begin(); it != json.end(); ++it) {
    models.push_back(Model(it.value().toObject()));
  }
  return models;
}

std::vector<Model> ModelsFetcher::getModelsFromURL(const QString &url) {
  return getModelsFromURL(QUrl(url));
}

std::vector<Model> ModelsFetcher::getModelsFromURL() {
  return getModelsFromURL("https://docs.sunnypilot.ai/models_v5.json");
}
