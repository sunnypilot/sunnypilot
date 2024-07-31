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

#include <QJsonObject>

class UserModel {
public:
  QString device_id;
  QString user_id;
  qint64 created_at;
  qint64 updated_at;
  QString token_hash;

  explicit UserModel(const QJsonObject &json) {
    device_id = json["device_id"].toString();
    user_id = json["user_id"].toString();
    created_at = json["created_at"].toInt();
    updated_at = json["updated_at"].toInt();
    token_hash = json["token_hash"].toString();
  }

  [[nodiscard]] QJsonObject toJson() const {
    QJsonObject json;
    json["device_id"] = device_id;
    json["user_id"] = user_id;
    json["created_at"] = created_at;
    json["updated_at"] = updated_at;
    json["token_hash"] = token_hash;
    return json;
  }
};
