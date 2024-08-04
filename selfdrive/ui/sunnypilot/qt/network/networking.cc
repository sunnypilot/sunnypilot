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

#include "selfdrive/ui/sunnypilot/qt/network/networking.h"

#include <algorithm>

#include <QHBoxLayout>
#include <QScrollBar>
#include <QStyle>
#include "selfdrive/ui/qt/widgets/ssh_keys.h"

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/qt/qt_window.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

static const int ICON_WIDTH = 49;

// Networking functions

NetworkingSP::NetworkingSP(QWidget* parent, bool show_advanced) : QFrame(parent) {
  main_layout = new QStackedLayout(this);

  wifi = new WifiManager(this);
  connect(wifi, &WifiManager::refreshSignal, this, &NetworkingSP::refresh);
  connect(wifi, &WifiManager::wrongPassword, this, &NetworkingSP::wrongPassword);

  wifiScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(wifiScreen);
  vlayout->setContentsMargins(20, 20, 20, 20);
  QHBoxLayout* hlayout = new QHBoxLayout();
  QPushButton* scanButton = new QPushButton(tr("Scan"));
  scanButton->setObjectName("scan_btn");
  scanButton->setFixedSize(400, 100);
  connect(wifi, &WifiManager::refreshSignal, this, [=]() { scanButton->setText(tr("Scan")); scanButton->setEnabled(true); });
  connect(scanButton, &QPushButton::clicked, [=]() { scanButton->setText(tr("Scanning...")); scanButton->setEnabled(false); wifi->requestScan(); });

  hlayout->addWidget(scanButton);
  hlayout->addStretch(1); // Pushes the button all the way to the left

  if (show_advanced) {
    hlayout->setSpacing(10);

    QPushButton* advancedSettings = new QPushButton(tr("Advanced"));
    advancedSettings->setObjectName("advanced_btn");
    advancedSettings->setFixedSize(400, 100);
    connect(advancedSettings, &QPushButton::clicked, [=]() { main_layout->setCurrentWidget(an); });
    hlayout->addWidget(advancedSettings);
  }

  vlayout->addLayout(hlayout);
  vlayout->addSpacing(10);

  wifiWidget = new WifiUISP(this, wifi);
  wifiWidget->setObjectName("wifiWidget");
  connect(wifiWidget, &WifiUISP::connectToNetwork, this, &NetworkingSP::connectToNetwork);

  ScrollView *wifiScroller = new ScrollView(wifiWidget, this);
  wifiScroller->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
  vlayout->addWidget(wifiScroller, 1);
  main_layout->addWidget(wifiScreen);

  an = new AdvancedNetworkingSP(this, wifi);
  connect(an, &AdvancedNetworkingSP::backPress, [=]() { main_layout->setCurrentWidget(wifiScreen); });
  connect(an, &AdvancedNetworkingSP::requestWifiScreen, [=]() { main_layout->setCurrentWidget(wifiScreen); });
  main_layout->addWidget(an);

  QPalette pal = palette();
  pal.setColor(QPalette::Window, QColor(0x29, 0x29, 0x29));
  setAutoFillBackground(true);
  setPalette(pal);

  setStyleSheet(R"(
    #wifiWidget > QPushButton, #back_btn, #advanced_btn, #scan_btn{
      font-size: 50px;
      margin: 0px;
      padding: 15px;
      border-width: 0;
      border-radius: 30px;
      color: #dddddd;
      background-color: #393939;
    }
    #back_btn:pressed, #advanced_btn:pressed, #scan_btn:pressed {
      background-color:  #4a4a4a;
    }
    #scan_btn:disabled {
      background-color: #121212;
      color: #33FFFFFF;
    }
  )");
  main_layout->setCurrentWidget(wifiScreen);
}

void NetworkingSP::refresh() {
  wifiWidget->refresh();
  an->refresh();
}

void NetworkingSP::connectToNetwork(const Network n) {
  if (wifi->isKnownConnection(n.ssid)) {
    wifi->activateWifiConnection(n.ssid);
  } else if (n.security_type == SecurityType::OPEN) {
    wifi->connect(n, false);
  } else if (n.security_type == SecurityType::WPA) {
    QString pass = InputDialog::getText(tr("Enter password"), this, tr("for \"%1\"").arg(QString::fromUtf8(n.ssid)), true, 8);
    if (!pass.isEmpty()) {
      wifi->connect(n, false, pass);
    }
  }
}

