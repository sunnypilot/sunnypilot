#include "selfdrive/ui/qt/offroad/sunnypilot/sunnylink_settings.h"

SunnylinkPanel::SunnylinkPanel(QWidget* parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);

  ListWidget *list = new ListWidget(this, false);
  list->addItem(new LabelControl(tr("sunnylink Dongle ID"), getSunnylinkDongleId().value_or(tr("N/A"))));
  list->addItem(horizontal_line());

  popup = new SunnylinkSponsorPopup(this);
  sponsorBtn = new ButtonControl(
    tr("Sponsor Status"), tr("SPONSOR"),
    tr("Become a sponsor of sunnypilot to get early access to sunnylink features.")
  );
  list->addItem(sponsorBtn);
  connect(sponsorBtn, &ButtonControl::clicked, [=]() {
    popup->exec();
  });
  list->addItem(horizontal_line());

  list->addItem(new LabelControl(tr("Manage Settings")));

  backup_settings = new BackupSettings;

  // Backup Settings
  backupSettings = new SubPanelButton(tr("Backup Settings"), 720, this);
  backupSettings->setObjectName("backup_btn");
  // Set margin on the outside of the button
  QVBoxLayout* backupSettingsLayout = new QVBoxLayout;
  backupSettingsLayout->setContentsMargins(0, 0, 0, 30);
  backupSettingsLayout->addWidget(backupSettings);
  connect(backupSettings, &QPushButton::clicked, [=]() {
    is_backup = true;
    backup_settings->started();
    if (uiState()->isSubscriber()) {
      if (ConfirmationDialog::confirm(tr("Are you sure you want to backup sunnypilot settings?"), tr("Backup"), this)) {
        backup_settings->sendParams(backup_settings->backupParams());
      } else {
        backup_settings->finished();
      }
    } else {
      if (ConfirmationDialog::confirm(tr("Early alpha access only. Become a sponsor to get early access to sunnylink features."), tr("Become a Sponsor"), this)) {
        popup->exec();
      }
      backup_settings->finished();
    }
    is_backup = false;
  });
  connect(backup_settings, &BackupSettings::updateLabels, this, &SunnylinkPanel::updateLabels);

  // Restore Settings
  restoreSettings = new SubPanelButton(tr("Restore Settings"), 720, this);
  restoreSettings->setObjectName("restore_btn");
  // Set margin on the outside of the button
  QVBoxLayout* restoreSettingsLayout = new QVBoxLayout;
  restoreSettingsLayout->setContentsMargins(0, 0, 0, 30);
  restoreSettingsLayout->addWidget(restoreSettings);
  connect(restoreSettings, &QPushButton::clicked, [=]() {
    is_restore = true;
    backup_settings->started();
    if (uiState()->isSubscriber()) {
      if (ConfirmationDialog::confirm(tr("Are you sure you want to restore the last backed up sunnypilot settings?"), tr("Restore"), this)) {
        backup_settings->getParams();
      } else {
        backup_settings->finished();
      }
    } else {
      if (ConfirmationDialog::confirm(tr("Early alpha access only. Become a sponsor to get early access to sunnylink features."), tr("Become a Sponsor"), this)) {
        popup->exec();
      }
      backup_settings->finished();
    }
    is_restore = false;
  });
  connect(backup_settings, &BackupSettings::updateLabels, this, &SunnylinkPanel::updateLabels);

  // Settings Restore and Settings Backup in the same horizontal space
  QHBoxLayout *settings_layout = new QHBoxLayout;
  settings_layout->setContentsMargins(0, 0, 0, 30);
  settings_layout->addWidget(backupSettings);
  settings_layout->addSpacing(10);
  settings_layout->addWidget(restoreSettings);
  settings_layout->setAlignment(Qt::AlignLeft);
  list->addItem(settings_layout);

  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    is_onroad = !offroad;
    updateLabels();
  });

  sunnylinkScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(sunnylinkScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  vlayout->addWidget(new ScrollView(list, this), 1);
  main_layout->addWidget(sunnylinkScreen);

  getSubscriber();

  updateLabels();
}

