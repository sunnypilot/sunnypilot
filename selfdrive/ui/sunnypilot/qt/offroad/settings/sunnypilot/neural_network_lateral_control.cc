/**
* Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnypilot/neural_network_lateral_control.h"

NeuralNetworkLateralcontrol::NeuralNetworkLateralcontrol(QWidget *parent) {
    toggle = new ParamControl(
      "NeuralNetworkLateralControlToggle",
      tr("Neural Network Lateral Control (NNLC)"),
      nnff_description,
      "");
    toggle->setConfirmation(true, false);
}

void NeuralNetworkLateralcontrol::refresh() {
    QString nnff_available_desc = tr("NNLC is currently not available on this platform.");
    QString nnff_fuzzy_desc = tr("Match: \"Exact\" is ideal, but \"Fuzzy\" is fine too. Reach out to the sunnypilot team in the following channel at the sunnypilot Discord server if there are any issues: ")
                                 + "<font color='white'><b>#tuning-nnlc</b></font>";
    QString nnff_status_init = "<font color='yellow'>⚠️ " + tr("Start the car to check car compatibility") + "</font>";
    QString nnff_not_loaded = "<font color='yellow'>⚠️ " + tr("NNLC Not Loaded") + "</font>";
    QString nnff_loaded = "<font color=#00ff00>✅ " + tr("NNLC Loaded") + "</font>";
    auto _car_model = QString::fromStdString(params.get("NNFFCarModel"));

    auto cp_bytes = params.get("CarParamsPersistent");
    auto cp_sp_bytes = params.get("CarParamsSPPersistent");
    if (!cp_bytes.empty() && !cp_sp_bytes.empty()) {
        AlignedBuffer aligned_buf;
        AlignedBuffer aligned_buf_sp;
        capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
        capnp::FlatArrayMessageReader cmsg_sp(aligned_buf_sp.align(cp_sp_bytes.data(), cp_sp_bytes.size()));
        cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();
        cereal::CarParamsSP::Reader CP_SP = cmsg_sp.getRoot<cereal::CarParamsSP>();

        if (CP.getSteerControlType() == cereal::CarParams::SteerControlType::ANGLE) {
            params.remove("EnforceTorqueLateral");

            toggle->setDescription(nnffDescriptionBuilder(nnff_available_desc));
            toggle->setEnabled(false);
            params.remove("NNFF");
        } else if (toggle->isToggled()) {
            if (CP.getLateralTuning().which() == cereal::CarParams::LateralTuning::TORQUE) {
                QString nn_model_name = QString::fromStdString(CP_SP.getNeuralNetworkLateralControl().getModelName());
                QString nn_fuzzy = CP_SP.getNeuralNetworkLateralControl().getFuzzyFingerprint() ? tr("Fuzzy") : tr("Exact");

                toggle->setDescription(nnffDescriptionBuilder(
                    (nn_model_name == "")     ? nnff_status_init :
                        (nn_model_name == "mock") ? (nnff_not_loaded + "<br>" + tr("Reach out to the sunnypilot team in the following channel at the sunnypilot Discord server and donate logs to get NNLC loaded for your car: ")
                                                     + "<font color='white'><b>#tuning-nnlc</b></font>") :
                            (nnff_loaded + " | " + tr("Match") + " = " + nn_fuzzy + " | " + _car_model + "<br><br>" + nnff_fuzzy_desc)));
            } else {
                toggle->setDescription(nnffDescriptionBuilder(nnff_status_init));
            }
        } else {
            toggle->setDescription(nnff_description);
        }
    }
}


// ParamControlSP *NeuralNetworkLateralcontrol::configure_settings_interaction(ListWidgetSP *list) {
//     list->addItem(neuralNetworkLateralControlToggle);
//     return neuralNetworkLateralControlToggle;
// }