void NetworkingSP::wrongPassword(const QString &ssid) {
  if (wifi->seenNetworks.contains(ssid)) {
    const Network &n = wifi->seenNetworks.value(ssid);
    QString pass = InputDialog::getText(tr("Wrong password"), this, tr("for \"%1\"").arg(QString::fromUtf8(n.ssid)), true, 8);
    if (!pass.isEmpty()) {
      wifi->connect(n, false, pass);
    }
  }
}

void NetworkingSP::showEvent(QShowEvent *event) {
  wifi->start();
}

void NetworkingSP::hideEvent(QHideEvent *event) {
  main_layout->setCurrentWidget(wifiScreen);
  wifi->stop();
}

// AdvancedNetworkingSP functions

AdvancedNetworkingSP::AdvancedNetworkingSP(QWidget* parent, WifiManager* wifi): QWidget(parent), wifi(wifi) {

  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setMargin(40);
  main_layout->setSpacing(20);

  // Back button
  QPushButton* back = new QPushButton(tr("Back"));
  back->setObjectName("back_btn");
  back->setFixedSize(400, 100);
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidgetSP *list = new ListWidgetSP(this);
  // Enable tethering layout
  const bool set_hotspot_on_boot = params.getBool("HotspotOnBoot") && params.getBool("HotspotOnBootConfirmed");
  tetheringToggle = new ToggleControlSP(tr("Enable Tethering"), "", "", wifi->isTetheringEnabled() || set_hotspot_on_boot);
  list->addItem(tetheringToggle);
  QObject::connect(tetheringToggle, &ToggleControlSP::toggleFlipped, this, &AdvancedNetworkingSP::toggleTethering);

  hotspotOnBootToggle = new ToggleControlSP(
    tr("Retain hotspot/tethering state"),
    tr("Enabling this toggle will retain the hotspot/tethering toggle state across reboots."),
    "",
    params.getBool("HotspotOnBoot")
  );
  hotspotOnBootToggle->setEnabled(wifi->isTetheringEnabled() || set_hotspot_on_boot);
  QObject::connect(hotspotOnBootToggle, &ToggleControlSP::toggleFlipped, [=](bool state) {
    params.putBool("HotspotOnBoot", state);
  });
  list->addItem(hotspotOnBootToggle);

  // Change tethering password
  ButtonControlSP *editPasswordButton = new ButtonControlSP(tr("Tethering Password"), tr("EDIT"));
  connect(editPasswordButton, &ButtonControlSP::clicked, [=]() {
    QString pass = InputDialog::getText(tr("Enter new tethering password"), this, "", true, 8, wifi->getTetheringPassword());
    if (!pass.isEmpty()) {
      wifi->changeTetheringPassword(pass);
    }
  });
  list->addItem(editPasswordButton);

  // IP address
  ipLabel = new LabelControlSP(tr("IP Address"), wifi->ipv4_address);
  list->addItem(ipLabel);

  // SSH keys
  list->addItem(new SshToggle());
  list->addItem(new SshControl());

  // Roaming toggle
  const bool roamingEnabled = params.getBool("GsmRoaming");
  roamingToggle = new ToggleControlSP(tr("Enable Roaming"), "", "", roamingEnabled);
  QObject::connect(roamingToggle, &ToggleControlSP::toggleFlipped, [=](bool state) {
    params.putBool("GsmRoaming", state);
    wifi->updateGsmSettings(state, QString::fromStdString(params.get("GsmApn")), params.getBool("GsmMetered"));
  });
  list->addItem(roamingToggle);

  // APN settings
  editApnButton = new ButtonControlSP(tr("APN Setting"), tr("EDIT"));
  connect(editApnButton, &ButtonControlSP::clicked, [=]() {
    const QString cur_apn = QString::fromStdString(params.get("GsmApn"));
    QString apn = InputDialog::getText(tr("Enter APN"), this, tr("leave blank for automatic configuration"), false, -1, cur_apn).trimmed();

    if (apn.isEmpty()) {
      params.remove("GsmApn");
    } else {
      params.put("GsmApn", apn.toStdString());
    }
    wifi->updateGsmSettings(params.getBool("GsmRoaming"), apn, params.getBool("GsmMetered"));
  });
  list->addItem(editApnButton);

  // Metered toggle
  const bool metered = params.getBool("GsmMetered");
  meteredToggle = new ToggleControlSP(tr("Cellular Metered"), tr("Prevent large data uploads when on a metered connection"), "", metered);
  QObject::connect(meteredToggle, &SshToggle::toggleFlipped, [=](bool state) {
    params.putBool("GsmMetered", state);
    wifi->updateGsmSettings(params.getBool("GsmRoaming"), QString::fromStdString(params.get("GsmApn")), state);
  });
  list->addItem(meteredToggle);

  // Hidden Network
  hiddenNetworkButton = new ButtonControlSP(tr("Hidden Network"), tr("CONNECT"));
  connect(hiddenNetworkButton, &ButtonControlSP::clicked, [=]() {
    QString ssid = InputDialog::getText(tr("Enter SSID"), this, "", false, 1);
    if (!ssid.isEmpty()) {
      QString pass = InputDialog::getText(tr("Enter password"), this, tr("for \"%1\"").arg(ssid), true, -1);
      Network hidden_network;
      hidden_network.ssid = ssid.toUtf8();
      if (!pass.isEmpty()) {
        hidden_network.security_type = SecurityType::WPA;
        wifi->connect(hidden_network, true, pass);
      } else {
        wifi->connect(hidden_network, true);
      }
      emit requestWifiScreen();
    }
  });
  list->addItem(hiddenNetworkButton);

  // Ngrok
  QProcess process;
  process.start("sudo service ngrok status | grep running");
  process.waitForFinished();
  QString output = QString(process.readAllStandardOutput());
  bool ngrokRunning = !output.isEmpty();
  ToggleControlSP *ngrokToggle = new ToggleControlSP(tr("Ngrok Service"), "", "", ngrokRunning);
  connect(ngrokToggle, &ToggleControlSP::toggleFlipped, [=](bool state) {
    if (state) std::system("sudo ngrok service start");
    else std::system("sudo ngrok service stop");
  });
  list->addItem(ngrokToggle);

  // Set initial config
  wifi->updateGsmSettings(roamingEnabled, QString::fromStdString(params.get("GsmApn")), metered);

  connect(uiState(), &UIState::primeTypeChanged, this, [=](PrimeType prime_type) {
    bool gsmVisible = prime_type == PrimeType::NONE || prime_type == PrimeType::LITE;
    roamingToggle->setVisible(gsmVisible);
    editApnButton->setVisible(gsmVisible);
    meteredToggle->setVisible(gsmVisible);
  });

  main_layout->addWidget(new ScrollView(list, this));
  main_layout->addStretch(1);
}

