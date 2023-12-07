#pragma once

#include "common/model.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/offroad/settings.h"
#include "selfdrive/ui/qt/offroad/sunnypilot/models_fetcher.h"

class SoftwarePanelSP final : public SoftwarePanel {
  Q_OBJECT

public:
  explicit SoftwarePanelSP(QWidget *parent = nullptr);

private:
  QString GetModelName();
  void checkNetwork();
  bool isDownloadingModel() const {
    return selectedModelToDownload.has_value() && modelDownloadProgress > 0.0 && modelDownloadProgress < 100.0;
  }

  // UI update related methods
  void updateLabels() override;
  void handleCurrentModelLblBtnClicked();
  void HandleModelDownloadProgressReport();
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
    const QString final_buttonText = !confirmButtonText.isEmpty() ? confirmButtonText : QString("Continue%1").arg(show_metered_warning ? " on Metered" : "");

    return ConfirmationDialog::confirm(final_message, final_buttonText, parent);
  }

  bool is_metered;
  bool is_wifi;
  double modelDownloadProgress = 0.0;
  std::optional<Model> selectedModelToDownload;
  ButtonControl *currentModelLblBtn;
  ModelsFetcher models_fetcher;
};
