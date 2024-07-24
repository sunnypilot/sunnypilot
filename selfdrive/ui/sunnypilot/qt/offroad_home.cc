#include "selfdrive/ui/sunnypilot/qt/offroad_home.h"
#include "selfdrive/ui/qt/offroad/experimental_mode.h"
#include "selfdrive/ui/qt/widgets/prime.h"
#include <QStackedWidget>
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
