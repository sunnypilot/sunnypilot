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

#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/sunnypilot/qt/util.h"
#include "common/util.h"

namespace SunnylinkApi {
  QByteArray rsa_encrypt(const QByteArray& data);
  QByteArray rsa_decrypt(const QByteArray& data);
  QString create_jwt(const QJsonObject& payloads = {}, int expiry = 3600, bool sunnylink = false);
}

class HttpRequestSP : public HttpRequest {
  Q_OBJECT

public:
  explicit HttpRequestSP(QObject* parent, bool create_jwt = true, int timeout = 20000, bool sunnylink = false) :
    HttpRequest(parent, create_jwt, timeout), sunnylink(sunnylink) {}

  using HttpRequest::sendRequest;
  void sendRequest(const QString& requestURL, Method method, const QByteArray& payload);

private:
  bool sunnylink;
    
protected:
  [[nodiscard]] QString GetJwtToken() const override { return SunnylinkApi::create_jwt({}, 3600, sunnylink); }
  [[nodiscard]] QString GetUserAgent() const override { return getUserAgent(sunnylink); }
};
