#include "selfdrive/ui/sunnypilot/qt/sp_priv_offroad_home.h"
#include "selfdrive/ui/qt/offroad/experimental_mode.h"
#include "selfdrive/ui/qt/widgets/prime.h"
#include <QStackedWidget>

#ifdef ENABLE_MAPS
#define LEFT_WIDGET MapSettings
#else
#define LEFT_WIDGET QWidget
#endif

void OffroadHomeSP::replaceWidget(QWidget* old_widget, QWidget* new_widget)
{
    old_widget->parentWidget()->layout()->replaceWidget(old_widget, new_widget);
    delete old_widget;
}

void OffroadHomeSP::replaceLeftWidget(){
    auto* new_left_widget = new QStackedWidget(left_widget->parentWidget());
    new_left_widget->addWidget(new LEFT_WIDGET);
    if (!custom_mapbox)
        new_left_widget->addWidget(new PrimeAdWidget);
    
    new_left_widget->setStyleSheet("border-radius: 10px;");
    new_left_widget->setCurrentIndex((uiState()->hasPrime() || custom_mapbox) ? 0 : 1);
    connect(uiState(), &UIState::primeChanged, [=](bool prime)    {
        new_left_widget->setCurrentIndex((prime || custom_mapbox) ? 0 : 1);
    });
    replaceWidget(left_widget, new_left_widget);
}

OffroadHomeSP::OffroadHomeSP(QWidget* parent) : OffroadHome(parent){
    custom_mapbox = QString::fromStdString(params.get("CustomMapboxTokenSk")) != "";
    replaceLeftWidget();
}