void AdvancedNetworkingSP::refresh() {
  ipLabel->setText(wifi->ipv4_address);
  tetheringToggle->setEnabled(true);
  update();
}

void AdvancedNetworkingSP::toggleTethering(bool enabled) {
  params.putBool("HotspotOnBootConfirmed", enabled);
  wifi->setTetheringEnabled(enabled);
  tetheringToggle->setEnabled(false);

  hotspotOnBootToggle->setEnabled(enabled);
  if (!enabled) {
    params.remove("HotspotOnBoot");
  }
}

// WifiUISP functions

WifiUISP::WifiUISP(QWidget *parent, WifiManager* wifi) : QWidget(parent), wifi(wifi) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(0, 0, 0, 0);
  main_layout->setSpacing(0);

  // load imgs
  for (const auto &s : {"low", "medium", "high", "full"}) {
    QPixmap pix(ASSET_PATH + "/offroad/icon_wifi_strength_" + s + ".svg");
    strengths.push_back(pix.scaledToHeight(68, Qt::SmoothTransformation));
  }
  lock = QPixmap(ASSET_PATH + "offroad/icon_lock_closed.svg").scaledToWidth(ICON_WIDTH, Qt::SmoothTransformation);
  checkmark = QPixmap(ASSET_PATH + "offroad/icon_checkmark.svg").scaledToWidth(ICON_WIDTH, Qt::SmoothTransformation);
  circled_slash = QPixmap(ASSET_PATH + "img_circled_slash.svg").scaledToWidth(ICON_WIDTH, Qt::SmoothTransformation);

  scanningLabel = new QLabel(tr("Scanning for networks..."));
  scanningLabel->setStyleSheet("font-size: 65px;");
  main_layout->addWidget(scanningLabel, 0, Qt::AlignCenter);

  wifi_list_widget = new ListWidgetSP(this);
  wifi_list_widget->setVisible(false);
  main_layout->addWidget(wifi_list_widget);

  setStyleSheet(R"(
    QScrollBar::handle:vertical {
      min-height: 0px;
      border-radius: 4px;
      background-color: #8A8A8A;
    }
    #forgetBtn {
      font-size: 32px;
      font-weight: 600;
      color: #292929;
      background-color: #BDBDBD;
      border-width: 1px solid #828282;
      border-radius: 5px;
      padding: 40px;
      padding-bottom: 16px;
      padding-top: 16px;
    }
    #forgetBtn:pressed {
      background-color: #828282;
    }
    #connecting {
      font-size: 32px;
      font-weight: 600;
      color: white;
      border-radius: 0;
      padding: 27px;
      padding-left: 43px;
      padding-right: 43px;
      background-color: black;
    }
    #ssidLabel {
      text-align: left;
      border: none;
      padding-top: 50px;
      padding-bottom: 50px;
    }
    #ssidLabel:disabled {
      color: #696969;
    }
  )");
}