void SunnylinkPanel::showEvent(QShowEvent* event) {
  getSubscriber(true);
  updateLabels();  // For snappier feeling
}

void SunnylinkPanel::hideEvent(QHideEvent* event) {
  sub_repeater->deleteLater();
}

void SunnylinkPanel::updateLabels() {
  if (!isVisible()) {
    return;
  }

  bool is_sub = uiState()->isSubscriber();

  sponsorBtn->setEnabled(!is_onroad);
  sponsorBtn->setText(is_sub ? tr("THANKS") + " ❤️" : tr("SPONSOR"));
  sponsorBtn->setValue(is_sub ? tr("Sponsor") : tr("Not Sponsor"));

  backupSettings->setEnabled(!backup_settings->in_progress && !is_onroad);
  restoreSettings->setEnabled(!backup_settings->in_progress && !is_onroad);

  backupSettings->setText(backup_settings->in_progress && is_backup ? tr("Backing up...") : tr("Backup Settings"));
  restoreSettings->setText(backup_settings->in_progress && is_restore ? tr("Restoring...") : tr("Restore Settings"));

  update();
}

void SunnylinkPanel::getSubscriber(bool poll) {
  if (auto sl_dongle_id = getSunnylinkDongleId()) {
    QString url = "https://stg.api.sunnypilot.ai/device/" + *sl_dongle_id + "/roles";

    init_sub_request = new HttpRequest(this, true, 10000, true);
    QObject::connect(init_sub_request, &HttpRequest::requestDone, [=](const QString &resp, bool success) {
      replyFinished(resp, success);
      updateLabels();
      init_sub_request->deleteLater();
    });
    init_sub_request->sendRequest(url);

    if (poll) {
      sub_repeater = new RequestRepeater(this, url, "", 60, false, true);
      QObject::connect(sub_repeater, &RequestRepeater::requestDone, [=](const QString &resp, bool success) {
        replyFinished(resp, success);
        updateLabels();
      });
    }
  }
}

void SunnylinkPanel::replyFinished(const QString &response, bool success) {
  if (!success) return;

  SunnylinkRoleType role_type;

  if (response == "[]") {
    role_type = static_cast<SunnylinkRoleType>(int(SunnylinkRoleType::SL_UNKNOWN));
    uiState()->setSunnylinkRoleType(role_type);
    qDebug() << "JSON Parse failed on getting sponsor status";
    return;
  }

  // TODO: Refactor to check additional role types with new mapping on the server side when implemented
  QJsonDocument doc = QJsonDocument::fromJson(response.toUtf8());
  QJsonArray jsonArray = doc.array();

  for (const QJsonValue &value : jsonArray) {
    QJsonObject json = value.toObject();
    role_type = static_cast<SunnylinkRoleType>(int(sunnylinkRoleTypeValue(QString(json["role_type"].toString()))));

    uiState()->setSunnylinkRoleType(role_type);
  }
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

  QByteArray processed_data = encrypt ? CommaApi::rsa_encrypt(compressedData) : compressedData;

  // Encode the compressed QByteArray in Base64.
  QString converted_params_processed_base64_data = QString(processed_data.toBase64());

  payload["is_encrypted"] = encrypt;
  payload["config"] = converted_params_processed_base64_data;
  // Create a sub-object for sunnypilot_version
  QJsonObject version;
  QStringList versioning = getVersion().split('.');
  version["major"] = versioning.value(0, 0).toInt();
  version["minor"] = versioning.value(1, 0).toInt();
  version["patch"] = versioning.value(2, 0).toInt();
  version["build"] = versioning.value(3, 0).toInt();
  version["branch"] = QString::fromStdString(params.get("GitBranch"));
  payload["sunnypilot_version"] = version;

  // Convert the QJsonObject payload to QByteArray
  QByteArray payloadData = QJsonDocument(payload).toJson();

  return payloadData;
}

