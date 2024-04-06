#include "selfdrive/ui/qt/api.h"

#include <openssl/bio.h>
#include <openssl/pem.h>
#include <openssl/rsa.h>
#include <openssl/aes.h>

#include <QApplication>
#include <QCryptographicHash>
#include <QDateTime>
#include <QDebug>
#include <QFile>
#include <QJsonDocument>
#include <QNetworkRequest>
#include <QSsl>

#include <string>

#include "common/params.h"
#include "common/util.h"
#include "system/hardware/hw.h"
#include "selfdrive/ui/qt/util.h"

namespace CommaApi {

QByteArray rsa_sign(const QByteArray &data) {
  static std::string key = util::read_file(Path::rsa_file());
  if (key.empty()) {
    qDebug() << "No RSA private key found, please run manager.py or registration.py";
    return {};
  }

  BIO* mem = BIO_new_mem_buf(key.data(), key.size());
  assert(mem);
  RSA* rsa_private = PEM_read_bio_RSAPrivateKey(mem, NULL, NULL, NULL);
  assert(rsa_private);
  auto sig = QByteArray();
  sig.resize(RSA_size(rsa_private));
  unsigned int sig_len;
  int ret = RSA_sign(NID_sha256, (unsigned char*)data.data(), data.size(), (unsigned char*)sig.data(), &sig_len, rsa_private);
  assert(ret == 1);
  assert(sig_len == sig.size());
  BIO_free(mem);
  RSA_free(rsa_private);
  return sig;
}

void derive_aes_key_iv_from_rsa(EVP_PKEY *rsa_key, unsigned char *aes_key, unsigned char *aes_iv) {
  unsigned char hash[SHA256_DIGEST_LENGTH];
  size_t pub_len;
  unsigned char *pub_key;

  // Convert RSA key to public key in DER format for simplicity
  pub_len = i2d_PublicKey(rsa_key, NULL);
  pub_key = (unsigned char *)malloc(pub_len);
  unsigned char *tmp = pub_key;
  i2d_PublicKey(rsa_key, &tmp);

  // Hash the public key to derive bytes for AES key and IV
  SHA256(pub_key, pub_len, hash);

  // Assuming AES-256-CBC, we need 32 bytes for the key and 16 for the IV
  memcpy(aes_key, hash, 32); // First 32 bytes for AES key
  memcpy(aes_iv, hash + 32 - 16, 16); // Last 16 bytes for AES IV

  free(pub_key);
}

EVP_PKEY *load_public_key(const char *file) {
  EVP_PKEY *key = NULL;
  FILE *fp = fopen(file, "r");
  if (fp) {
    key = PEM_read_PUBKEY(fp, NULL, NULL, NULL);
    fclose(fp);
  }
  return key;
}

EVP_PKEY *load_private_key(const char *file) {
  EVP_PKEY *key = NULL;
  FILE *fp = fopen(file, "r");
  if (fp) {
    key = PEM_read_PrivateKey(fp, NULL, NULL, NULL);
    fclose(fp);
  }
  return key;
}

QByteArray rsa_encrypt(const QByteArray &data) {
  EVP_PKEY *rsa_key = load_public_key(Path::rsa_pub_file().c_str()); // Load your RSA key
  unsigned char aes_key[32], aes_iv[16];
  derive_aes_key_iv_from_rsa(rsa_key, aes_key, aes_iv);

  EVP_CIPHER_CTX *ctx;
  if (!(ctx = EVP_CIPHER_CTX_new())) {
    // Handle error: Allocate memory failed
    return {};
  }

  if (EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, aes_key, aes_iv) != 1) {
    qDebug() << "Failed to initialize encryption";
    EVP_CIPHER_CTX_free(ctx);
    return {};
  }

  int ciphertext_len;
  int len = data.size();
  unsigned char out[len + AES_BLOCK_SIZE];
  auto *in = (unsigned char*) data.constData();
  if (EVP_EncryptUpdate(ctx, out, &ciphertext_len, in, len) != 1) {
    qDebug() << "Failed to update encryption";
    EVP_CIPHER_CTX_free(ctx);
    return {};
  }

  if (EVP_EncryptFinal_ex(ctx, out + ciphertext_len, &len) != 1) {
    // Handle error: Encryption finalize failed
    qDebug() << "Failed to finalize encryption";
    EVP_CIPHER_CTX_free(ctx);
    return {};
  }

  //qDebug() << "Encrypted data length: %d", ciphertext_len + len;  // Print the length of encrypted data
  EVP_CIPHER_CTX_free(ctx);
  return {reinterpret_cast<char*>(out), ciphertext_len + len};
}

