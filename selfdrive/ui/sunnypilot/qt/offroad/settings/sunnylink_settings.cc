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

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnylink_settings.h"
#include "selfdrive/ui/sunnypilot/qt/api.h"

#include <map>
#include <string>

#include <QtConcurrent>

#include <common/watchdog.h>

SunnylinkPanel::SunnylinkPanel(QWidget* parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);
  sunnylink_client = new SunnylinkClient(this);
  param_watcher = new ParamWatcher(this);
  param_watcher->addParam("SunnylinkEnabled");
  connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    paramsRefresh(param_name, param_value);
  });

  is_sunnylink_enabled = Params().getBool("SunnylinkEnabled");
  connect(uiStateSP(), &UIStateSP::sunnylinkRolesChanged, this, &SunnylinkPanel::updateLabels);
  connect(uiStateSP(), &UIStateSP::sunnylinkDeviceUsersChanged, this, &SunnylinkPanel::updateLabels);

  auto list = new ListWidgetSP(this, false);
  sunnylinkEnabledBtn = new ParamControlSP(
    "SunnylinkEnabled",
    tr("Enable sunnylink"),
    sunnylinkBtnDescription,
    "../assets/offroad/icon_blank.png");
  sunnylinkEnabledBtn->setValue(tr("Device ID ")+ getSunnylinkDongleId().value_or(tr("N/A")));

  list->addItem(sunnylinkEnabledBtn);
  list->addItem(horizontal_line());

  sunnylinkBtnDescription = tr("This is the master switch, it will allow you to cutoff any sunnylink requests should you want to do that.");
  connect(sunnylinkEnabledBtn, &ParamControlSP::showDescriptionEvent, [=]() {
    //resets the description to the default one for the easter egg
    sunnylinkEnabledBtn->setDescription(sunnylinkBtnDescription);
  });

  connect(sunnylinkEnabledBtn, &ParamControlSP::toggleFlipped, [=](bool enabled) {
    if (enabled) {
      auto proud_description = "<font color='SeaGreen'>"+ tr("🎉Welcome back! We're excited to see you've enabled sunnylink again! 🚀")+ "</font>";
      sunnylinkEnabledBtn->showDescription();
      sunnylinkEnabledBtn->setDescription(proud_description);
    } else {
      auto shame_description = "<font color='orange'>"+ tr("👋Not going to lie, it's sad to see you disabled sunnylink 😢, but we'll be here when you're ready to come back 🎉.")+ "</font>";
      sunnylinkEnabledBtn->showDescription();
      sunnylinkEnabledBtn->setDescription(shame_description);
    }

    updateLabels();
  });

  status_popup = new SunnylinkSponsorPopup(false, this);
  sponsorBtn = new ButtonControlSP(
    tr("Sponsor Status"), tr("SPONSOR"),
    tr("Become a sponsor of sunnypilot to get early access to sunnylink features when they become available."));
  list->addItem(sponsorBtn);
  connect(sponsorBtn, &ButtonControlSP::clicked, [=]() {
    status_popup->exec();
  });
  list->addItem(horizontal_line());

  pair_popup = new SunnylinkSponsorPopup(true, this);
  pairSponsorBtn = new ButtonControlSP(
    tr("Pair GitHub Account"), tr("PAIR"),
    tr("Pair your GitHub account to grant your device sponsor benefits, including API access on sunnylink.") + "🌟");
  list->addItem(pairSponsorBtn);
  connect(pairSponsorBtn, &ButtonControlSP::clicked, [=]() {
    if (getSunnylinkDongleId().value_or(tr("N/A")) == "N/A") {
      ConfirmationDialog::alert(tr("sunnylink Dongle ID not found. This may be due to weak internet connection or sunnylink registration issue. Please reboot and try again."), this);
    } else {
      pair_popup->exec();
    }
  });
  list->addItem(horizontal_line());

  list->addItem(new LabelControlSP(tr("Manage Settings")));

  backup_settings = new BackupSettings;

  // Backup Settings
  backupSettings = new SubPanelButton(tr("Backup Settings"), 720, this);
  backupSettings->setObjectName("backup_btn");
  // Set margin on the outside of the button
  auto backupSettingsLayout = new QVBoxLayout;
  backupSettingsLayout->setContentsMargins(0, 0, 0, 30);
  backupSettingsLayout->addWidget(backupSettings);
  connect(backupSettings, &QPushButton::clicked, [=]() {
    is_backup = true;
    backup_settings->started();
    if (ConfirmationDialog::confirm(tr("Are you sure you want to backup sunnypilot settings?"), tr("Back Up"), this)) {
      backup_settings->sendParams(backup_settings->backupParams());
    } else {
      backup_settings->finished();
    }
    is_backup = false;
  });
  connect(backup_settings, &BackupSettings::updateLabels, this, &SunnylinkPanel::updateLabels);

  // Restore Settings
  restoreSettings = new SubPanelButton(tr("Restore Settings"), 720, this);
  restoreSettings->setObjectName("restore_btn");
  // Set margin on the outside of the button
  auto restoreSettingsLayout = new QVBoxLayout;
  restoreSettingsLayout->setContentsMargins(0, 0, 0, 30);
  restoreSettingsLayout->addWidget(restoreSettings);
  connect(restoreSettings, &QPushButton::clicked, [=]() {
    is_restore = true;
    backup_settings->started();
    if (ConfirmationDialog::confirm(tr("Are you sure you want to restore the last backed up sunnypilot settings?"), tr("Restore"), this)) {
      backup_settings->getParams();
    } else {
      backup_settings->finished();
    }
    is_restore = false;
  });
  connect(backup_settings, &BackupSettings::updateLabels, this, &SunnylinkPanel::updateLabels);

  // Settings Restore and Settings Backup in the same horizontal space
  auto settings_layout = new QHBoxLayout;
  settings_layout->setContentsMargins(0, 0, 0, 30);
  settings_layout->addWidget(backupSettings);
  settings_layout->addSpacing(10);
  settings_layout->addWidget(restoreSettings);
  settings_layout->setAlignment(Qt::AlignLeft);
  list->addItem(settings_layout);

  connect(uiStateSP(), &UIStateSP::offroadTransition, [=](bool offroad) {
    is_onroad = !offroad;
    updateLabels();
  });

  sunnylinkScreen = new QWidget(this);
  auto vlayout = new QVBoxLayout(sunnylinkScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  vlayout->addWidget(new ScrollViewSP(list, this), 1);
  main_layout->addWidget(sunnylinkScreen);
  if (is_sunnylink_enabled) {
    startSunnylink();
  }
  updateLabels();
}

