/**
* Copyright (c) 2025-, sunnypilot contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <QrCode.hpp>
#include <QtCore/qjsonobject.h>

#include "common/util.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

const QString SUNNYLINK_COMMUNITY_URL = "https://community.sunnypilot.ai/sp-qr";

class SunnylinkCommunityQRWidget : public QWidget {
  Q_OBJECT

public:
  explicit SunnylinkCommunityQRWidget(QWidget* parent = nullptr);
  void paintEvent(QPaintEvent*) override;

private:
  QPixmap img;
  void updateQrCode(const QString &text);
  void showEvent(QShowEvent *event) override;
};

// Popup widget
class SunnylinkCommunityPopup : public DialogBase {
  Q_OBJECT

public:
  explicit SunnylinkCommunityPopup(QWidget* parent = nullptr);

private:
  static QStringList getInstructions();
};
