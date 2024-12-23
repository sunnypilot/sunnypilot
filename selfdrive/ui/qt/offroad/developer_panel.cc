#include <QDebug>

#include "selfdrive/ui/qt/offroad/developer_panel.h"
#include "selfdrive/ui/qt/widgets/ssh_keys.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "common/util.h"

DeveloperPanel::DeveloperPanel(SettingsWindow *parent) : ListWidget(parent) {
  // SSH keys
  addItem(new SshToggle());
  addItem(new SshControl());

  joystickToggle = new ParamControl("JoystickDebugMode", tr("Joystick Debug Mode"), "", "");
  QObject::connect(joystickToggle, &ParamControl::toggleFlipped, [=](bool state) {
    params.putBool("LongitudinalManeuverMode", false);
    longManeuverToggle->refresh();
  });
  addItem(joystickToggle);

  longManeuverToggle = new ParamControl("LongitudinalManeuverMode", tr("Longitudinal Maneuver Mode"), "", "");
  QObject::connect(longManeuverToggle, &ParamControl::toggleFlipped, [=](bool state) {
    params.putBool("JoystickDebugMode", false);
    joystickToggle->refresh();
  });
  addItem(longManeuverToggle);

  auto enableGithubRunner = new ParamControl("EnableGithubRunner", tr("Enable GitHub runner service"), tr("Enables or disables the github runner service."), "");
  addItem(enableGithubRunner);

  // FIXME-SP: Move to sunnypilot panels before merging
  auto madsToggle = new ParamControl("Mads", tr("Modular Assistive Driving System (MADS)"), "", "");
  addItem(madsToggle);

  // TODO-SP: Rename toggle
  auto madsMainCruiseToggle = new ParamControl("MadsMainCruiseAllowed", tr("MADS: Toggle with Main Cruise"), tr("Note: For vehicles without LFA/LKAS button, disabling this will prevent lateral control engagement."), "");
  addItem(madsMainCruiseToggle);

  auto madsPauseLateralOnBrakeToggle = new ParamControl("MadsPauseLateralOnBrake", tr("MADS: Pause Lateral on Brake"), "", "");
  addItem(madsPauseLateralOnBrakeToggle);

  auto madsUnifiedEngagementModeToggle = new ParamControl("MadsUnifiedEngagementMode", tr("MADS: Unified Engagement Mode"), "", "");
  addItem(madsUnifiedEngagementModeToggle);

  // Joystick and longitudinal maneuvers should be hidden on release branches
  is_release = params.getBool("IsReleaseBranch");

  // Toggles should be not available to change in onroad state
  QObject::connect(uiState(), &UIState::offroadTransition, this, &DeveloperPanel::updateToggles);
}

void DeveloperPanel::updateToggles(bool _offroad) {
  for (auto btn : findChildren<ParamControl *>()) {
    btn->setVisible(!is_release);
    btn->setEnabled(_offroad);
  }

  // longManeuverToggle should not be toggleable if the car don't have longitudinal control
  auto cp_bytes = params.get("CarParamsPersistent");
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();
    longManeuverToggle->setEnabled(hasLongitudinalControl(CP) && _offroad);
  } else {
    longManeuverToggle->setEnabled(false);
  }

  offroad = _offroad;
}

void DeveloperPanel::showEvent(QShowEvent *event) {
  updateToggles(offroad);
}
