#include "selfdrive/ui/qt/network/sunnylink/sunnylink_client.h"
#include "selfdrive/ui/qt/network/sunnylink/services/user_service.h"

SunnylinkClient::SunnylinkClient(QObject* parent) : QObject(parent) {
  role_service = new RoleService(parent);
  user_service = new UserService(parent);
}
