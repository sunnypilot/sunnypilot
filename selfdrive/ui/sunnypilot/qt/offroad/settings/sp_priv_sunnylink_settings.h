#pragma once

#include <QtCore/qjsonobject.h>

#include <QrCode.hpp>
#include "selfdrive/ui/sunnypilot/qt/network/sunnylink/sp_priv_sunnylink_client.h"

#include "selfdrive/ui/sunnypilot/sp_priv_ui.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/sp_priv_scrollview.h"

const QString SUNNYLINK_BASE_URL = util::getenv("SUNNYLINK_API_HOST", "https://stg.api.sunnypilot.ai").c_str();
// sponsor QR code
class SunnylinkSponsorQRWidget : public QWidget {
  Q_OBJECT

public:
  explicit SunnylinkSponsorQRWidget(bool sponsor_pair = false, QWidget* parent = 0);
  void paintEvent(QPaintEvent*) override;

private:
  QPixmap img;
  QTimer *timer;
  void updateQrCode(const QString &text);
  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent *event) override;

  bool sponsor_pair = false;

private slots:
  void refresh();
};


// sponsor popup widget
class SunnylinkSponsorPopup : public DialogBase {
  Q_OBJECT

public:
  explicit SunnylinkSponsorPopup(bool sponsor_pair = false, QWidget* parent = 0);

private:
  static QStringList getInstructions(bool sponsor_pair);
  bool sponsor_pair = false;
};

class BackupSettings : public QFrame {
  Q_OBJECT

public:
  explicit BackupSettings(QWidget *parent = nullptr);
  void sendParams(const QByteArray &payload);
  void getParams();
  QByteArray backupParams(bool encrypt = true);
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
  void paramsRefresh(const QString&param_name, const QString&param_value);

public slots:
  void updateLabels();

private:

  ParamControlSP* sunnylinkEnabledBtn;
  QStackedLayout* main_layout = nullptr;
  QWidget* sunnylinkScreen = nullptr;
  ScrollViewSP *scrollView = nullptr;

  BackupSettings *backup_settings;
  SubPanelButton *restoreSettings;
  SubPanelButton *backupSettings;
  SunnylinkSponsorPopup *status_popup;
  SunnylinkSponsorPopup *pair_popup;
  ButtonControlSP* sponsorBtn;
  ButtonControlSP* pairSponsorBtn;
  SunnylinkClient* sunnylink_client;

  bool is_onroad = false;
  bool is_backup = false;
  bool is_restore = false;
  bool is_sunnylink_enabled = false;
  ParamWatcher *param_watcher;
  QString sunnylinkBtnDescription;
  void stopSunnylink() const;
  void startSunnylink() const;
};
