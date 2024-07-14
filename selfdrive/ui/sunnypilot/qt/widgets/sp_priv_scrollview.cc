#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_scrollview.h"

#include <QScrollBar>

ScrollViewSP::ScrollViewSP(QWidget *w, QWidget *parent) : ScrollView(w, parent) {
}

void ScrollViewSP::setLastScrollPosition() {
  lastScrollPosition = verticalScrollBar()->value();
}

void ScrollViewSP::restoreScrollPosition() {
  verticalScrollBar()->setValue(lastScrollPosition);
}
