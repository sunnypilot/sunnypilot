#pragma once

#include <QJsonObject>
#include <QNetworkReply>
#include <QString>
#include <QTimer>

#include "common/util.h"

namespace CommaApi {

const QString BASE_URL = util::getenv("API_HOST", "https://api.commadotai.com").c_str();
QByteArray rsa_sign(const QByteArray &data);
QByteArray rsa_encrypt(const QByteArray &data);
QByteArray rsa_decrypt(const QByteArray &data);
QString create_jwt(const QJsonObject &payloads = {}, int expiry = 3600, bool sunnylink = false);

}  // namespace CommaApi

/**
 * Makes a request to the request endpoint.
 */

class HttpRequest : public QObject {
  Q_OBJECT

public:
  enum class Method {GET, DELETE, POST, PUT};

  explicit HttpRequest(QObject* parent, bool create_jwt = true, int timeout = 20000, const bool sunnylink = false);
  void sendRequest(const QString &requestURL, const Method method = Method::GET, const QByteArray &payload = {});
  bool active() const;
  bool timeout() const;

signals:
  void requestDone(const QString &response, bool success, QNetworkReply::NetworkError error);

protected:
  QNetworkReply *reply = nullptr;

private:
  static QNetworkAccessManager *nam();
  QTimer *networkTimer = nullptr;
  bool create_jwt;
  bool sunnylink;

private slots:
  void requestTimeout();
  void requestFinished();
};
