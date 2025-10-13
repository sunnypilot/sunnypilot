/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/subaru_settings.h"

SubaruSettings::SubaruSettings(QWidget *parent) : BrandSettingsInterface(parent) {
  stopAndGoToggle = new ParamControl("SubaruStopAndGo", tr("Stop and Go (Beta)"), "", "");
  stopAndGoToggle->setConfirmation(true, false);
  list->addItem(stopAndGoToggle);

  stopAndGoManualParkingBrakeToggle = new ParamControl(
    "SubaruStopAndGoManualParkingBrake",
    tr("Stop and Go for Manual Parking Brake (Beta)"),
    "",
    ""
  );
  stopAndGoManualParkingBrakeToggle->setConfirmation(true, false);
  list->addItem(stopAndGoManualParkingBrakeToggle);
}

void SubaruSettings::updateSettings() {
  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();

    is_subaru = CP.getBrand() == "subaru";

    if (is_subaru) {
      if (!(CP.getFlags() & (SUBARU_FLAG_GLOBAL_GEN2 | SUBARU_FLAG_HYBRID))) {
        has_stop_and_go = true;
      }
    }
  } else {
    is_subaru = false;
    has_stop_and_go = false;
  }

  bool stop_and_go_disabled = !offroad || !has_stop_and_go;
  QString stop_and_go_desc = stopAndGoDescriptionBuilder(stopAndGoDesc);
  QString stop_and_go_manual_parking_brake_desc = stopAndGoDescriptionBuilder(stopAndGoManualParkingBrakeDesc);
  if (stop_and_go_disabled) {
    stop_and_go_desc = stopAndGoDescriptionBuilder(stopAndGoDesc, stopAndGoDisabledMsg());
    stop_and_go_manual_parking_brake_desc = stopAndGoDescriptionBuilder(stopAndGoManualParkingBrakeDesc, stopAndGoDisabledMsg());
  }

  stopAndGoToggle->setEnabled(has_stop_and_go);
  stopAndGoToggle->setDescription(stop_and_go_desc);
  stopAndGoToggle->showDescription();

  stopAndGoManualParkingBrakeToggle->setEnabled(has_stop_and_go);
  stopAndGoManualParkingBrakeToggle->setDescription(stop_and_go_manual_parking_brake_desc);
  stopAndGoManualParkingBrakeToggle->showDescription();
}
