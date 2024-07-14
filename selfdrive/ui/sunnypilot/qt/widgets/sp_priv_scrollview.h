#pragma once

#include "selfdrive/ui/qt/widgets/scrollview.h"

class ScrollViewSP : public ScrollView {
  Q_OBJECT

public:
  explicit ScrollViewSP(QWidget *w = nullptr, QWidget *parent = nullptr);

public slots:
  void setLastScrollPosition();
  void restoreScrollPosition();

private:
  int lastScrollPosition = 0;
};