void SunnylinkPanel::showEvent(QShowEvent* event) {
  if (is_sunnylink_enabled)  {
    startSunnylink();
  }
  updateLabels();  // For snappier feeling
}

void SunnylinkPanel::paramsRefresh(const QString &param_name, const QString &param_value) {
  // We do it on paramsRefresh because the toggleEvent happens before the value is updated
  if (param_name == "SunnylinkEnabled" && param_value == "1") {
    startSunnylink();
  } else if (param_name == "SunnylinkEnabled" && param_value == "0") {
    stopSunnylink();
  }

  updateLabels();
}

void SunnylinkPanel::startSunnylink() const {
  if (!sunnylink_client->role_service->isCurrentyPolling()) {
    sunnylink_client->role_service->startPolling();
  } else {
    sunnylink_client->role_service->load();
  }

  if (!sunnylink_client->user_service->isCurrentyPolling()) {
    sunnylink_client->user_service->startPolling();
  } else {
    sunnylink_client->user_service->load();
  }
}

void SunnylinkPanel::stopSunnylink() const {
  sunnylink_client->role_service->stopPolling();
  sunnylink_client->user_service->stopPolling();
}

void SunnylinkPanel::updateLabels() {
  if (!isVisible()) {
    return;
  }

  is_sunnylink_enabled = Params().getBool("SunnylinkEnabled");
  const auto sunnylinkDongleId = getSunnylinkDongleId().value_or(tr("N/A"));
  bool is_sub = uiStateSP()->isSunnylinkSponsor() && is_sunnylink_enabled;
  auto max_current_sponsor_rule = uiStateSP()->sunnylinkSponsorRole();
  auto role_name = max_current_sponsor_rule.getSponsorTierString();
  std::optional role_color = max_current_sponsor_rule.getSponsorTierColor();
  bool is_paired = uiStateSP()->isSunnylinkPaired();
  auto paired_users = uiStateSP()->sunnylinkDeviceUsers();

  sunnylinkEnabledBtn->setEnabled(!is_onroad);
  sunnylinkEnabledBtn->setValue(tr("Device ID ")+ sunnylinkDongleId);

  sponsorBtn->setEnabled(!is_onroad && is_sunnylink_enabled);
  sponsorBtn->setText(is_sub ? tr("THANKS") + " ❤️" : tr("SPONSOR"));
  sponsorBtn->setValue(is_sub ? tr(role_name.toStdString().c_str()) : tr("Not Sponsor"), role_color);

  pairSponsorBtn->setEnabled(!is_onroad && is_sunnylink_enabled);
  pairSponsorBtn->setValue(is_paired ? tr("Paired") : tr("Not Paired"));

  backupSettings->setEnabled(!backup_settings->in_progress && !is_onroad && is_sunnylink_enabled);
  restoreSettings->setEnabled(!backup_settings->in_progress && !is_onroad && is_sunnylink_enabled);

  backupSettings->setText(backup_settings->in_progress && is_backup ? tr("Backing up...") : tr("Backup Settings"));
  restoreSettings->setText(backup_settings->in_progress && is_restore ? tr("Restoring...") : tr("Restore Settings"));

  if (!is_sunnylink_enabled) {
    sunnylinkEnabledBtn->setValue("");
    sponsorBtn->setValue("");
    pairSponsorBtn->setValue("");
  }

  update();
}

