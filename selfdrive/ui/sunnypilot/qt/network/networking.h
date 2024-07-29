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

#pragma once

#include <QWidget>
#include <vector>

#include "selfdrive/ui/qt/network/wifi_manager.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class WifiItemSP : public QWidget {
  Q_OBJECT
public:
  explicit WifiItemSP(const QString &connecting_text, const QString &forget_text, QWidget* parent = nullptr);
  void setItem(const Network& n, const QPixmap &icon, bool show_forget_btn, const QPixmap &strength);

signals:
  // Cannot pass Network by reference. it may change after the signal is sent.
  void connectToNetwork(const Network n);
  void forgotNetwork(const Network n);

protected:
  ElidedLabelSP* ssidLabel;
  QPushButton* connecting;
  QPushButton* forgetBtn;
  QLabel* iconLabel;
  QLabel* strengthLabel;
  Network network;
};

class WifiUISP : public QWidget {
  Q_OBJECT

public:
  explicit WifiUISP(QWidget *parent = 0, WifiManager* wifi = 0);

private:
  WifiItemSP *getItem(int n);

  WifiManager *wifi = nullptr;
  QLabel *scanningLabel = nullptr;
  QPixmap lock;
  QPixmap checkmark;
  QPixmap circled_slash;
  QVector<QPixmap> strengths;
  ListWidgetSP *wifi_list_widget = nullptr;
  std::vector<WifiItemSP*> wifi_items;

signals:
  void connectToNetwork(const Network n);

public slots:
  void refresh();
};

class AdvancedNetworkingSP : public QWidget {
  Q_OBJECT
public:
  explicit AdvancedNetworkingSP(QWidget* parent = 0, WifiManager* wifi = 0);

private:
  LabelControlSP* ipLabel;
  ToggleControlSP* tetheringToggle;
  ToggleControlSP* roamingToggle;
  ButtonControlSP* editApnButton;
  ButtonControlSP* hiddenNetworkButton;
  ToggleControlSP* meteredToggle;
  WifiManager* wifi = nullptr;
  Params params;

  ToggleControlSP* hotspotOnBootToggle;

signals:
  void backPress();
  void requestWifiScreen();

public slots:
  void toggleTethering(bool enabled);
  void refresh();
};

class NetworkingSP : public QFrame {
  Q_OBJECT

public:
  explicit NetworkingSP(QWidget* parent = 0, bool show_advanced = true);
  WifiManager* wifi = nullptr;

private:
  QStackedLayout* main_layout = nullptr;
  QWidget* wifiScreen = nullptr;
  AdvancedNetworkingSP* an = nullptr;
  WifiUISP* wifiWidget;

  void showEvent(QShowEvent* event) override;
  void hideEvent(QHideEvent* event) override;

public slots:
  void refresh();

private slots:
  void connectToNetwork(const Network n);
  void wrongPassword(const QString &ssid);
};
