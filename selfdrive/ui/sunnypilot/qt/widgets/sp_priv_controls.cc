#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"

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

AbstractControlSP::AbstractControlSP(const QString &title, const QString &desc, const QString &icon, QWidget *parent) : QFrame(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
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

void AbstractControlSP::hideEvent(QHideEvent *e) {
  if (description != nullptr) {
    description->hide();
  }
}

ParamControlSP::ParamControlSP(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent)
    : ParamControl(param, title, desc, icon, parent) {

  hlayout->removeWidget(&toggle);
  hlayout->insertWidget(0, &toggle);

  hlayout->removeWidget(this->icon_label);
  this->icon_pixmap = QPixmap(icon).scaledToWidth(20, Qt::SmoothTransformation);
  this->icon_label->setPixmap(this->icon_pixmap);
  this->icon_label->setSizePolicy(QSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed));
  hlayout->insertWidget(1, this->icon_label);
}
