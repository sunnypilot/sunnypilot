/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnylink_panel.h"

#include "selfdrive/ui/sunnypilot/qt/util.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

SunnylinkPanel::SunnylinkPanel(QWidget *parent) : QFrame(parent) {
    main_layout = new QStackedLayout(this);
    sunnylink_client = new SunnylinkClient(this);
    param_watcher = new ParamWatcher(this);
    param_watcher->addParam("SunnylinkEnabled");
    connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
        paramsRefresh(param_name, param_value);
    });

    is_sunnylink_enabled = Params().getBool("SunnylinkEnabled");
    connect(uiStateSP(), &UIStateSP::sunnylinkRolesChanged, this, &SunnylinkPanel::updatePanel);
    connect(uiStateSP(), &UIStateSP::sunnylinkDeviceUsersChanged, this, &SunnylinkPanel::updatePanel);
    connect(uiStateSP(), &UIStateSP::offroadTransition, [=](bool offroad) {
        is_onroad = !offroad;
        updatePanel();
    });

    sunnylinkScreen = new QWidget(this);
    auto vlayout = new QVBoxLayout(sunnylinkScreen);
    vlayout->setContentsMargins(50, 20, 50, 20);

    auto *list = new ListWidget(this, false);
    QString sunnylinkEnabledBtnDesc = tr(
        "This is the master switch, it will allow you to cutoff any sunnylink requests should you want to do that.");
    sunnylinkEnabledBtn = new ParamControl(
        "SunnylinkEnabled",
        tr("Enable sunnylink"),
        sunnylinkEnabledBtnDesc,
        "");
    list->addItem(sunnylinkEnabledBtn);

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
            ConfirmationDialog::alert(
                tr(
                    "sunnylink Dongle ID not found. This may be due to weak internet connection or sunnylink registration issue. Please reboot and try again."),
                this);
        } else {
            pair_popup->exec();
        }
    });
    list->addItem(horizontal_line());

    connect(sunnylinkEnabledBtn, &ParamControl::showDescriptionEvent, [=]() {
        // resets the description to the default one for the Easter egg
        sunnylinkEnabledBtn->setDescription(sunnylinkEnabledBtnDesc);
    });

    connect(sunnylinkEnabledBtn, &ParamControl::toggleFlipped, [=](bool enabled) {
        QString description;
        if (enabled) {
            description = "<font color='SeaGreen'>" + tr("🎉Welcome back! We're excited to see you've enabled sunnylink again! 🚀") + "</font>";
        } else {
            description = "<font color='orange'>" + tr(
                              "👋Not going to lie, it's sad to see you disabled sunnylink 😢, but we'll be here when you're ready to come back 🎉.")
                          + "</font>";
        }
        sunnylinkEnabledBtn->showDescription();
        sunnylinkEnabledBtn->setDescription(description);

        updatePanel();
    });

    // Backup Settings
    backupSettings = new PushButtonSP(tr("Backup Settings"), 730, this);
    backupSettings->setObjectName("backup_btn");
    connect(backupSettings, &QPushButton::clicked, [=]() {
        is_backup = true;
        if (ConfirmationDialog::confirm(tr("Are you sure you want to backup sunnypilot settings?"), tr("Back Up"), this)) {
            params.putBool("BackupManager_CreateBackup", true);
            backupSettings->setEnabled(false);
        }
        is_backup = false;
    });
    // connect(backup_settings, &BackupSettings::updateLabels, this, &SunnylinkPanel::updateLabels);

    // Restore Settings
    restoreSettings = new PushButtonSP(tr("Restore Settings"), 730, this);
    restoreSettings->setObjectName("restore_btn");
    connect(restoreSettings, &QPushButton::clicked, [=]() {
        is_restore = true;
        if (ConfirmationDialog::confirm(tr("Are you sure you want to restore the last backed up sunnypilot settings?"), tr("Restore"), this)) {
            params.put("BackupManager_RestoreVersion", "latest");
            restoreSettings->setEnabled(false);
        }
        is_restore = false;
    });
    // connect(backup_settings, &BackupSettings::updateLabels, this, &SunnylinkPanel::updateLabels);
    // Settings Restore and Settings Backup in the same horizontal space
    auto settings_layout = new QHBoxLayout;
    settings_layout->setContentsMargins(0, 0, 0, 30);
    settings_layout->addWidget(backupSettings);
    settings_layout->addSpacing(10);
    settings_layout->addWidget(restoreSettings);
    settings_layout->setAlignment(Qt::AlignLeft);
    list->addItem(settings_layout);

    QObject::connect(uiState(), &UIState::offroadTransition, this, &SunnylinkPanel::updatePanel);
    QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &SunnylinkPanel::updatePanel);

    sunnylinkScroller = new ScrollViewSP(list, this);
    vlayout->addWidget(sunnylinkScroller);

    main_layout->addWidget(sunnylinkScreen);

    if (is_sunnylink_enabled) {
        startSunnylink();
    }
}

