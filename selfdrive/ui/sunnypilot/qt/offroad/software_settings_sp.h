#pragma once

#include "common/model.h"
#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/sp_priv_ui.h"
#else
#include "selfdrive/ui/ui.h"
#endif
#include "selfdrive/ui/qt/offroad/settings.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/models_fetcher.h"

class SoftwarePanelSP final : public SoftwarePanel {
  Q_OBJECT

public:
  explicit SoftwarePanelSP(QWidget *parent = nullptr);


private:
  QString GetModelName();
  QString GetNavModelName();
  QString GetMetadataName();

  void checkNetwork();
  bool isDownloadingModel() const {
    LOGD("isDownloadingModel: selectedModelToDownload.has_value() [%s] && modelDownloadProgress [%f]",selectedModelToDownload.has_value() ?"true": "false", modelDownloadProgress.value_or(0.0));
    return selectedModelToDownload.has_value() && modelDownloadProgress.value_or(0.0) > 0.0 && modelDownloadProgress.value_or(0.0) < 100.0;
  }

  bool isDownloadingNavModel() const {
    LOGD("isDownloadingNavModel: selectedNavModelToDownload.has_value() [%s] && navModelDownloadProgress [%f]",selectedNavModelToDownload.has_value() ?"true": "false", navModelDownloadProgress.value_or(0.0));
    return selectedNavModelToDownload.has_value() && navModelDownloadProgress.value_or(0.0) > 0.0 && navModelDownloadProgress.value_or(0.0) < 100.0;
  }

  bool isDownloadingMetadata() const {
    LOGD("isDownloadingMetadata: selectedMetadataToDownload.has_value() [%s] && metadataDownloadProgress [%f]",selectedMetadataToDownload.has_value() ?"true": "false", metadataDownloadProgress.value_or(0.0));
    return selectedMetadataToDownload.has_value() && metadataDownloadProgress.value_or(0.0) > 0.0 && metadataDownloadProgress.value_or(0.0) < 100.0;
  }

  // UI update related methods
  void updateLabels() override;
  void handleCurrentModelLblBtnClicked();
  void HandleModelDownloadProgressReport();
  void handleDownloadProgress(double progress, const QString&modelType);
  void HandleNavModelDownloadProgressReport();
  void handleDownloadFailed(const QString &modelType);
  void showResetParamsDialog();
  bool canContinueOnMeteredDialog() {
    if (!is_metered) return true;
    return showConfirmationDialog(QString(), QString(), is_metered);
  }

  inline bool showConfirmationDialog(const QString &message = QString(), const QString &confirmButtonText = QString(), const bool show_metered_warning = false) {
    return showConfirmationDialog(this, message, confirmButtonText, show_metered_warning);
  }

  static inline bool showConfirmationDialog(QWidget *parent, const QString &message = QString(), const QString &confirmButtonText = QString(), const bool show_metered_warning = false) {
    const QString warning_message = show_metered_warning ? tr("Warning: You are on a metered connection!") : QString();
    const QString final_message = QString("%1%2").arg(!message.isEmpty() ? message+"\n" : QString(), warning_message);
    const QString final_buttonText = !confirmButtonText.isEmpty() ? confirmButtonText : QString(tr("Continue") + " %1").arg(show_metered_warning ? tr("on Metered") : "");

    return ConfirmationDialog::confirm(final_message, final_buttonText, parent);
  }

  bool is_metered{};
  bool is_wifi{};
  bool modelFromCache;
  bool navModelFromCache;
  bool metadataFromCache;
  std::optional<double> modelDownloadProgress;
  std::optional<double> navModelDownloadProgress;
  std::optional<double> metadataDownloadProgress;
  std::optional<Model> selectedModelToDownload;
  std::optional<Model> selectedNavModelToDownload;
  std::optional<Model> selectedMetadataToDownload;
  ButtonControl *currentModelLblBtn;
  ModelsFetcher models_fetcher;
  ModelsFetcher nav_models_fetcher;
  ModelsFetcher metadata_fetcher;
  bool model_download_failed;
  QString failed_downloads_description = "";
};
