#pragma once

#include "common/swaglog.h"
#include "common/util.h"
#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/ui.h"

class RequestRepeater : public HttpRequest {

private:
  Params params;
  QTimer *timer;
  QString prevResp;
  QString request_url;
  bool while_onroad;
  void timerTick();

public:
  RequestRepeater(QObject *parent, const QString &requestURL, const QString &cacheKey = "", int period = 0, bool whileOnroad=false, bool sunnylink = false);
  void ForceUpdate() {
    LOGD("Forcing update for %s", qPrintable(request_url));
    timerTick();
  }
};