void SunnylinkPanel::updateBackupManagerState() {
    const SubMaster &sm = *(uiStateSP()->sm);
    backup_manager = sm["backupManagerSP"].getBackupManagerSP();
}

void SunnylinkPanel::handleBackupProgress() {
    auto backup_status = backup_manager.getBackupStatus();
    auto restore_status = backup_manager.getRestoreStatus();
    auto backup_progress = backup_manager.getBackupProgress();
    auto restore_progress = backup_manager.getRestoreProgress();

    switch (backup_status) {
        case cereal::BackupManagerSP::Status::IN_PROGRESS:
            backupSettings->setText(QString(tr("Backup in progress %1%").arg(backup_progress)));
            break;
        case cereal::BackupManagerSP::Status::FAILED:
            backupSettings->setText(tr("Backup Failed"));
            break;
        case cereal::BackupManagerSP::Status::COMPLETED:
        default:
            backupSettings->setText(tr("Backup Settings"));
            break;
    }
    backupSettings->setEnabled(!is_onroad && backup_status != cereal::BackupManagerSP::Status::IN_PROGRESS);

    switch (restore_status) {
        case cereal::BackupManagerSP::Status::IN_PROGRESS:
            restoreSettings->setText(QString(tr("Restore in progress %1%").arg(restore_progress)));
            break;
        case cereal::BackupManagerSP::Status::FAILED:
            restoreSettings->setText(tr("Restore Failed"));
            break;
        case cereal::BackupManagerSP::Status::COMPLETED:
        default:
            restoreSettings->setText(tr("Restore Settings"));
            break;
    }
    restoreSettings->setEnabled(!is_onroad && restore_status != cereal::BackupManagerSP::Status::IN_PROGRESS);
}

void SunnylinkPanel::paramsRefresh(const QString &param_name, const QString &param_value) {
    // We do it on paramsRefresh because the toggleEvent happens before the value is updated
    if (param_name == "SunnylinkEnabled" && param_value == "1") {
        startSunnylink();
    } else if (param_name == "SunnylinkEnabled" && param_value == "0") {
        stopSunnylink();
    }

    updatePanel();
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

void SunnylinkPanel::showEvent(QShowEvent *event) {
    updatePanel();
    if (is_sunnylink_enabled) {
        startSunnylink();
    }
}

void SunnylinkPanel::updatePanel() {
    if (!isVisible()) {
        return;
    }

    updateBackupManagerState();
    handleBackupProgress();
    const auto sunnylinkDongleId = getSunnylinkDongleId().value_or(tr("N/A"));
    sunnylinkEnabledBtn->setEnabled(!is_onroad);

    is_sunnylink_enabled = Params().getBool("SunnylinkEnabled");
    bool is_sub = uiStateSP()->isSunnylinkSponsor() && is_sunnylink_enabled;
    auto max_current_sponsor_rule = uiStateSP()->sunnylinkSponsorRole();
    auto role_name = max_current_sponsor_rule.getSponsorTierString();
    std::optional role_color = max_current_sponsor_rule.getSponsorTierColor();
    bool is_paired = uiStateSP()->isSunnylinkPaired();
    auto paired_users = uiStateSP()->sunnylinkDeviceUsers();

    sunnylinkEnabledBtn->setEnabled(!is_onroad);
    sunnylinkEnabledBtn->setValue(tr("Device ID") + " " + sunnylinkDongleId);

    sponsorBtn->setEnabled(!is_onroad && is_sunnylink_enabled);
    sponsorBtn->setText(is_sub ? tr("THANKS ♥") : tr("SPONSOR"));
    sponsorBtn->setValue(is_sub ? tr(role_name.toStdString().c_str()) : tr("Not Sponsor"), role_color);

    pairSponsorBtn->setEnabled(!is_onroad && is_sunnylink_enabled);
    pairSponsorBtn->setValue(is_paired ? tr("Paired") : tr("Not Paired"));


    if (!is_sunnylink_enabled) {
        sunnylinkEnabledBtn->setValue("");
        sponsorBtn->setValue("");
        pairSponsorBtn->setValue("");
    }

    update();
}
