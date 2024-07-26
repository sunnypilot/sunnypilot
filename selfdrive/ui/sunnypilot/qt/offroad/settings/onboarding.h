#pragma once

#include <selfdrive/ui/qt/offroad/onboarding.h>

#include "common/params.h"
#include "selfdrive/ui/qt/qt_window.h"

class TermsPageSP : public TermsPage {
  Q_OBJECT


public:
  explicit TermsPageSP(bool sunnypilot = false, QWidget *parent = 0) : TermsPage(parent), sunnypilot_tc(sunnypilot) {}


private:
  bool sunnypilot_tc = false;
  void showEvent(QShowEvent *event) override;
};

class OnboardingWindowSP : public OnboardingWindow {
  Q_OBJECT

public:
  explicit OnboardingWindowSP(QWidget *parent = 0);
  inline bool completed() const override { return accepted_terms && accepted_terms_sp && training_done; }

private:
  bool accepted_terms_sp = false;
  void updateActiveScreen() override;
};