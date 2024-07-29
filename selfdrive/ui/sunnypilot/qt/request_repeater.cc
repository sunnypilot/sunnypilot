/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#include "selfdrive/ui/sunnypilot/qt/request_repeater.h"

#include "common/swaglog.h"

RequestRepeaterSP::RequestRepeaterSP(QObject *parent, const QString &requestURL, const QString &cacheKey,
                                 int period, bool whileOnroad, bool sunnylink) : HttpRequestSP(parent, true, 20000, sunnylink) {
  request_url = requestURL;
  while_onroad = whileOnroad;
  timer = new QTimer(this);
  timer->setTimerType(Qt::VeryCoarseTimer);
  connect(timer, &QTimer::timeout, [=]() { this->timerTick(); });
  timer->start(period * 1000);

  if (!cacheKey.isEmpty()) {
    prevResp = QString::fromStdString(params.get(cacheKey.toStdString()));
    if (!prevResp.isEmpty()) {
      QTimer::singleShot(500, [=]() { emit requestDone(prevResp, true, QNetworkReply::NoError); });
    }
    connect(this, &HttpRequest::requestDone, [=](const QString &resp, bool success) {
      if (success && resp != prevResp) {
        params.put(cacheKey.toStdString(), resp.toStdString());
        prevResp = resp;
      }
    });
  }

  // Don't wait for the timer to fire to send the first request
  ForceUpdate();
}

void RequestRepeaterSP::timerTick() {
  if ((!uiState()->scene.started || while_onroad) && device()->isAwake() && !active()) {
    LOGD("Sending request for %s", qPrintable(request_url));
    sendRequest(request_url);
  }
}
