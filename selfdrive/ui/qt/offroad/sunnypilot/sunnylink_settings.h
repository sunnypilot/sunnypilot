#pragma once

#include <QApplication>
#include <QJsonArray>
#include <QJsonDocument>
#include <QtCore/qjsonobject.h>

#include <QrCode.hpp>

#include "common/watchdog.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/request_repeater.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

// sponsor QR code
class SunnylinkSponsorQRWidget : public QWidget {
  Q_OBJECT

public:
  explicit SunnylinkSponsorQRWidget(QWidget* parent = 0);
  void paintEvent(QPaintEvent*) override;

private:
  QPixmap img;
  QTimer *timer;
  void updateQrCode(const QString &text);
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent *event) override;

private slots:
  void refresh();
};


// sponsor popup widget
class SunnylinkSponsorPopup : public DialogBase {
  Q_OBJECT

public:
  explicit SunnylinkSponsorPopup(QWidget* parent);
};

class BackupSettings : public QFrame {
  Q_OBJECT

public:
  explicit BackupSettings(QWidget *parent = nullptr);
  void sendParams(const QByteArray &payload);
  void getParams();
  QByteArray backupParams(const bool encrypt = true);
  void restoreParams(const QString &resp);
  void started();
  void finished();
  bool in_progress = false;

signals:
  void updateLabels();

private:
  Params params;
};

class SunnylinkPanel : public QFrame {
  Q_OBJECT

public:
  explicit SunnylinkPanel(QWidget *parent = nullptr);
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent *event) override;

public slots:
  void updateLabels();

private:
  void getSubscriber(bool poll = false);
  void replyFinished(const QString &response, bool success);

  QStackedLayout* main_layout = nullptr;
  QWidget* sunnylinkScreen = nullptr;
  ScrollView *scrollView = nullptr;
  RequestRepeater* sub_repeater = nullptr;
  HttpRequest* init_sub_request = nullptr;

  LabelControl *sunnylinkId;
  BackupSettings *backup_settings;
  SubPanelButton *restoreSettings;
  SubPanelButton *backupSettings;
  SunnylinkSponsorPopup *popup;
  ButtonControl* sponsorBtn;

  bool is_onroad = false;
  bool is_backup = false;
  bool is_restore = false;
};
