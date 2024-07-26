#include "selfdrive/ui/qt/request_repeater.h"

RequestRepeater::RequestRepeater(QObject *parent, const QString &url, const QString &cache_key,
                                 int period, bool trigger_while_onroad) : HttpRequest(parent) {
  timer = new QTimer(this);
  timer->setTimerType(Qt::VeryCoarseTimer);

  connectTimer(url, trigger_while_onroad);

  timer->start(period * 1000);

  setupCacheProcess(cache_key);
}

void RequestRepeater::connectTimer(const QString &url, bool trigger_while_onroad) {
  QObject::connect(timer, &QTimer::timeout, [=]() {
    if ((!uiState()->scene.started || trigger_while_onroad) && device()->isAwake() && !active()) {
      sendRequest(url);
    }
  });
}

void RequestRepeater::setupCacheProcess(const QString &cache_key) {
  if (!cache_key.isEmpty()) {
    prevResp = QString::fromStdString(params.get(cache_key.toStdString()));
    if (!prevResp.isEmpty()) {
      QTimer::singleShot(500, [=]() { emit requestDone(prevResp, true, QNetworkReply::NoError); });
    }
    QObject::connect(this, &HttpRequest::requestDone, [=](const QString &resp, bool success) {
      if (success && resp != prevResp) {
        params.put(cache_key.toStdString(), resp.toStdString());
        prevResp = resp;
      }
    });
  }
}