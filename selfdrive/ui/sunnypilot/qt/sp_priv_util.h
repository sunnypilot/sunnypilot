#pragma once

#include <optional>
#include <vector>

#include <QDateTime>
#include <QFileSystemWatcher>
#include <QPainter>
#include <QPixmap>
#include <QSurfaceFormat>
#include <QWidget>

#include "cereal/gen/cpp/car.capnp.h"
#include "common/params.h"

QString getUserAgent(bool sunnylink = false);
std::optional<QString> getSunnylinkDongleId();
QMap<QString, QString> getCarNames();
void drawRoundedRect(QPainter &painter, const QRectF &rect, qreal xRadiusTop, qreal yRadiusTop, qreal xRadiusBottom, qreal yRadiusBottom);
QColor interpColor(float xv, std::vector<float> xp, std::vector<QColor> fp);