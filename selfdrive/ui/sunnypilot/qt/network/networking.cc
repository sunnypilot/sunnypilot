#include "selfdrive/ui/sunnypilot/qt/network/networking.h"
#include <QVBoxLayout>
#include <QPushButton>
#include <QStackedLayout>

NetworkingSP::NetworkingSP(QWidget *parent) : Networking(parent) {
  auto vlayout = wifiScreen->findChild<QVBoxLayout*>();
  auto hlayout = new QHBoxLayout();

  // Create and setup scan button
  auto scanButton = new QPushButton(tr("Scan"));
  scanButton->setObjectName("scan_btn");
  scanButton->setFixedSize(400, 100);

  connect(wifi, &WifiManager::refreshSignal, this, [=]() { scanButton->setText(tr("Scan")); scanButton->setEnabled(true); });
  connect(scanButton, &QPushButton::clicked, [=]() { scanButton->setText(tr("Scanning...")); scanButton->setEnabled(false); wifi->requestScan(); });

  hlayout->addWidget(scanButton);
  hlayout->addStretch(1);

  // Look for an existing Advanced button
  QPushButton* existingAdvanced = wifiScreen->findChild<QPushButton*>("advanced_btn");
  if (existingAdvanced) {
    // Override the advanced networking panel
    an = new AdvancedNetworkingSP(this, wifi);
    disconnect(existingAdvanced, &QPushButton::clicked, nullptr, nullptr);
    connect(existingAdvanced, &QPushButton::clicked, [=]() { main_layout->setCurrentWidget(an); });
    connect(an, &AdvancedNetworkingSP::backPress, [=]() { main_layout->setCurrentWidget(wifiScreen); });
    connect(an, &AdvancedNetworkingSP::requestWifiScreen, [=]() { main_layout->setCurrentWidget(wifiScreen); });
    main_layout->addWidget(an);
    hlayout->addWidget(existingAdvanced);
  }

  // Insert our new layout at the top of vlayout
  vlayout->setMargin(40);
  vlayout->insertLayout(0, hlayout);

  // Add our scan button to the existing style selectors
  auto newStyleSheet = styleSheet().replace(
    ", #advanced_btn ",
    ", #advanced_btn, #scan_btn "
  ).replace(
    ", #advanced_btn:pressed",
    ", #advanced_btn:pressed, #scan_btn:pressed"
  ).append(R"(
    #scan_btn:disabled {
      background-color: #121212;
      color: #33FFFFFF;
    }
  )");
  setStyleSheet(newStyleSheet);
}

AdvancedNetworkingSP::AdvancedNetworkingSP(QWidget *parent, WifiManager *wifi) : AdvancedNetworking(parent, wifi) {
  // Persist tethering toggle
  auto tetheringPersistToggle = new ToggleControl(tr("Persist tethering across reboot"), "", "", params.getBool("PersistTetheringAcrossReboot"));
  connect(tetheringPersistToggle, &ToggleControl::toggleFlipped, [=](bool state) {
    params.putBool("PersistTetheringAcrossReboot", state);
  });
  // Insert it after tetheringToggle
  auto buttons = findChildren<QPushButton*>();
  auto tetheringToggleTitle = std::find_if(buttons.begin(), buttons.end(), [](QPushButton* btn) {
    return btn->text() == tr("Enable Tethering");
  });
  auto tetheringToggle = tetheringToggleTitle != buttons.end() ? (*tetheringToggleTitle)->parentWidget() : nullptr; // Toggle widget is the parent of the button label
  auto list = findChild<ListWidgetSP*>();
  if (tetheringToggle && list) {
    list->AddWidgetAt(list->indexOf(tetheringToggle) + 1, tetheringPersistToggle);
  }

  // Initialize tethering on startup
  if (params.getBool("TetheringEnabled") && params.getBool("PersistTetheringAcrossReboot")) {
    QTimer::singleShot(2000, this, [=] {
      qDebug() << "Re-enabling tethering on startup";
      wifi->setTetheringEnabled(true);
      tetheringToggle->setEnabled(true);
    });
  }
}

void AdvancedNetworkingSP::toggleTethering(bool enabled) {
  params.putBool("TetheringEnabled", enabled);
  AdvancedNetworking::toggleTethering(enabled);
}
