#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/sp_priv_sunnylink_client.h"
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/services/sp_priv_user_service.h"

SunnylinkClient::SunnylinkClient(QObject* parent) : QObject(parent) {
  role_service = new RoleService(parent);
  user_service = new UserService(parent);
}
