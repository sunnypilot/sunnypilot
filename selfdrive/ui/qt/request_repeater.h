#pragma once

#include "common/util.h"

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/api.h"
#else
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/api.h"
#endif

class RequestRepeater : public HttpRequest {
public:
  void connectTimer(const QString& requestURL, bool while_onroad);
  void setupCacheProcess(const QString& cacheKey);
  RequestRepeater(QObject *parent, const QString &requestURL, const QString &cacheKey = "", int period = 0, bool while_onroad=false);

private:
  Params params;
  QTimer *timer;
  QString prevResp;
};
