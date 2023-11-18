#ifndef SAFETY_SUNNYPILOT_COMMON_H
#define SAFETY_SUNNYPILOT_COMMON_H

void mads_acc_main_check(const bool main_on) {
  if (main_on && mads_enabled) {
    controls_allowed = true;
  }
  if (!main_on && acc_main_on_prev) {
    disengageFromBrakes = false;
    controls_allowed = false;
    controls_allowed_long = false;
  }
  acc_main_on_prev = main_on;
}

void mads_lkas_button_check(const bool lkas_pressed) {
  if (lkas_pressed && !lkas_pressed_prev) {
    controls_allowed = true;
  }
  lkas_pressed_prev = lkas_pressed;
}

void mads_exit_controls_check(void) {
  if (alternative_experience & ALT_EXP_MADS_DISABLE_DISENGAGE_LATERAL_ON_BRAKE) {
    disengageFromBrakes = true;
    controls_allowed_long = false;
  } else {
    if ((alternative_experience & ALT_EXP_ENABLE_MADS) && controls_allowed) {
      disengageFromBrakes = true;
    }
    controls_allowed = false;
    controls_allowed_long = false;
  }
}

void mads_resume_controls_check(void) {
  disengageFromBrakes = false;
  if (alternative_experience & ALT_EXP_ENABLE_MADS) {
    controls_allowed = true;
  }
}

#endif