BackupSettings::BackupSettings(QWidget* parent) : QFrame(parent) {
}

QByteArray BackupSettings::backupParams(const bool encrypt) {
  // Call the readAll() method from the Params class to get all parameters.
  std::map<std::string, std::string> allParams = params.readAll();

  // Create a QJsonObject.
  QJsonObject payload;

  // Iterate over the map returned by readAll().
  QJsonObject converted_params;
  for (const auto& kv : allParams) {
    if ( !(params.getKeyType(kv.first) & BACKUP) )
      continue;  // Skip this iteration if the key does not have the BACKUP flag

    // For each key-value pair in the map, add an entry to the QJsonObject.
    converted_params.insert(QString::fromStdString(kv.first), QString::fromStdString(kv.second));
  }

  // Convert the QJsonObject to a QJsonDocument.
  QJsonDocument jsonDoc(converted_params);

  // Convert the QJsonDocument to a QByteArray.
  QByteArray jsonData = jsonDoc.toJson();

  // Compress the QByteArray.
  QByteArray compressedData = qCompress(jsonData);

  QByteArray processed_data = encrypt ? SunnylinkApi::rsa_encrypt(compressedData) : compressedData;

  // Encode the compressed QByteArray in Base64.
  auto converted_params_processed_base64_data = QString(processed_data.toBase64());

  payload["is_encrypted"] = encrypt;
  payload["config"] = converted_params_processed_base64_data;
  // Create a sub-object for sunnypilot_version
  QJsonObject version;
  QStringList versioning = getVersion().split('.');
  version["major"] = versioning.value(0, nullptr).toInt();
  version["minor"] = versioning.value(1, nullptr).toInt();
  version["patch"] = versioning.value(2, nullptr).toInt();
  version["build"] = versioning.value(3, nullptr).toInt();
  version["branch"] = QString::fromStdString(params.get("GitBranch"));
  payload["sunnypilot_version"] = version;

  // Convert the QJsonObject payload to QByteArray
  QByteArray payloadData = QJsonDocument(payload).toJson();

  return payloadData;
}

void BackupSettings::sendParams(const QByteArray &payload) {
  if (auto sl_dongle_id = getSunnylinkDongleId()) {
    QString url = SUNNYLINK_BASE_URL + "/backup/" + *sl_dongle_id;
    auto request = new HttpRequestSP(this, true, 10000, true);
    connect(request, &HttpRequestSP::requestDone, [=](const QString &resp, bool success) {
      if (success && resp != "[]") {
        ConfirmationDialog::alert(tr("Settings backed up for sunnylink Device ID:") + " " + *sl_dongle_id, this);
      } else if (resp == "[]") {
        ConfirmationDialog::alert(tr("Settings updated successfully, but no additional data was returned by the server."), this);
      } else {
        ConfirmationDialog::alert(tr("OOPS! We made a booboo.") + "\n" + tr("Please try again later."), this);
      }

      connect(request, &QObject::destroyed, this, &BackupSettings::finished);

      request->deleteLater();
    });

    request->sendRequest(url, HttpRequest::Method::PUT, payload);
  }
}

