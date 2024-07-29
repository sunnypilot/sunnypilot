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

#include "selfdrive/ui/sunnypilot/qt/api.h"

#include <openssl/pem.h>
#include <openssl/rsa.h>
#include <openssl/aes.h>

#include <QApplication>
#include <QJsonDocument>

#include <string>
#include <common/swaglog.h>

#include "util.h"
#include "common/util.h"
#include "system/hardware/hw.h"
#include "selfdrive/ui/qt/util.h"

namespace SunnylinkApi {

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
  return jwt + "." + CommaApi::rsa_sign(hash).toBase64(b64_opts);
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


}  // namespace SunnylinkApi

void HttpRequestSP::sendRequest(const QString& requestURL, Method method, const QByteArray& payload) {
  if (active()) {
    return;
  }  
  QNetworkRequest request = prepareRequest(requestURL);

  if(!payload.isEmpty() && (method == Method::POST || method == Method::PUT)) {
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
  }

  switch (method) {
  case Method::GET:
    reply = nam()->get(request);
    break;
  case Method::DELETE:
    reply = nam()->deleteResource(request);
    break;
  case Method::POST:
    reply = nam()->post(request, payload);
    break;
  case Method::PUT:
    reply = nam()->put(request, payload);
    break;
  }

  networkTimer->start();
  connect(reply, &QNetworkReply::finished, this, &HttpRequestSP::requestFinished);
}
