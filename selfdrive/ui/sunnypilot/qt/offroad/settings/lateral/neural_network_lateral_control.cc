/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/neural_network_lateral_control.h"

NeuralNetworkLateralControl::NeuralNetworkLateralControl() :
  ParamControl("NeuralNetworkLateralControl", tr("Neural Network Lateral Control (NNLC)"),  "", "") {
  setConfirmation(true, false);
  updateToggle();
}

void NeuralNetworkLateralControl::showEvent(QShowEvent *event) {
  updateToggle();
}

void NeuralNetworkLateralControl::updateToggle() {
  QString nnff_available_desc = tr("NNLC is currently not available on this platform.");
  QString nnff_fuzzy_desc =
    tr("Match: \"Exact\" is ideal, but \"Fuzzy\" is fine too. Reach out to the sunnypilot team in the following channel at the sunnypilot Discord server if there are any issues:")
    + " <font color='white'><b>#tuning-nnlc</b></font>";
  QString nnff_status_init = "<font color='yellow'>" + tr("Start the car to check car compatibility") + "</font>";
  QString nnff_not_loaded = "<font color='yellow'>" + tr("NNLC Not Loaded") + "</font>";
  QString nnff_loaded = "<font color=#00ff00>" + tr("NNLC Loaded") + "</font>";

  auto cp_bytes = params.get("CarParamsPersistent");
  auto cp_sp_bytes = params.get("CarParamsSPPersistent");
  if (!cp_bytes.empty() && !cp_sp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    AlignedBuffer aligned_buf_sp;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    capnp::FlatArrayMessageReader cmsg_sp(aligned_buf_sp.align(cp_sp_bytes.data(), cp_sp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();
    cereal::CarParamsSP::Reader CP_SP = cmsg_sp.getRoot<cereal::CarParamsSP>();

    /*** NNLC ***/
    {
      if (CP.getSteerControlType() == cereal::CarParams::SteerControlType::ANGLE) {
        params.remove("NeuralNetworkLateralControl");

        setDescription(nnffDescriptionBuilder(nnff_available_desc));
        setEnabled(false);
      } else if (isToggled()) {
        if (CP.getLateralTuning().which() == cereal::CarParams::LateralTuning::TORQUE) {
          QString nn_model_name = QString::fromStdString(CP_SP.getNeuralNetworkLateralControl().getModel().getName());
          QString nn_fuzzy = CP_SP.getNeuralNetworkLateralControl().getFuzzyFingerprint() ? tr("Fuzzy") : tr("Exact");

          setDescription(nnffDescriptionBuilder(
            (nn_model_name == "")
              ? nnff_status_init
              : (nn_model_name == "MOCK")
                  ? (nnff_not_loaded + "<br>" + tr(
                       "Reach out to the sunnypilot team in the following channel at the sunnypilot Discord server and donate logs to get NNLC loaded for your car: ")
                     + "<font color='white'><b>#tuning-nnlc</b></font>")
                  : (nnff_loaded + " | " + tr("Match") + " = " + nn_fuzzy + " | " + nn_model_name + "<br><br>" +
                     nnff_fuzzy_desc)
          ));
        } else {
          setDescription(nnffDescriptionBuilder(nnff_status_init));
        }
      } else {
        setDescription(nnff_description);
      }
    }
  } else {
    setDescription(isToggled() ? nnffDescriptionBuilder(nnff_status_init) : nnff_description);
  }

  if (getDescription() != nnff_description) {
    showDescription();
  }
}
