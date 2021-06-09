#include "networking.h"

#include <QDebug>
#include <QHBoxLayout>
#include <QLabel>
#include <QPixmap>

#include "selfdrive/ui/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/util.h"

// Networking functions

Networking::Networking(QWidget* parent, bool show_advanced) : QWidget(parent), show_advanced(show_advanced){
  s = new QStackedLayout;

  QLabel* warning = new QLabel("네트워크 관리자 비활성화됨!");
  warning->setAlignment(Qt::AlignCenter);
  warning->setStyleSheet(R"(font-size: 65px;)");

  s->addWidget(warning);
  setLayout(s);

  QTimer* timer = new QTimer(this);
  QObject::connect(timer, &QTimer::timeout, this, &Networking::refresh);
  timer->start(5000);
  attemptInitialization();
}

void Networking::attemptInitialization(){
  // Checks if network manager is active
  try {
    wifi = new WifiManager(this);
  } catch (std::exception &e) {
    return;
  }

  connect(wifi, &WifiManager::wrongPassword, this, &Networking::wrongPassword);

  QVBoxLayout* vlayout = new QVBoxLayout;

  if (show_advanced) {
    QPushButton* advancedSettings = new QPushButton("추가옵션");
    advancedSettings->setStyleSheet("margin-right: 30px;");
    advancedSettings->setFixedSize(350, 100);
    connect(advancedSettings, &QPushButton::released, [=](){ s->setCurrentWidget(an); });
    vlayout->addSpacing(10);
    vlayout->addWidget(advancedSettings, 0, Qt::AlignRight);
    vlayout->addSpacing(10);
  }

  wifiWidget = new WifiUI(this, wifi);
  connect(wifiWidget, &WifiUI::connectToNetwork, this, &Networking::connectToNetwork);
  vlayout->addWidget(new ScrollView(wifiWidget, this), 1);

  QWidget* wifiScreen = new QWidget(this);
  wifiScreen->setLayout(vlayout);
  s->addWidget(wifiScreen);

  an = new AdvancedNetworking(this, wifi);
  connect(an, &AdvancedNetworking::backPress, [=](){s->setCurrentWidget(wifiScreen);});
  s->addWidget(an);

  setStyleSheet(R"(
    QPushButton {
      font-size: 50px;
      margin: 0px;
      padding: 15px;
      border-width: 0;
      border-radius: 30px;
      color: #dddddd;
      background-color: #444444;
    }
    QPushButton:disabled {
      color: #777777;
      background-color: #222222;
    }
  )");
  s->setCurrentWidget(wifiScreen);
  ui_setup_complete = true;
}

void Networking::refresh(){
  if (!this->isVisible()) {
    return;
  }
  if (!ui_setup_complete) {
    attemptInitialization();
    if (!ui_setup_complete) {
      return;
    }
  }
  wifiWidget->refresh();
  an->refresh();
}

void Networking::connectToNetwork(Network n) {
  if (n.security_type == SecurityType::OPEN) {
    wifi->connect(n);
  } else if (n.security_type == SecurityType::WPA) {
    QString pass = InputDialog::getText(n.ssid + "의 패스워드를 입력하세요", 8);
    wifi->connect(n, pass);
  }
}

void Networking::wrongPassword(QString ssid) {
  for (Network n : wifi->seen_networks) {
    if (n.ssid == ssid) {
      QString pass = InputDialog::getText(n.ssid + " 잘못된 패스워드 입니다", 8);
      wifi->connect(n, pass);
      return;
    }
  }
}

// AdvancedNetworking functions

