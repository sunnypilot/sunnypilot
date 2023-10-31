#pragma once

#include <QScrollArea>

class ScrollView : public QScrollArea {
  Q_OBJECT

public:
  explicit ScrollView(QWidget *w = nullptr, QWidget *parent = nullptr);
protected:
  void hideEvent(QHideEvent *e) override;

public slots:
  void setLastScrollPosition();
  void restoreScrollPosition();

private:
  int lastScrollPosition = 0;
};