void BackupSettings::restoreParams(const QString &resp) {
  // Convert the response QString to a QByteArray
  QByteArray jsonData = resp.toUtf8();

  // Parse the JSON data into a QJsonDocument
  QJsonDocument jsonDoc = QJsonDocument::fromJson(jsonData);

  // Check if the JSON document is an object
  if (jsonDoc.isObject()) {
    // Convert the JSON document to a QJsonObject
    QJsonObject jsonObject = jsonDoc.object();

    // Get the "config" object from the JSON object
    const QJsonValue configValue = jsonObject.value("config");
    const QJsonValue isEncryptedValue = jsonObject.value("is_encrypted");

    const bool isEncrypted = isEncryptedValue.isBool() && isEncryptedValue.toBool();
    // Check if the "config" key exists and its value is a string
    if (configValue.isString()) {
      // Decode the Base64-encoded "config" value
      const QByteArray configJsonDataDecoded = QByteArray::fromBase64(configValue.toString().toUtf8());
      const QByteArray configJsonDataCompressed = isEncrypted ? SunnylinkApi::rsa_decrypt(configJsonDataDecoded) : configJsonDataDecoded;
      const QByteArray configJsonData = qUncompress(configJsonDataCompressed);

      // Convert the decompressed JSON data to a QJsonDocument
      const QJsonDocument configJsonDoc = QJsonDocument::fromJson(configJsonData);

      // Get the QJsonObject from the QJsonDocument
      QJsonObject configJsonObject = configJsonDoc.object();

      // Iterate over the "config" QJsonObject and process the data
      for (auto it = configJsonObject.begin(); it != configJsonObject.end(); ++it) {
        if ( !(params.getKeyType(it.key().toStdString()) & BACKUP) )
          continue;  // Skip this iteration if the key does not have the BACKUP flag

        // Process each key-value pair as needed
        params.put(it.key().toStdString(), it.value().toString().toStdString());
      }
    } else {
      qDebug() << "Error: 'config' value is not a string or 'config' key not found";
    }
  } else {
    qDebug() << "Error: JSON document is not an object";
  }
}

void BackupSettings::getParams() {
  if (auto sl_dongle_id = getSunnylinkDongleId()) {
    QString url = SUNNYLINK_BASE_URL + "/backup/" + *sl_dongle_id;
    auto request = new HttpRequestSP(this, true, 10000, true);
    connect(request, &HttpRequestSP::requestDone, [=](const QString &resp, bool success) {
      bool restart_ui = false;
      if (success && resp != "[]") {
        restoreParams(resp);
        ConfirmationDialog::alert(tr("Settings restored. Confirm to restart the interface."), this);
        restart_ui = true;
      } else if (resp == "[]") {
        ConfirmationDialog::alert(tr("No settings found to restore."), this);
      } else {
        ConfirmationDialog::alert(tr("OOPS! We made a booboo.") + "\n" + tr("Please try again later."), this);
      }

      connect(request, &QObject::destroyed, [=]() {
        finished();

        if (restart_ui) {
          qApp->exit(18);
          watchdog_kick(0);
        }
      });

      request->deleteLater();
    });

    request->sendRequest(url);
  }
}

void BackupSettings::started() {
  in_progress = true;
  emit updateLabels();
}

void BackupSettings::finished() {
  in_progress = false;
  emit updateLabels();
}

// Sponsor Upsell
using qrcodegen::QrCode;

SunnylinkSponsorQRWidget::SunnylinkSponsorQRWidget(bool sponsor_pair, QWidget* parent) : QWidget(parent), sponsor_pair(sponsor_pair) {
  timer = new QTimer(this);
  connect(timer, &QTimer::timeout, this, &SunnylinkSponsorQRWidget::refresh);
}

void SunnylinkSponsorQRWidget::showEvent(QShowEvent *event) {
  refresh();
  timer->start(5 * 60 * 1000);
  device()->setOffroadBrightness(100);
}

void SunnylinkSponsorQRWidget::hideEvent(QHideEvent *event) {
  timer->stop();
  device()->setOffroadBrightness(BACKLIGHT_OFFROAD);
}

void SunnylinkSponsorQRWidget::refresh() {
  QString qrString;

  if (sponsor_pair) {
    QString token = SunnylinkApi::create_jwt({}, 3600, true);
    auto sl_dongle_id = getSunnylinkDongleId();
    QByteArray payload = QString("1|" + sl_dongle_id.value_or("") + "|" + token).toUtf8().toBase64();
    qrString = SUNNYLINK_BASE_URL + "/sso?state=" + payload;
  } else {
    qrString = "https://github.com/sponsors/sunnyhaibin";
  }

  this->updateQrCode(qrString);
  update();
}

