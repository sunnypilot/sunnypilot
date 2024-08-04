/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

#include <QPainter>
#include <QStyleOption>
#include "selfdrive/ui/sunnypilot/sunnypilot_main.h"

QFrame *horizontal_line(QWidget *parent) {
  QFrame *line = new QFrame(parent);
  line->setFrameShape(QFrame::StyledPanel);
  line->setStyleSheet(R"(
    border-width: 2px;
    border-bottom-style: solid;
    border-color: gray;
  )");
  line->setFixedHeight(10);
  return line;
}

AbstractControlSP::AbstractControlSP(const QString &title, const QString &desc, const QString &icon, QWidget *parent)
  : AbstractControl(title, desc, icon, parent) {

  main_layout = new QVBoxLayout(this);
  main_layout->setMargin(0);

  hlayout = new QHBoxLayout;
  hlayout->setMargin(0);
  hlayout->setSpacing(20);

  // left icon
  icon_label = new QLabel(this);
  hlayout->addWidget(icon_label);
  if (!icon.isEmpty()) {
    icon_pixmap = QPixmap(icon).scaledToWidth(80, Qt::SmoothTransformation);
    icon_label->setPixmap(icon_pixmap);
    icon_label->setSizePolicy(QSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed));
  }
  icon_label->setVisible(!icon.isEmpty());

  // title
  title_label = new QPushButton(title);
  title_label->setFixedHeight(120);
  title_label->setStyleSheet("font-size: 50px; font-weight: 450; text-align: left; border: none;");
  hlayout->addWidget(title_label, 1);

  // value next to control button
  value = new ElidedLabelSP();
  value->setAlignment(Qt::AlignRight | Qt::AlignVCenter);
  value->setStyleSheet("color: #aaaaaa");
  hlayout->addWidget(value);

  main_layout->addLayout(hlayout);

  // description
  description = new QLabel(desc);
  description->setContentsMargins(40, 20, 40, 20);
  description->setStyleSheet("font-size: 40px; color: grey");
  description->setWordWrap(true);
  description->setVisible(false);
  main_layout->addWidget(description);

  connect(title_label, &QPushButton::clicked, [=]() {
    if (!description->isVisible()) {
      emit showDescriptionEvent();
    }

    if (!description->text().isEmpty()) {
      description->setVisible(!description->isVisible());
    }
  });

  main_layout->addStretch();
}

void AbstractControlSP::hideEvent(QHideEvent *e) {
  if (description != nullptr) {
    description->hide();
  }
}

AbstractControlSP_SELECTOR::AbstractControlSP_SELECTOR(const QString &title, const QString &desc, const QString &icon, QWidget *parent)
  : AbstractControlSP(title, desc, icon, parent) {

  if (value != nullptr) {
    ReplaceWidget(value, new QWidget());
    value = nullptr;
  }

  QLayoutItem* item;
  while ((item = main_layout->takeAt(0)) != nullptr) {
    if (item->widget()) {
      delete item->widget();
    }
    delete item;
  }

  main_layout->setMargin(0);

  hlayout = new QHBoxLayout;
  hlayout->setMargin(0);
  hlayout->setSpacing(0);

  // title
  if (!title.isEmpty()) {
    title_label = new QPushButton(title);
    title_label->setFixedHeight(120);
    title_label->setStyleSheet("font-size: 50px; font-weight: 450; text-align: left; border: none;");
    main_layout->addWidget(title_label, 1);

    connect(title_label, &QPushButton::clicked, [=]() {
      if (!description->isVisible()) {
        emit showDescriptionEvent();
      }

      if (!description->text().isEmpty()) {
        description->setVisible(!description->isVisible());
      }
    });
  } else {
    main_layout->addSpacing(20);
  }

  main_layout->addLayout(hlayout);
  main_layout->addSpacing(2);

  // description
  description = new QLabel(desc);
  description->setContentsMargins(0, 20, 40, 20);
  description->setStyleSheet("font-size: 40px; color: grey");
  description->setWordWrap(true);
  description->setVisible(false);
  main_layout->addWidget(description);

  main_layout->addStretch();
}

// controls

ButtonControlSP::ButtonControlSP(const QString &title, const QString &text, const QString &desc, QWidget *parent) : AbstractControlSP(title, desc, "", parent) {
  btn.setText(text);
  btn.setStyleSheet(R"(
    QPushButton {
      padding: 0;
      border-radius: 50px;
      font-size: 35px;
      font-weight: 500;
      color: #E4E4E4;
      background-color: #393939;
    }
    QPushButton:pressed {
      background-color: #4a4a4a;
    }
    QPushButton:disabled {
      color: #33E4E4E4;
    }
  )");
  btn.setFixedSize(250, 100);
  QObject::connect(&btn, &QPushButton::clicked, this, &ButtonControlSP::clicked);
  hlayout->addWidget(&btn);
}

// ElidedLabelSP

ElidedLabelSP::ElidedLabelSP(QWidget *parent) : ElidedLabelSP({}, parent) {}

ElidedLabelSP::ElidedLabelSP(const QString &text, QWidget *parent) : QLabel(text.trimmed(), parent) {
  setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
  setMinimumWidth(1);
}

void ElidedLabelSP::resizeEvent(QResizeEvent* event) {
  QLabel::resizeEvent(event);
  lastText_ = elidedText_ = "";
}

void ElidedLabelSP::paintEvent(QPaintEvent *event) {
  const QString curText = text();
  if (curText != lastText_) {
    elidedText_ = fontMetrics().elidedText(curText, Qt::ElideRight, contentsRect().width());
    lastText_ = curText;
  }

  QPainter painter(this);
  drawFrame(&painter);
  QStyleOption opt;
  opt.initFrom(this);
  style()->drawItemText(&painter, contentsRect(), alignment(), opt.palette, isEnabled(), elidedText_, foregroundRole());
}

// ParamControlSP

ParamControlSP::ParamControlSP(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent)
    : ToggleControlSP(title, desc, icon, false, parent) {
  key = param.toStdString();
  QObject::connect(this, &ParamControlSP::toggleFlipped, this, &ParamControlSP::toggleClicked);

  hlayout->removeWidget(&toggle);
  hlayout->insertWidget(0, &toggle);

  hlayout->removeWidget(this->icon_label);
  this->icon_pixmap = QPixmap(icon).scaledToWidth(20, Qt::SmoothTransformation);
  this->icon_label->setPixmap(this->icon_pixmap);
  this->icon_label->setSizePolicy(QSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed));
  hlayout->insertWidget(1, this->icon_label);
}

void ParamControlSP::toggleClicked(bool state) {
  auto do_confirm = [this]() {
    QString content("<body><h2 style=\"text-align: center;\">" + title_label->text() + "</h2><br>"
                    "<p style=\"text-align: center; margin: 0 128px; font-size: 50px;\">" + getDescription() + "</p></body>");
    return ConfirmationDialog(content, tr("Enable"), tr("Cancel"), true, this).exec();
  };

  bool confirmed = store_confirm && params.getBool(key + "Confirmed");
  if (!confirm || confirmed || !state || do_confirm()) {
    if (store_confirm && state) params.putBool(key + "Confirmed", true);
    params.putBool(key, state);
    setIcon(state);
  } else {
    toggle.togglePosition();
  }
}