QByteArray rsa_decrypt(const QByteArray &data) {
  EVP_PKEY *rsa_key = load_public_key(Path::rsa_pub_file().c_str());  // Load your RSA key
  unsigned char aes_key[32], aes_iv[16];
  derive_aes_key_iv_from_rsa(rsa_key, aes_key, aes_iv);

  EVP_CIPHER_CTX *ctx;
  if (!(ctx = EVP_CIPHER_CTX_new())) {
    qDebug() << "Failed to allocate memory for EVP_CIPHER_CTX";
    return {};
  }

  if (EVP_DecryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, aes_key, aes_iv) != 1) {
    qDebug() << "Failed to initialize EVP";
    EVP_CIPHER_CTX_free(ctx);
    return {};
  }

  int len = data.size();
  unsigned char out[len + AES_BLOCK_SIZE];
  auto *in = (unsigned char*) data.constData();
  if (EVP_DecryptUpdate(ctx, out, &len, in, len) != 1) {
    qDebug() << "Failed to update decryption";
    EVP_CIPHER_CTX_free(ctx);
    return {};
  }

  int final_len;
  if (EVP_DecryptFinal_ex(ctx, out + len, &final_len) != 1) {
    qDebug() << "Failed to finalize decryption";
    EVP_CIPHER_CTX_free(ctx);
    return {};
  }
  EVP_CIPHER_CTX_free(ctx);

  //qDebug() << "Decrypted data length: %d", len + final_len;  // Print the length of decrypted data
  return {reinterpret_cast<char*>(out), len + final_len};
}

QString create_jwt(const QJsonObject &payloads, int expiry, bool sunnylink) {
  QJsonObject header = {{"alg", "RS256"}};

  auto t = QDateTime::currentSecsSinceEpoch();
  auto dongle_id = sunnylink ? getSunnylinkDongleId() : getDongleId();
  QJsonObject payload = {{"identity", dongle_id.value_or("")}, {"nbf", t}, {"iat", t}, {"exp", t + expiry}};
  for (auto it = payloads.begin(); it != payloads.end(); ++it) {
    payload.insert(it.key(), it.value());
  }

  auto b64_opts = QByteArray::Base64UrlEncoding | QByteArray::OmitTrailingEquals;
  QString jwt = QJsonDocument(header).toJson(QJsonDocument::Compact).toBase64(b64_opts) + '.' +
                QJsonDocument(payload).toJson(QJsonDocument::Compact).toBase64(b64_opts);

  auto hash = QCryptographicHash::hash(jwt.toUtf8(), QCryptographicHash::Sha256);
  auto sig = rsa_sign(hash);
  jwt += '.' + sig.toBase64(b64_opts);
  return jwt;
}

}  // namespace CommaApi

HttpRequest::HttpRequest(QObject *parent, bool create_jwt, int timeout, const bool sunnylink) : create_jwt(create_jwt), sunnylink(sunnylink), QObject(parent) {
  networkTimer = new QTimer(this);
  networkTimer->setSingleShot(true);
  networkTimer->setInterval(timeout);
  connect(networkTimer, &QTimer::timeout, this, &HttpRequest::requestTimeout);
}

bool HttpRequest::active() const {
  return reply != nullptr;
}

bool HttpRequest::timeout() const {
  return reply && reply->error() == QNetworkReply::OperationCanceledError;
}

void HttpRequest::sendRequest(const QString &requestURL, const HttpRequest::Method method, const QByteArray &payload) {
  if (active()) {
    qDebug() << "HttpRequest is active";
    return;
  }
  QString token;
  if (create_jwt) {
    token = CommaApi::create_jwt({}, 3600, sunnylink);
  } else {
    QString token_json = QString::fromStdString(util::read_file(util::getenv("HOME") + "/.comma/auth.json"));
    QJsonDocument json_d = QJsonDocument::fromJson(token_json.toUtf8());
    token = json_d["access_token"].toString();
  }

  QNetworkRequest request;
  request.setUrl(QUrl(requestURL));
  request.setRawHeader("User-Agent", getUserAgent(sunnylink).toUtf8());
  if (!payload.isEmpty()) {
    request.setRawHeader("Content-Type", "application/json");
  }

  if (!token.isEmpty()) {
    request.setRawHeader(QByteArray("Authorization"), ("JWT " + token).toUtf8());
  }

  if (method == HttpRequest::Method::GET) {
    reply = nam()->get(request);
  } else if (method == HttpRequest::Method::DELETE) {
    reply = nam()->deleteResource(request);
  } else if (method == HttpRequest::Method::POST) {
    reply = nam()->post(request, payload);
  } else if (method == HttpRequest::Method::PUT) {
    reply = nam()->put(request, payload);
  }

  networkTimer->start();
  connect(reply, &QNetworkReply::finished, this, &HttpRequest::requestFinished);
}

void HttpRequest::requestTimeout() {
  reply->abort();
}

void HttpRequest::requestFinished() {
  networkTimer->stop();

  if (reply->error() == QNetworkReply::NoError) {
    emit requestDone(reply->readAll(), true, reply->error());
  } else {
    QString error;
    if (reply->error() == QNetworkReply::OperationCanceledError) {
      nam()->clearAccessCache();
      nam()->clearConnectionCache();
      error = "Request timed out";
    } else {
      error = reply->errorString();
    }
    emit requestDone(error, false, reply->error());
  }

  reply->deleteLater();
  reply = nullptr;
}

QNetworkAccessManager *HttpRequest::nam() {
  static QNetworkAccessManager *networkAccessManager = new QNetworkAccessManager(qApp);
  return networkAccessManager;
}