void BackupSettings::sendParams(const QByteArray &payload) {
  if (auto sl_dongle_id = getSunnylinkDongleId()) {
    QString url = "https://stg.api.sunnypilot.ai/backup/" + *sl_dongle_id;
    HttpRequest *request = new HttpRequest(this, true, 10000, true);
    QObject::connect(request, &HttpRequest::requestDone, [=](const QString &resp, bool success) {
      if (success && resp != "[]") {
        ConfirmationDialog::alert(tr("Settings backed up for sunnylink Device ID: ") + *sl_dongle_id, this);
      } else if (resp == "[]") {
        ConfirmationDialog::alert(tr("Settings updated successfully, but no additional data was returned by the server."), this);
      } else {
        ConfirmationDialog::alert(tr("OOPS! We made a booboo.") + "\n" + tr("Please try again later."), this);
      }

      QObject::connect(request, &QObject::destroyed, this, &BackupSettings::finished);

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
      const QByteArray configJsonDataCompressed = isEncrypted ? CommaApi::rsa_decrypt(configJsonDataDecoded) : configJsonDataDecoded;
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
    QString url = "https://stg.api.sunnypilot.ai/backup/" + *sl_dongle_id;
    HttpRequest *request = new HttpRequest(this, true, 10000, true);
    QObject::connect(request, &HttpRequest::requestDone, [=](const QString &resp, bool success) {
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

      QObject::connect(request, &QObject::destroyed, [=]() {
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

SunnylinkSponsorQRWidget::SunnylinkSponsorQRWidget(QWidget* parent) : QWidget(parent) {
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
  QString qrString = "https://github.com/sponsors/sunnyhaibin";
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

SunnylinkSponsorPopup::SunnylinkSponsorPopup(QWidget *parent) : DialogBase(parent) {
  QHBoxLayout *hlayout = new QHBoxLayout(this);
  hlayout->setContentsMargins(0, 0, 0, 0);
  hlayout->setSpacing(0);

  setStyleSheet("SunnylinkSponsorPopup { background-color: #E0E0E0; }");

  // text
  QVBoxLayout *vlayout = new QVBoxLayout();
  vlayout->setContentsMargins(85, 70, 50, 70);
  vlayout->setSpacing(50);
  hlayout->addLayout(vlayout, 1);
  {
    QPushButton *close = new QPushButton(QIcon(":/icons/close.svg"), "", this);
    close->setIconSize(QSize(80, 80));
    close->setStyleSheet("border: none;");
    vlayout->addWidget(close, 0, Qt::AlignLeft);
    QObject::connect(close, &QPushButton::clicked, this, &QDialog::reject);

    //vlayout->addSpacing(30);

    QLabel *title = new QLabel(tr("Early Access: Become a sunnypilot Sponsor"), this);
    title->setStyleSheet("font-size: 75px; color: black;");
    title->setWordWrap(true);
    vlayout->addWidget(title);

    QLabel *instructions = new QLabel(QString(R"(
      <ol type='1' style='margin-left: 15px;'>
        <li style='margin-bottom: 50px;'>%1</li>
        <li style='margin-bottom: 50px;'>%2</li>
        <li style='margin-bottom: 50px;'>%3</li>
      </ol>
    )").arg(tr("Scan the QR code to visit sunnyhaibin's GitHub Sponsors page"))
    .arg(tr("Choose your sponsorship tier and confirm your support"))
    .arg(tr("Join our community on Discord at https://discord.gg/sunnypilot and reach out to a moderator to confirm your sponsor status")), this);

    instructions->setStyleSheet("font-size: 47px; font-weight: bold; color: black;");
    instructions->setWordWrap(true);
    vlayout->addWidget(instructions);

    vlayout->addStretch();
  }

  // QR code
  SunnylinkSponsorQRWidget *qr = new SunnylinkSponsorQRWidget(this);
  hlayout->addWidget(qr, 1);
}
