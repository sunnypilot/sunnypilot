/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <QWidget>
#include <QTimer>
#include <QVBoxLayout>
#include <map>

#include "common/params.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/widgets/input.h"


class HyundaiLiveTuning : public QWidget {
  Q_OBJECT

public:
  explicit HyundaiLiveTuning(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;
  void updateToggles();

signals:
  void backPress();

private:
  Params params;
  QVBoxLayout *main_layout;
  ListWidgetSP *list;
  std::map<std::string, QLabel*> spinner_controls;
  std::map<std::string, ButtonControlSP*> list_controls;

  void resetToDefaults();
  void createFloatControl(const QString &param, const QString &title, const QString &desc,
                         float min_val, float max_val, float step = 0.01f);
  void createListControl(const QString &param, const QString &title, const QString &desc);
};