void WifiUISP::refresh() {
  bool is_empty = wifi->seenNetworks.isEmpty();
  scanningLabel->setVisible(is_empty);
  wifi_list_widget->setVisible(!is_empty);
  if (is_empty) return;

  setUpdatesEnabled(false);

  const bool is_tethering_enabled = wifi->isTetheringEnabled();
  QList<Network> sortedNetworks = wifi->seenNetworks.values();
  std::sort(sortedNetworks.begin(), sortedNetworks.end(), compare_by_strength);

  int n = 0;
  for (Network &network : sortedNetworks) {
    QPixmap status_icon;
    if (network.connected == ConnectedType::CONNECTED) {
      status_icon = checkmark;
    } else if (network.security_type == SecurityType::UNSUPPORTED) {
      status_icon = circled_slash;
    } else if (network.security_type == SecurityType::WPA) {
      status_icon = lock;
    }
    bool show_forget_btn = wifi->isKnownConnection(network.ssid) && !is_tethering_enabled;
    QPixmap strength = strengths[strengthLevel(network.strength)];

    auto item = getItem(n++);
    item->setItem(network, status_icon, show_forget_btn, strength);
    item->setVisible(true);
  }
  for (; n < wifi_items.size(); ++n) wifi_items[n]->setVisible(false);

  setUpdatesEnabled(true);
}

WifiItemSP *WifiUISP::getItem(int n) {
  auto item = n < wifi_items.size() ? wifi_items[n] : wifi_items.emplace_back(new WifiItemSP(tr("CONNECTING..."), tr("FORGET")));
  if (!item->parentWidget()) {
    QObject::connect(item, &WifiItemSP::connectToNetwork, this, &WifiUISP::connectToNetwork);
    QObject::connect(item, &WifiItemSP::forgotNetwork, [this](const Network n) {
      if (ConfirmationDialog::confirm(tr("Forget Wi-Fi Network \"%1\"?").arg(QString::fromUtf8(n.ssid)), tr("Forget"), this))
        wifi->forgetConnection(n.ssid);
    });
    wifi_list_widget->addItem(item);
  }
  return item;
}

// WifiItemSP

WifiItemSP::WifiItemSP(const QString &connecting_text, const QString &forget_text, QWidget *parent) : QWidget(parent) {
  QHBoxLayout *hlayout = new QHBoxLayout(this);
  hlayout->setContentsMargins(44, 0, 73, 0);
  hlayout->setSpacing(50);

  hlayout->addWidget(ssidLabel = new ElidedLabelSP());
  ssidLabel->setObjectName("ssidLabel");
  ssidLabel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
  hlayout->addWidget(connecting = new QPushButton(connecting_text), 0, Qt::AlignRight);
  connecting->setObjectName("connecting");
  hlayout->addWidget(forgetBtn = new QPushButton(forget_text), 0, Qt::AlignRight);
  forgetBtn->setObjectName("forgetBtn");
  hlayout->addWidget(iconLabel = new QLabel(), 0, Qt::AlignRight);
  hlayout->addWidget(strengthLabel = new QLabel(), 0, Qt::AlignRight);

  iconLabel->setFixedWidth(ICON_WIDTH);
  QObject::connect(forgetBtn, &QPushButton::clicked, [this]() { emit forgotNetwork(network); });
  QObject::connect(ssidLabel, &ElidedLabelSP::clicked, [this]() {
    if (network.connected == ConnectedType::DISCONNECTED) emit connectToNetwork(network);
  });
}

void WifiItemSP::setItem(const Network &n, const QPixmap &status_icon, bool show_forget_btn, const QPixmap &strength_icon) {
  network = n;

  ssidLabel->setText(n.ssid);
  ssidLabel->setEnabled(n.security_type != SecurityType::UNSUPPORTED);
  ssidLabel->setFont(InterFont(55, network.connected == ConnectedType::DISCONNECTED ? QFont::Normal : QFont::Bold));

  connecting->setVisible(n.connected == ConnectedType::CONNECTING);
  forgetBtn->setVisible(show_forget_btn);

  iconLabel->setPixmap(status_icon);
  strengthLabel->setPixmap(strength_icon);
}
