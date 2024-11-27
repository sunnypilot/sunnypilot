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

  // FIXME-SP: Move to sunnypilot panels before merging
  auto madsToggle = new ParamControl("Mads", tr("Modular Assistive Driving System (MADS)"), "", "");
  addItem(madsToggle);

  // TODO-SP: Rename toggle
  auto madsCruiseMainToggle = new ParamControl("MadsCruiseMain", tr("MADS: Cruise Main"), "", "");
  addItem(madsCruiseMainToggle);

  auto madsDisengageLateralOnBrakeToggle = new ParamControl("MadsDisengageLateralOnBrake", tr("MADS: Disengage Lateral on Brake"), "", "");
  addItem(madsDisengageLateralOnBrakeToggle);

  auto madsUnifiedEngagementModeToggle = new ParamControl("MadsUnifiedEngagementMode", tr("MADS: Unified Engagement Mode"), "", "");
  addItem(madsUnifiedEngagementModeToggle);

  auto toyotaabhToggle = new ParamControl("ToyotaAutoHold", tr("Toyota: Auto Brake Hold"), "", "");
  addItem(toyotaabhToggle);

  auto toyotaebsmToggle = new ParamControl("ToyotaEnhancedBsm", tr("Toyota: Enhanced BSM"), "", "");
  addItem(toyotaebsmToggle);

  auto toyotatss2longToggle = new ParamControl("ToyotaTSS2Long", tr("Toyota: custom tune"), "", "");
  addItem(toyotatss2longToggle);

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
