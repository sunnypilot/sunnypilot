/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/onroad/alerts.h"

#include <QPainter>
#include <map>
#include <QRect>
#include <QFont>

OnroadAlerts::Alert OnroadAlertsSP::getAlert(const SubMaster &sm, uint64_t started_frame) {
  OnroadAlerts::Alert alert = OnroadAlerts::getAlert(sm, started_frame);
  alert.text1.replace("openpilot", "sunnypilot");
  alert.text2.replace("openpilot", "sunnypilot");
  return alert;
}

void OnroadAlertsSP::paintEvent(QPaintEvent *event) {
  if (alert.size == cereal::SelfdriveState::AlertSize::NONE) {
    return;
  } else if (alert.size == cereal::SelfdriveState::AlertSize::FULL) {
    OnroadAlerts::paintEvent(event);
    return;
  }
  static std::map<cereal::SelfdriveState::AlertSize, const int> alert_heights = {
    {cereal::SelfdriveState::AlertSize::SMALL, 271},
    {cereal::SelfdriveState::AlertSize::MID, 420}
  };
  int h = alert_heights[alert.size];

  QPainter p(this);
  QFont topFont;
  QFont bottomFont;
  QRect topTextBoundingRect;
  QRect bottomTextBoundingRect;
  QRect rect;

  int margin = 40;
  int radius = 30;

  const int dev_ui_info = uiStateSP()->scene.dev_ui_info;
  const int v_adjustment = dev_ui_info > 1 && alert.size != cereal::SelfdriveState::AlertSize::FULL ? 40 : 0;
  const int h_adjustment = dev_ui_info > 0 && alert.size != cereal::SelfdriveState::AlertSize::FULL ? 230 : 0;

  if (alert.size == cereal::SelfdriveState::AlertSize::SMALL) {
    topFont = InterFont(74, QFont::DemiBold);
    QFontMetrics fmTop(topFont);
    topTextBoundingRect = fmTop.boundingRect(
      QRect(0 + margin, height() - h + margin - v_adjustment, width() - margin * 2 - h_adjustment, 0), Qt::TextWordWrap,
      alert.text1);
    h = topTextBoundingRect.height();
    rect = QRect(0 + margin, height() - h - margin * 2 - v_adjustment, width() - margin * 2 - h_adjustment, h + margin);
  } else if (alert.size == cereal::SelfdriveState::AlertSize::MID) {
    topFont = InterFont(88, QFont::Bold);
    bottomFont = InterFont(66);
    QFontMetrics fmTop(topFont);
    QFontMetrics fmBotton(bottomFont);
    topTextBoundingRect = fmTop.boundingRect(
      QRect(0 + margin, height() - h + margin - v_adjustment, width() - margin * 2 - h_adjustment, 0), Qt::TextWordWrap,
      alert.text1);
    bottomTextBoundingRect = fmBotton.boundingRect(
      QRect(0 + margin, height() - h + margin - v_adjustment + topTextBoundingRect.height(),
            width() - margin * 2 - h_adjustment, 0), Qt::TextWordWrap, alert.text2);
    h = topTextBoundingRect.height() + bottomTextBoundingRect.height() + margin * 2;
    rect = QRect(0 + margin, height() - h - margin * 2 - v_adjustment, width() - margin * 2 - h_adjustment, h + margin);
  }


  // draw background + gradient
  // draw background + gradient
  p.setPen(Qt::NoPen);
  p.setCompositionMode(QPainter::CompositionMode_SourceOver);
  p.setBrush(QBrush(alert_colors[alert.status]));
  p.drawRoundedRect(rect, radius, radius);

  QLinearGradient g(0, rect.y(), 0, rect.bottom());
  g.setColorAt(0, QColor::fromRgbF(0, 0, 0, 0.05));
  g.setColorAt(1, QColor::fromRgbF(0, 0, 0, 0.35));

  p.setCompositionMode(QPainter::CompositionMode_DestinationOver);
  p.setBrush(QBrush(g));
  p.drawRoundedRect(rect, radius, radius);
  p.setCompositionMode(QPainter::CompositionMode_SourceOver);

  // text
  p.setPen(QColor(0xff, 0xff, 0xff));
  p.setRenderHint(QPainter::TextAntialiasing);
  p.setFont(topFont);
  if (alert.size == cereal::SelfdriveState::AlertSize::SMALL) {
    p.drawText(rect, Qt::AlignCenter | Qt::TextWordWrap, alert.text1);
  } else if (alert.size == cereal::SelfdriveState::AlertSize::MID) {
    QRect topText = QRect(rect.x(), rect.top() + margin, rect.width(), topTextBoundingRect.height());
    p.drawText(topText, Qt::AlignHCenter | Qt::AlignTop | Qt::TextWordWrap | Qt::AlignCenter, alert.text1);
    p.setFont(bottomFont);
    p.drawText(QRect(rect.x(), topText.bottom() + margin, rect.width(), bottomTextBoundingRect.height()),
               Qt::AlignHCenter | Qt::TextWordWrap | Qt::AlignCenter, alert.text2);
  }
}