void SunnylinkSponsorQRWidget::updateQrCode(const QString &text) {
  QrCode qr = QrCode::encodeText(text.toUtf8().data(), QrCode::Ecc::LOW);
  qint32 sz = qr.getSize();
  QImage im(sz, sz, QImage::Format_RGB32);

  QRgb black = qRgb(0, 0, 0);
  QRgb white = qRgb(255, 255, 255);
  for (int y = 0; y < sz; y++) {
    for (int x = 0; x < sz; x++) {
      im.setPixel(x, y, qr.getModule(x, y) ? black : white);
    }
  }

  // Integer division to prevent anti-aliasing
  int final_sz = ((width() / sz) - 1) * sz;
  img = QPixmap::fromImage(im.scaled(final_sz, final_sz, Qt::KeepAspectRatio), Qt::MonoOnly);
}

void SunnylinkSponsorQRWidget::paintEvent(QPaintEvent *e) {
  QPainter p(this);
  p.fillRect(rect(), Qt::white);

  QSize s = (size() - img.size()) / 2;
  p.drawPixmap(s.width(), s.height(), img);
}

QStringList SunnylinkSponsorPopup::getInstructions(bool sponsor_pair) {
  QStringList instructions;
  if (sponsor_pair) {
    instructions << tr("Scan the QR code to login to your GitHub account")
                 << tr("Follow the prompts to complete the pairing process")
                 << tr("Re-enter the \"sunnylink\" panel to verify sponsorship status")
                 << tr("If sponsorship status was not updated, please contact a moderator on Discord at https://discord.gg/sunnypilot");
  } else {
    instructions << tr("Scan the QR code to visit sunnyhaibin's GitHub Sponsors page")
                 << tr("Choose your sponsorship tier and confirm your support")
                 << tr("Join our community on Discord at https://discord.gg/sunnypilot and reach out to a moderator to confirm your sponsor status");
  }
  return instructions;
}

SunnylinkSponsorPopup::SunnylinkSponsorPopup(bool sponsor_pair, QWidget *parent) : DialogBase(parent), sponsor_pair(sponsor_pair) {
  auto *hlayout = new QHBoxLayout(this);
  auto sunnylink_client = new SunnylinkClient(this);
  hlayout->setContentsMargins(0, 0, 0, 0);
  hlayout->setSpacing(0);

  setStyleSheet("SunnylinkSponsorPopup { background-color: #E0E0E0; }");

  // text
  auto vlayout = new QVBoxLayout();
  vlayout->setContentsMargins(85, 70, 50, 70);
  vlayout->setSpacing(50);
  hlayout->addLayout(vlayout, 1);
  {
    auto close = new QPushButton(QIcon(":/icons/close.svg"), "", this);
    close->setIconSize(QSize(80, 80));
    close->setStyleSheet("border: none;");
    vlayout->addWidget(close, 0, Qt::AlignLeft);
    connect(close, &QPushButton::clicked, this, [=] {
      sunnylink_client->role_service->load();
      sunnylink_client->user_service->load();
      QDialog::reject();
    });

    //vlayout->addSpacing(30);

    const QString titleText = sponsor_pair ? tr("Pair your GitHub account") : tr("Early Access: Become a sunnypilot Sponsor");
    const auto title = new QLabel(titleText, this);
    title->setStyleSheet("font-size: 75px; color: black;");
    title->setWordWrap(true);
    vlayout->addWidget(title);

    QStringList instructions = getInstructions(sponsor_pair);
    QString instructionsHtml = "<ol type='1' style='margin-left: 15px;'>";
    for (const auto & instruction : instructions) {
      instructionsHtml += QString("<li style='margin-bottom: 50px;'>%1</li>").arg(instruction);
    }
    instructionsHtml += "</ol>";
    const auto instructionsLabel = new QLabel(instructionsHtml, this);


    instructionsLabel->setStyleSheet("font-size: 47px; font-weight: bold; color: black;");
    instructionsLabel->setWordWrap(true);
    vlayout->addWidget(instructionsLabel);

    vlayout->addStretch();
  }

  // QR code
  auto *qr = new SunnylinkSponsorQRWidget(sponsor_pair ? true : false, this);
  hlayout->addWidget(qr, 1);
}
