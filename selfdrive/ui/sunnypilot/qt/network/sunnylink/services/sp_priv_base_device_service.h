#pragma once

#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/qt/request_repeater.h"
#include "selfdrive/ui/qt/util.h"

class BaseDeviceService : public QObject {
  Q_OBJECT

protected:
  void paramsRefresh();
  void loadDeviceData(const QString &url, bool poll = false);
  virtual void handleResponse(const QString &response, bool success) = 0;

  static bool is_sunnylink_enabled() { return Params().getBool("SunnylinkEnabled");}
  ParamWatcher* param_watcher;
  HttpRequest* initial_request = nullptr;
  RequestRepeater* repeater = nullptr;

public:
  explicit BaseDeviceService(QObject* parent = nullptr);
  virtual QString getCacheKey() const = 0;
  bool isCurrentyPolling() {return repeater != nullptr;}
  void stopPolling();
};
