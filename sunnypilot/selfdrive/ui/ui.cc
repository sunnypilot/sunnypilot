/**
 * The MIT License
 *
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 * Last updated: July 29, 2024
 */

#include "../../sunnypilot/selfdrive/ui/ui.h"

#include "common/watchdog.h"

void UIStateSP::updateStatus() {
  UIState::updateStatus();
}

UIStateSP::UIStateSP(QObject *parent) : UIState(parent) {
  sm = std::make_unique<SubMaster>(std::vector<const char*>{
    "modelV2", "controlsState", "liveCalibration", "radarState", "deviceState",
    "pandaStates", "carParams", "driverMonitoringState", "carState", "driverStateV2",
    "wideRoadCameraState", "managerState", "selfdriveState", "longitudinalPlan",
  });

  // update timer
  timer = new QTimer(this);
  QObject::connect(timer, &QTimer::timeout, this, &UIStateSP::update);
  timer->start(1000 / UI_FREQ);
}

// This method overrides completely the update method from the parent class intentionally.
void UIStateSP::update() {
  update_sockets(this);
  update_state(this);
  updateStatus();

  if (sm->frame % UI_FREQ == 0) {
    watchdog_kick(nanos_since_boot());
  }
  emit uiUpdate(*this);
}

DeviceSP::DeviceSP(QObject *parent) : Device(parent){
  QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &DeviceSP::update);
}

UIStateSP *uiStateSP() {
  static UIStateSP ui_state;
  return &ui_state;
}
UIStateSP *uiState() { return uiStateSP(); }

DeviceSP *deviceSP() {
  static DeviceSP _device;
  return &_device;
}
