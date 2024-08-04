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

#pragma once

#include "selfdrive/ui/sunnypilot/qt/request_repeater.h"
#include "selfdrive/ui/qt/util.h"

class BaseDeviceService : public QObject {
  Q_OBJECT

protected:
  void paramsRefresh();
  void loadDeviceData(const QString &url, bool poll = false);
  virtual void handleResponse(const QString &response, bool success) = 0;

  static bool is_sunnylink_enabled() { return Params().getBool("SunnylinkEnabled");}
  ParamWatcher* param_watcher;
  HttpRequestSP* initial_request = nullptr;
  RequestRepeaterSP* repeater = nullptr;

public:
  explicit BaseDeviceService(QObject* parent = nullptr);
  virtual QString getCacheKey() const = 0;
  bool isCurrentyPolling() {return repeater != nullptr;}
  void stopPolling();
};
