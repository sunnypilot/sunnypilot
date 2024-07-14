#pragma once

#include "selfdrive/ui/qt/widgets/controls.h"

class ParamControlSP : public ParamControl {
  Q_OBJECT

public:
  ParamControlSP(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent = nullptr);

  bool isToggled() { return params.getBool(key); }
};
