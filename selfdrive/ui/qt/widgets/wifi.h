#pragma once

#include <QFrame>
#include <QWidget>

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnylink/community_widget.h"

class WiFiPromptWidget : public QFrame {
  Q_OBJECT

public:
  explicit WiFiPromptWidget(QWidget* parent = 0);

private:
  SunnylinkCommunityPopup *community_popup;

signals:
  void openSettings(int index = 0, const QString &param = "");
};
