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

#include "selfdrive/ui/sunnypilot/qt/offroad_home.h"

#include <QStackedWidget>

#include "selfdrive/ui/qt/offroad/experimental_mode.h"
#include "selfdrive/ui/qt/widgets/prime.h"
#include "selfdrive/ui/sunnypilot/sunnypilot_main.h"

#ifdef ENABLE_MAPS
#define LEFT_WIDGET MapSettings
#else
#define LEFT_WIDGET QWidget
#endif

void OffroadHomeSP::replaceLeftWidget(){
  auto* new_left_widget = new QStackedWidget(left_widget->parentWidget());
  new_left_widget->addWidget(new LEFT_WIDGET);
  if (!custom_mapbox)
    new_left_widget->addWidget(new PrimeAdWidget);
    
  new_left_widget->setStyleSheet("border-radius: 10px;");
  new_left_widget->setCurrentIndex((uiStateSP()->hasPrime() || custom_mapbox) ? 0 : 1);
  connect(uiStateSP(), &UIStateSP::primeChanged, [=](bool prime)    {
    new_left_widget->setCurrentIndex((prime || custom_mapbox) ? 0 : 1);
  });
  ReplaceWidget(left_widget, new_left_widget);
}

OffroadHomeSP::OffroadHomeSP(QWidget* parent) : OffroadHome(parent){
  custom_mapbox = QString::fromStdString(params.get("CustomMapboxTokenSk")) != "";
  replaceLeftWidget();
}
