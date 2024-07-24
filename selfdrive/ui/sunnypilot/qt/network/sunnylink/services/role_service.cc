#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/services/role_service.h"

#include <QJsonArray>
#include <QJsonDocument>

RoleService::RoleService(QObject* parent) : BaseDeviceService(parent) {}

void RoleService::load() {
  loadDeviceData(url);
}

void RoleService::startPolling() {
  loadDeviceData(url, true);
}

void RoleService::handleResponse(const QString &response, bool success) {
  if (!success) return;

  QJsonDocument doc = QJsonDocument::fromJson(response.toUtf8());
  QJsonArray jsonArray = doc.array();

  std::vector<RoleModel> roles;
  for (const auto &value : jsonArray) {
    roles.emplace_back(value.toObject());
  }

  emit rolesReady(roles);
  uiStateSP()->setSunnylinkRoles(roles);
}
