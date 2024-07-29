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

#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/services/user_service.h"

#include <QJsonArray>
#include <QJsonDocument>

UserService::UserService(QObject* parent) : BaseDeviceService(parent) {
  url = "/users";
}

void UserService::load() {
  loadDeviceData(url);
}

void UserService::startPolling() {
  loadDeviceData(url, true);
}

void UserService::handleResponse(const QString &response, bool success) {
  if (!success) return;

  QJsonDocument doc = QJsonDocument::fromJson(response.toUtf8());
  QJsonArray jsonArray = doc.array();

  std::vector<UserModel> users;
  for (const auto &value : jsonArray) {
    users.emplace_back(value.toObject());
  }

  emit usersReady(users);
  uiStateSP()->setSunnylinkDeviceUsers(users);
}
