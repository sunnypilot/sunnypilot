/**
* Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/util.h"
#include "selfdrive/ui/qt/util.h"

#include <string>
#include <vector>

#include <QDir>
#include <QLayoutItem>
#include <QPainterPath>

#include "system/hardware/hw.h"

std::optional<QString> getParamIgnoringDefault(const std::string &param_name, const std::string &default_value) {
  std::string value = Params().get(param_name);

  if (!value.empty() && value != default_value)
    return QString::fromStdString(value);

  return {};
}

QString getUserAgent(bool sunnylink) {
  return (sunnylink ? "sunnypilot-" : "openpilot-") + getVersion();
}

std::optional<QString> getSunnylinkDongleId() {
  return getParamIgnoringDefault("SunnylinkDongleId", "UnregisteredDevice");
}

void drawRoundedRect(QPainter &painter, const QRectF &rect, qreal xRadiusTop, qreal yRadiusTop, qreal xRadiusBottom, qreal yRadiusBottom){
  qreal w_2 = rect.width() / 2;
  qreal h_2 = rect.height() / 2;

  xRadiusTop = 100 * qMin(xRadiusTop, w_2) / w_2;
  yRadiusTop = 100 * qMin(yRadiusTop, h_2) / h_2;

  xRadiusBottom = 100 * qMin(xRadiusBottom, w_2) / w_2;
  yRadiusBottom = 100 * qMin(yRadiusBottom, h_2) / h_2;

  qreal x = rect.x();
  qreal y = rect.y();
  qreal w = rect.width();
  qreal h = rect.height();

  qreal rxx2Top = w*xRadiusTop/100;
  qreal ryy2Top = h*yRadiusTop/100;

  qreal rxx2Bottom = w*xRadiusBottom/100;
  qreal ryy2Bottom = h*yRadiusBottom/100;

  QPainterPath path;
  path.arcMoveTo(x, y, rxx2Top, ryy2Top, 180);
  path.arcTo(x, y, rxx2Top, ryy2Top, 180, -90);
  path.arcTo(x+w-rxx2Top, y, rxx2Top, ryy2Top, 90, -90);
  path.arcTo(x+w-rxx2Bottom, y+h-ryy2Bottom, rxx2Bottom, ryy2Bottom, 0, -90);
  path.arcTo(x, y+h-ryy2Bottom, rxx2Bottom, ryy2Bottom, 270, -90);
  path.closeSubpath();

  painter.drawPath(path);
}

QColor interpColor(float xv, std::vector<float> xp, std::vector<QColor> fp) {
  assert(xp.size() == fp.size());

  int N = xp.size();
  int hi = 0;

  while (hi < N and xv > xp[hi]) hi++;
  int low = hi - 1;

  if (hi == N && xv > xp[low]) {
    return fp[fp.size() - 1];
  } else if (hi == 0){
    return fp[0];
  } else {
    return QColor(
      (xv - xp[low]) * (fp[hi].red() - fp[low].red()) / (xp[hi] - xp[low]) + fp[low].red(),
      (xv - xp[low]) * (fp[hi].green() - fp[low].green()) / (xp[hi] - xp[low]) + fp[low].green(),
      (xv - xp[low]) * (fp[hi].blue() - fp[low].blue()) / (xp[hi] - xp[low]) + fp[low].blue(),
      (xv - xp[low]) * (fp[hi].alpha() - fp[low].alpha()) / (xp[hi] - xp[low]) + fp[low].alpha());
  }
}