/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <QProgressBar>

#include "selfdrive/ui/sunnypilot/qt/util.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"

class ModelsPanel : public QWidget {
  Q_OBJECT

public:
  explicit ModelsPanel(QWidget *parent = nullptr);

private:
  QString GetActiveModelName();
  QString GetActiveModelInternalName();
  QString GetActiveModelRef();
  void updateModelManagerState();
  void showEvent(QShowEvent *event) override;

  bool isDownloading() const {
    if (!model_manager.hasSelectedBundle()) {
        return false;
    }

    const auto &selected_bundle = model_manager.getSelectedBundle();
    return selected_bundle.getStatus() == cereal::ModelManagerSP::DownloadStatus::DOWNLOADING;
  }

  // UI update related methods
  void updateLabels();
  void handleCurrentModelLblBtnClicked();
  void handleBundleDownloadProgress();
  void refreshLaneTurnValueControl();
  void showResetParamsDialog();
  QProgressBar* createProgressBar(QWidget *parent);
  QFrame* createModelDetailFrame(QWidget *parent, QString &typeName, QProgressBar *progressBar);
  cereal::ModelManagerSP::Reader model_manager;
  cereal::ModelManagerSP::DownloadStatus download_status{};
  cereal::ModelManagerSP::DownloadStatus prev_download_status{};
  void clearModelCache();
  double calculateCacheSize();

  bool canContinueOnMeteredDialog() {
    if (!is_metered) return true;
    return showConfirmationDialog(QString(), QString(), is_metered);
  }

  inline bool showConfirmationDialog(const QString &message = QString(), const QString &confirmButtonText = QString(), const bool show_metered_warning = false) {
    return showConfirmationDialog(this, message, confirmButtonText, show_metered_warning);
  }

  static inline bool showConfirmationDialog(QWidget *parent, const QString &message = QString(), const QString &confirmButtonText = QString(), const bool show_metered_warning = false) {
    const QString warning_message = show_metered_warning ? tr("Warning: You are on a metered connection!") : QString();
    const QString final_message = QString("%1%2").arg(!message.isEmpty() ? message + "\n" : QString(), warning_message);
    const QString final_buttonText = !confirmButtonText.isEmpty() ? confirmButtonText : QString(tr("Continue") + " %1").arg(show_metered_warning ? tr("on Metered") : "");

    return ConfirmationDialog(final_message, final_buttonText, tr("Cancel"), true, parent).exec();
  }

  bool is_metered{};
  bool is_wifi{};
  bool is_onroad = false;

  ButtonControlSP *currentModelLblBtn;
  ParamControlSP *lagd_toggle_control;
  OptionControlSP *delay_control;
  QProgressBar *supercomboProgressBar;
  QFrame *supercomboFrame;
  QProgressBar *navigationProgressBar;
  QFrame *navigationFrame;
  QProgressBar *visionProgressBar;
  QFrame *visionFrame;
  QProgressBar *policyProgressBar;
  QFrame *policyFrame;
  Params params;
  ButtonControlSP *clearModelCacheBtn;
  ButtonControlSP *refreshAvailableModelsBtn;
  ParamControlSP *lane_turn_desire_toggle;
  OptionControlSP *lane_turn_value_control;
};
