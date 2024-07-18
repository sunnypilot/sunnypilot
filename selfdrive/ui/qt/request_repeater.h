#pragma once

#include "common/swaglog.h"
#include "common/util.h"
#include "selfdrive/ui/qt/api.h"
#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/sp_priv_ui.h"
#else
#include "selfdrive/ui/ui.h"
#endif

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