AdvancedNetworking::AdvancedNetworking(QWidget* parent, WifiManager* wifi): QWidget(parent), wifi(wifi){

  QVBoxLayout* vlayout = new QVBoxLayout;
  vlayout->setMargin(40);
  vlayout->setSpacing(20);

  // Back button
  QPushButton* back = new QPushButton("뒤로가기");
  back->setFixedSize(500, 100);
  connect(back, &QPushButton::released, [=](){emit backPress();});
  vlayout->addWidget(back, 0, Qt::AlignLeft);

  // Enable tethering layout
  ToggleControl *tetheringToggle = new ToggleControl("테더링 활성화", "", "", wifi->tetheringEnabled());
  vlayout->addWidget(tetheringToggle);
  QObject::connect(tetheringToggle, &ToggleControl::toggleFlipped, this, &AdvancedNetworking::toggleTethering);
  vlayout->addWidget(horizontal_line(), 0);

  // Change tethering password
  editPasswordButton = new ButtonControl("테더링 패스워드", "변경", "", [=](){
    QString pass = InputDialog::getText("Enter new tethering password", 8);
    if (pass.size()) {
      wifi->changeTetheringPassword(pass);
    }
  });
  vlayout->addWidget(editPasswordButton, 0);
  vlayout->addWidget(horizontal_line(), 0);

  // IP address
  ipLabel = new LabelControl("IP 주소", wifi->ipv4_address);
  vlayout->addWidget(ipLabel, 0);
  vlayout->addWidget(horizontal_line(), 0);

  // SSH keys
  vlayout->addWidget(new SshToggle());
  vlayout->addWidget(horizontal_line(), 0);
  vlayout->addWidget(new SshControl());

  vlayout->addStretch(1);
  setLayout(vlayout);
}

void AdvancedNetworking::refresh(){
  ipLabel->setText(wifi->ipv4_address);
  update();
}

void AdvancedNetworking::toggleTethering(bool enable) {
  if (enable) {
    wifi->enableTethering();
  } else {
    wifi->disableTethering();
  }
  editPasswordButton->setEnabled(!enable);
}


// WifiUI functions

WifiUI::WifiUI(QWidget *parent, WifiManager* wifi) : QWidget(parent), wifi(wifi) {
  vlayout = new QVBoxLayout;

  // Scan on startup
  QLabel *scanning = new QLabel("네트워크 검색 중");
  scanning->setStyleSheet(R"(font-size: 65px;)");
  vlayout->addWidget(scanning, 0, Qt::AlignCenter);
  vlayout->setSpacing(25);

  setLayout(vlayout);
}

void WifiUI::refresh() {
  wifi->request_scan();
  wifi->refreshNetworks();
  clearLayout(vlayout);

  connectButtons = new QButtonGroup(this); // TODO check if this is a leak
  QObject::connect(connectButtons, qOverload<QAbstractButton*>(&QButtonGroup::buttonClicked), this, &WifiUI::handleButton);

  int i = 0;
  for (Network &network : wifi->seen_networks) {
    QHBoxLayout *hlayout = new QHBoxLayout;
    hlayout->addSpacing(50);

    QLabel *ssid_label = new QLabel(QString::fromUtf8(network.ssid));
    ssid_label->setStyleSheet("font-size: 55px;");
    hlayout->addWidget(ssid_label, 1, Qt::AlignLeft);

    // TODO: don't use images for this
    // strength indicator
    unsigned int strength_scale = network.strength / 17;
    QPixmap pix("../assets/images/network_" + QString::number(strength_scale) + ".png");
    QLabel *icon = new QLabel();
    icon->setPixmap(pix.scaledToWidth(100, Qt::SmoothTransformation));
    icon->setSizePolicy(QSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed));
    hlayout->addWidget(icon, 0, Qt::AlignRight);

    // connect button
    QPushButton* btn = new QPushButton(network.security_type == SecurityType::UNSUPPORTED ? "연결불가" : (network.connected == ConnectedType::CONNECTED ? "연결됨" : (network.connected == ConnectedType::CONNECTING ? "연결중" : "연결")));
    btn->setDisabled(network.connected == ConnectedType::CONNECTED || network.connected == ConnectedType::CONNECTING || network.security_type == SecurityType::UNSUPPORTED);
    btn->setFixedWidth(350);
    hlayout->addWidget(btn, 0, Qt::AlignRight);

    connectButtons->addButton(btn, i);

    vlayout->addLayout(hlayout, 1);
    // Don't add the last horizontal line
    if (i+1 < wifi->seen_networks.size()) {
      vlayout->addWidget(horizontal_line(), 0);
    }
    i++;
  }
  vlayout->addStretch(3);
}

void WifiUI::handleButton(QAbstractButton* button) {
  QPushButton* btn = static_cast<QPushButton*>(button);
  Network n = wifi->seen_networks[connectButtons->id(btn)];
  emit connectToNetwork(n);
}
