/**
* Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/software_panel.h"

#include <algorithm>
#include <QJsonDocument>
#include "common/swaglog.h"

/**
 * @brief Constructs the software panel with model bundle selection functionality
 * @param parent Parent widget
 */
SoftwarePanelSP::SoftwarePanelSP(QWidget *parent) : SoftwarePanel(parent) {
  const auto current_model = GetModelName();
  currentModelLblBtn = new ButtonControlSP(tr("Current Model"), tr("SELECT"), current_model);
  currentModelLblBtn->setValue(current_model);

  connect(currentModelLblBtn, &ButtonControlSP::clicked, this, &SoftwarePanelSP::handleCurrentModelLblBtnClicked);
  QObject::connect(uiStateSP(), &UIStateSP::uiUpdate, this, &SoftwarePanelSP::updateLabels);
  AddWidgetAt(0, currentModelLblBtn);
}

/**
 * @brief Updates the UI with bundle download progress information
 * Reads status from modelManagerSP cereal message and displays status for all models
 */
void SoftwarePanelSP::handleBundleDownloadProgress() {
  const SubMaster &sm = *(uiStateSP()->sm);
  const auto model_manager = sm["modelManagerSP"].getModelManagerSP();
  QString description;

  if (!model_manager.hasSelectedBundle()) {
    currentModelLblBtn->setDescription(description);
    return;
  }

  const auto &bundle = model_manager.getSelectedBundle();
  const QString bundleName = QString::fromStdString(bundle.getDisplayName());
  const auto models = bundle.getModels();  // Get models from bundle
  
  // Helper lambda to get status line for a specific model type
  auto getModelStatusLine = [&](cereal::ModelManagerSP::Type type) -> QString {
    for (const auto &model : models) {
      auto model_name = QString::fromStdString(model.getFullName());
      if (model.getType() == type) {
        QString modelType;
        switch (type) {
          case cereal::ModelManagerSP::Type::DRIVE:
            modelType = tr("Driving");
            model_name = bundleName;
            break;
          case cereal::ModelManagerSP::Type::NAVIGATION:
            modelType = tr("Navigation");
            break;
          case cereal::ModelManagerSP::Type::METADATA:
            modelType = tr("Metadata");
            break;
        }

        const auto &progress = model.getDownloadProgress();
        auto status = progress.getStatus();
        
        if (status == cereal::ModelManagerSP::DownloadStatus::DOWNLOADING) {
          float percent = progress.getProgress();
          return tr("Downloading %1 model [%2]... (%3%)").arg(modelType, model_name).arg(percent, 0, 'f', 2);
        } else if (status == cereal::ModelManagerSP::DownloadStatus::DOWNLOADED) {
          return tr("%1 model [%2] downloaded").arg(modelType, model_name);
        } else if (status == cereal::ModelManagerSP::DownloadStatus::FAILED) {
          return tr("%1 model [%2] download failed").arg(modelType, model_name);
        } else {
          return tr("%1 model [%2] pending...").arg(modelType, model_name);
        }
      }
    }
    return QString();
  };

  // Always show status for all model types in consistent order
  QStringList modelTypes = {
    getModelStatusLine(cereal::ModelManagerSP::Type::DRIVE),
    getModelStatusLine(cereal::ModelManagerSP::Type::NAVIGATION),
    getModelStatusLine(cereal::ModelManagerSP::Type::METADATA)
  };

  // Build description with all non-empty status lines
  description = modelTypes.filter(QRegExp(".+")).join("\n");

  if (!description.isEmpty()) {
    currentModelLblBtn->setDescription(description);
  }

  if (model_manager.getSelectedBundle().getStatus() == cereal::ModelManagerSP::DownloadStatus::DOWNLOADING) {
    currentModelLblBtn->showDescription();
  }
  
  currentModelLblBtn->setEnabled(!is_onroad && !isDownloading());
}

/**
 * @brief Gets the name of the currently selected model bundle
 * @return Display name of the selected bundle or default model name
 */
QString SoftwarePanelSP::GetModelName() {
  const SubMaster &sm = *(uiStateSP()->sm);
  const auto model_manager = sm["modelManagerSP"].getModelManagerSP();

  if (model_manager.hasActiveBundle()) {
    return QString::fromStdString(model_manager.getActiveBundle().getDisplayName());
  }
  
  return "";
}

/**
 * @brief Handles the model bundle selection button click
 * Displays available bundles, allows selection, and initiates download
 */
void SoftwarePanelSP::handleCurrentModelLblBtnClicked() {
  currentModelLblBtn->setEnabled(false);
  currentModelLblBtn->setValue(tr("Fetching bundles..."));

  const SubMaster &sm = *(uiStateSP()->sm);
  const auto model_manager = sm["modelManagerSP"].getModelManagerSP();
  
  // Create mapping of bundle indices to display names
  QMap<uint32_t, QString> index_to_bundle;
  const auto bundles = model_manager.getAvailableBundles();
  for (const auto &bundle : bundles) {
    index_to_bundle.insert(bundle.getIndex(), QString::fromStdString(bundle.getDisplayName()));
  }

  // Sort bundles by index in descending order
  QStringList bundleNames;
  auto indices = index_to_bundle.keys();
  std::sort(indices.begin(), indices.end(), std::greater<uint32_t>());
  for (const auto &index : indices) {
    bundleNames.append(index_to_bundle[index]);
  }

  currentModelLblBtn->setEnabled(!is_onroad);
  currentModelLblBtn->setValue(GetModelName());

  // Get current selection for default option
  QString currentBundleName;
  if (model_manager.hasSelectedBundle()) {
    currentBundleName = QString::fromStdString(model_manager.getSelectedBundle().getDisplayName());
  }

  const QString selectedBundleName = MultiOptionDialog::getSelection(
    tr("Select a Model Bundle"), bundleNames, currentBundleName, this);

  if (selectedBundleName.isEmpty() || !canContinueOnMeteredDialog()) {
    return;
  }

  // Find selected bundle and initiate download
  for (const auto &bundle : bundles) {
    if (QString::fromStdString(bundle.getDisplayName()) == selectedBundleName) {
      params.put("ModelManager_DownloadIndex", std::to_string(bundle.getIndex()));
      if (bundle.getGeneration() != model_manager.getActiveBundle().getGeneration()) {
        showResetParamsDialog();
      }
      break;
    }
  }
  
  updateLabels();
}

/**
 * @brief Updates the UI elements based on current state
 */
void SoftwarePanelSP::updateLabels() {
  if (!isVisible()) {
    return;
  }

  handleBundleDownloadProgress();
  currentModelLblBtn->setValue(GetModelName());
  SoftwarePanel::updateLabels();
}

/**
 * @brief Shows dialog prompting user to reset calibration after model download
 */
void SoftwarePanelSP::showResetParamsDialog() {
  const auto confirmMsg = tr("Bundle download has started in the background.") + "\n" +
                         tr("We STRONGLY suggest you to reset calibration. Would you like to do that now?");
  const auto button_text = tr("Reset Calibration");

  if (showConfirmationDialog(confirmMsg, button_text, false)) {
    params.remove("CalibrationParams");
    params.remove("LiveTorqueParameters");
  }
}