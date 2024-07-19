#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/services/sp_priv_user_service.h"

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
