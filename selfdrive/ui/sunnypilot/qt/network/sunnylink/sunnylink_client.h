#pragma once

#include <QObject>

#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/services/role_service.h"
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/services/user_service.h"

class SunnylinkClient : public QObject {
  Q_OBJECT

public:
  explicit SunnylinkClient(QObject* parent);
  RoleService* role_service;
  UserService* user_service;
};
