/**
 * Copyright (c) 2025-, sunnypilot contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnylink/community_widget.h"

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/util.h"

using qrcodegen::QrCode;

// --- SunnylinkCommunityQRWidget ---

SunnylinkCommunityQRWidget::SunnylinkCommunityQRWidget(QWidget* parent)
    : QWidget(parent) {}

void SunnylinkCommunityQRWidget::showEvent(QShowEvent *event) {
  updateQrCode(SUNNYLINK_COMMUNITY_URL);
  update();
}

void SunnylinkCommunityQRWidget::updateQrCode(const QString &text) {
  QrCode qr = QrCode::encodeText(text.toUtf8().data(), QrCode::Ecc::LOW);
  qint32 sz = qr.getSize();
  QImage im(sz, sz, QImage::Format_RGB32);

  QRgb black = qRgb(0, 0, 0);
  QRgb white = qRgb(255, 255, 255);
  for (int y = 0; y < sz; y++) {
    for (int x = 0; x < sz; x++) {
      im.setPixel(x, y, qr.getModule(x, y) ? black : white);
    }
  }

  int final_sz = ((width() / sz) - 1) * sz;
  img = QPixmap::fromImage(im.scaled(final_sz, final_sz, Qt::KeepAspectRatio), Qt::MonoOnly);
}

void SunnylinkCommunityQRWidget::paintEvent(QPaintEvent *e) {
  QPainter p(this);
  p.fillRect(rect(), Qt::white);

  if (!img.isNull()) {
    QSize s = (size() - img.size()) / 2;
    p.drawPixmap(s.width(), s.height(), img);
  }
}

// --- SunnylinkCommunityPopup ---

QStringList SunnylinkCommunityPopup::getInstructions() {
  QStringList instructions;
  instructions << tr("Scan the QR code and join us!");
  return instructions;
}

SunnylinkCommunityPopup::SunnylinkCommunityPopup(QWidget* parent)
    : DialogBase(parent) {
  auto *mainLayout = new QVBoxLayout(this);
  mainLayout->setContentsMargins(0, 0, 0, 0);
  mainLayout->setSpacing(0);

  // Solarized Light base3 background
  setStyleSheet("SunnylinkCommunityPopup { background-color: #FDF6E3; }");

  // Header spanning full width
  auto headerWidget = new QWidget(this);
  auto headerLayout = new QHBoxLayout(headerWidget);
  headerLayout->setContentsMargins(85, 50, 85, 30);
  headerLayout->setSpacing(30);

  auto close = new QPushButton(QIcon(":/icons/close.svg"), "", this);
  close->setIconSize(QSize(80, 80));
  close->setStyleSheet("border: none;");
  connect(close, &QPushButton::clicked, this, &QDialog::reject);
  headerLayout->addWidget(close, 0, Qt::AlignLeft | Qt::AlignVCenter);

  const auto title = new QLabel(tr("Join the sunnypilot Community Forum"), this);
  // Solarized base02 for text
  title->setStyleSheet("font-size: 65px; color: #073642;");
  title->setWordWrap(false);
  title->setAlignment(Qt::AlignCenter);
  headerLayout->addWidget(title, 1);

  // Spacer to balance the close button on the right
  auto spacer = new QWidget(this);
  spacer->setFixedSize(80, 80);
  headerLayout->addWidget(spacer, 0);

  mainLayout->addWidget(headerWidget);

  // Two-column content layout
  auto contentLayout = new QHBoxLayout();
  contentLayout->setContentsMargins(0, 0, 0, 0);
  contentLayout->setSpacing(0);
  mainLayout->addLayout(contentLayout, 66);

  // Left side: description
  auto leftLayout = new QVBoxLayout();
  leftLayout->setContentsMargins(85, 40, 50, 70);
  leftLayout->setSpacing(35);
  contentLayout->addLayout(leftLayout, 40);

  // Hype / intro paragraph
  const auto desc = new QLabel(tr(
    "We're excited to announce our <b>sunnypilot Community Forum</b><br><br>"
    "Over the years, Discord just hasn't scaled well for our growing community.<br>"
    "It's noisy, unsearchable, and great discussions disappear too easily.<br>"
    "Our new community forum aims to fix that by making it easier to <b>find answers, share ideas, track feedback, report bugs, help newcomers</b> and more!<br><br>"
    "<b>Here's what's waiting for you:</b><br>"
    "• Fully <b>indexable</b> and discoverable through search engines 🔎<br>"
    "• <b>AI-powered</b>🤖 topic and chat summaries, spam detection, and more<br>"
    "• A <b>trust-level system</b>✅ that rewards meaningful contributions<br>"
    "• Designed to work <b>on your own time</b>.🧘<br><br>"
    "Scan the QR code on the right and join the discussion!"
  ), this);
  // Solarized base01 for body text
  desc->setStyleSheet("font-size: 40px; color: #586E75;");
  desc->setWordWrap(true);
  leftLayout->addWidget(desc);

  leftLayout->addStretch();

  // Right side: QR code and instructions
  auto rightLayout = new QVBoxLayout();
  rightLayout->setContentsMargins(50, 40, 85, 70);
  rightLayout->setSpacing(40);
  contentLayout->addLayout(rightLayout, 1);

  // QR code (smaller, fixed size)
  auto *qr = new SunnylinkCommunityQRWidget(this);
  qr->setFixedSize(500, 500);
  rightLayout->addStretch();
  rightLayout->addWidget(qr, 0, Qt::AlignCenter);
  rightLayout->addStretch();
}