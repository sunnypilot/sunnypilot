#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"

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
