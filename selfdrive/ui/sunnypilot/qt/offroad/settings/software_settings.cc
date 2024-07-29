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

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/software_settings.h"

#include <algorithm>

#include "common/model.h"

SoftwarePanelSP::SoftwarePanelSP(QWidget *parent) : SoftwarePanel(parent) {
  // Get current model name and create new ButtonControlSP
  const auto current_model = GetModelName();
  currentModelLblBtn = new ButtonControlSP(tr("Driving Model"), tr("SELECT"), current_model);
  currentModelLblBtn->setValue(current_model);

  connect(&models_fetcher, &ModelsFetcher::downloadProgress, this, [this](const double progress) {
    handleDownloadProgress(progress, "driving");
  });

  connect(&nav_models_fetcher, &ModelsFetcher::downloadProgress, this, [this](const double progress) {
    handleDownloadProgress(progress, "navigation");
  });

  connect(&metadata_fetcher, &ModelsFetcher::downloadProgress, this, [this](const double progress) {
    handleDownloadProgress(progress, "metadata");
  });

  connect(&models_fetcher, &ModelsFetcher::downloadComplete, this, [this](const QByteArray& data, bool fromCache) {
    modelFromCache = fromCache;
    if (!isDownloadingModel() && modelDownloadProgress.has_value()) {
      params.put("DrivingModelText", selectedModelToDownload->fullName.toStdString());
      params.put("DrivingModelName", selectedModelToDownload->displayName.toStdString());
      params.put("DrivingModelGeneration", selectedModelToDownload->generation.toStdString());
      selectedModelToDownload.reset();
      modelDownloadProgress.reset();
      params.putBool("CustomDrivingModel", !model_download_failed);
    }
    nav_models_fetcher.download(selectedNavModelToDownload->downloadUriNav, selectedNavModelToDownload->fileNameNav);
    HandleModelDownloadProgressReport();
  });

  connect(&nav_models_fetcher, &ModelsFetcher::downloadComplete, this, [this](const QByteArray&data, bool fromCache = false) {
    navModelFromCache = fromCache;
    if (!isDownloadingNavModel() && navModelDownloadProgress.has_value()) {
      params.put("NavModelText", selectedNavModelToDownload->fullNameNav.toStdString());
      selectedNavModelToDownload.reset();
      navModelDownloadProgress.reset();
    }
    metadata_fetcher.download(selectedMetadataToDownload->downloadUriMetadata, selectedMetadataToDownload->fileNameMetadata);
    HandleModelDownloadProgressReport();
    // updateLabels();
  });

  connect(&metadata_fetcher, &ModelsFetcher::downloadComplete, this, [this](const QByteArray&data, bool fromCache = false) {
    metadataFromCache = fromCache;
    if (!isDownloadingMetadata() && metadataDownloadProgress.has_value()) {
      params.put("DrivingModelMetadataText", selectedMetadataToDownload->fullNameMetadata.toStdString());
      selectedMetadataToDownload.reset();
      metadataDownloadProgress.reset();
    }
    HandleModelDownloadProgressReport();
    // updateLabels();
  });

  connect(&models_fetcher, &ModelsFetcher::downloadFailed, this, &SoftwarePanelSP::handleDownloadFailed);
  connect(&nav_models_fetcher, &ModelsFetcher::downloadFailed, this, &SoftwarePanelSP::handleDownloadFailed);
  connect(&metadata_fetcher, &ModelsFetcher::downloadFailed, this, &SoftwarePanelSP::handleDownloadFailed);


  // Connect click event from currentModelLblBtn to local slot
  connect(currentModelLblBtn, &ButtonControlSP::clicked, this, &SoftwarePanelSP::handleCurrentModelLblBtnClicked);

  AddWidgetAt(0, currentModelLblBtn);
}

void SoftwarePanelSP::handleDownloadFailed(const QString &modelType) {
  model_download_failed = true;
  LOGE("Download failed reported for [%s]", modelType.toStdString().c_str());
  failed_downloads_description += "["+ modelType +"]\n";
  HandleModelDownloadProgressReport(); // Call to update UI based on the new status
}

void SoftwarePanelSP::handleDownloadProgress(const double progress, const QString &modelType) {
  if (modelType == "driving") {
    modelDownloadProgress = progress;
  } else if (modelType == "navigation") {
    navModelDownloadProgress = progress;
  } else if (modelType == "metadata") {
    metadataDownloadProgress = progress;
  }

  HandleModelDownloadProgressReport();
}

QString SoftwarePanelSP::GetModelName() {
  if (selectedModelToDownload.has_value()) {
    return selectedModelToDownload->displayName;
  }

  if (params.getBool("CustomDrivingModel") && QString::fromStdString(params.get("DrivingModelGeneration")) != "0") {
    return QString::fromStdString(params.get("DrivingModelName"));
  }

  return CURRENT_MODEL;
}

QString SoftwarePanelSP::GetNavModelName() {
  if (selectedNavModelToDownload.has_value()) {
    return selectedNavModelToDownload->fullNameNav;
  }

  return QString::fromStdString(params.get("NavModelText"));
}

QString SoftwarePanelSP::GetMetadataName() {
  if (selectedMetadataToDownload.has_value()) {
    // Assuming your metadata structure has a 'name' or similar field
    return selectedMetadataToDownload->fullNameMetadata;
  }

  // Return a default name or an empty string if there's no metadata selected
  return QString::fromStdString(params.get("DrivingModelMetadataText"));
}

void SoftwarePanelSP::HandleModelDownloadProgressReport() {
  // Template strings for download status
  const QString downloadingTemplate = "Downloading %1 model [%2]... (%3%)";
  const QString downloadedTemplate = "%1 model [%2] downloaded";

  // Get model names
  QString drivingModelName = GetModelName();
  QString navModelName = GetNavModelName();
  QString metadataName = GetMetadataName();
  QString description;

  // Driving model status
  if (isDownloadingModel()) {
    auto modelProgress = modelDownloadProgress.value_or(0.0);
    auto progressText = modelProgress <= 0.01 ? tr("PENDING")+"..." : QString::number(modelProgress, 'f', 2) + "%";
    description += QString(tr("Downloading Driving model") + " [%1]... (%2)").arg(drivingModelName, progressText);
  } else {
    if (modelFromCache) drivingModelName += QString(" " + tr("(CACHED)"));
    description += QString(tr("Driving model") + " [%1] " + tr("downloaded")).arg(drivingModelName);
  }

  // Navigation model status
  if (isDownloadingNavModel() && !navModelName.isEmpty()) {
    auto navModelProgress = navModelDownloadProgress.value_or(0.0);
    auto progressText = navModelProgress <= 0.01 ? tr("PENDING")+"..." : QString::number(navModelProgress, 'f', 2) + "%";
    if (!description.isEmpty()) description += "\n"; // Add newline if driving model status is already appended
    description += QString(tr("Downloading Navigation model") + " [%1]... (%2)").arg(navModelName, progressText);
  } else if (!navModelName.isEmpty()) {
    if (navModelFromCache) navModelName += QString(" " + tr("(CACHED)"));
    if (!description.isEmpty()) description += "\n"; // Ensure newline separation
    description += QString(tr("Navigation model") + " [%1] " + tr("downloaded")).arg(navModelName);
  }

  // Metadata status
  if (isDownloadingMetadata() && !metadataName.isEmpty()) {
    auto metadataProgress = metadataDownloadProgress.value_or(0.0);
    auto progressText = metadataProgress <= 0.01 ? tr("PENDING")+"..." : QString::number(metadataProgress, 'f', 2) + "%";
    if (!description.isEmpty()) description += "\n";
    description += QString(tr("Downloading Metadata model") + " [%1]... (%2)").arg(metadataName, progressText);
  } else if (!metadataName.isEmpty()) {
    if (metadataFromCache) metadataName += QString(" " + tr("(CACHED)"));
    if (!description.isEmpty()) description += "\n";
    description += QString(tr("Metadata model") + " [%1] " + tr("downloaded")).arg(metadataName);
  }

  if (model_download_failed) {
    description = tr("Downloads have failed, please try swapping the model!") + "\n" +
                  tr("Failed:") + "\n" + failed_downloads_description;
    LOGE("MODEL DOWNLOADS FAILED!!!");
  }

  currentModelLblBtn->setDescription(description);
  currentModelLblBtn->showDescription();
  currentModelLblBtn->setEnabled(
      !(is_onroad || (isDownloadingModel() || isDownloadingMetadata() || isDownloadingNavModel())));
}

void SoftwarePanelSP::handleCurrentModelLblBtnClicked() {
  // Disabling label button and displaying fetching message
  currentModelLblBtn->setEnabled(false);
  currentModelLblBtn->setValue(tr("Fetching models..."));

  checkNetwork();
  const auto currentModelName = QString::fromStdString(params.get("DrivingModelName"));
  const bool is_release_sp = params.getBool("IsReleaseSPBranch");
  const auto models = ModelsFetcher::getModelsFromURL();

  QMap<QString, QString> index_to_model;

  // Collecting indices with display names
  for (const auto &model : models) {
    if ((is_release_sp && model.environment == "release") || !is_release_sp) {
      index_to_model.insert(model.index, model.displayName);
    }
  }

  QStringList modelNames;
  QStringList indices = index_to_model.keys();
  std::sort(indices.begin(), indices.end(), [&](const QString &index1, const QString &index2) {
    return index1.toInt() > index2.toInt();
  });

  for (const QString &index : indices) {
    modelNames.push_back(index_to_model[index]);
  }

  currentModelLblBtn->setEnabled(!is_onroad);
  currentModelLblBtn->setValue(GetModelName());

  const QString selectedModelName = MultiOptionDialog::getSelection(tr("Select a Driving Model"), modelNames,
                                                                    currentModelName, this);

  // Bail if no selected model or the user doesn't want to continue while on metered
  if (selectedModelName.isEmpty() || !canContinueOnMeteredDialog()) {
    return;
  }

  // Finding and setting the selected model
  for (auto &model : models) {
    if (model.displayName == selectedModelName) {
      selectedModelToDownload = model;
      selectedNavModelToDownload = model;
      selectedMetadataToDownload = model;
      params.putBool("CustomDrivingModel", false);
      break;
    }
  }

  // If decision is to download and there is a selected model, update UI and begin downloading
  if (selectedModelToDownload.has_value()) {
    model_download_failed = false;
    currentModelLblBtn->setValue(selectedModelToDownload->displayName);
    currentModelLblBtn->setDescription(selectedModelToDownload->displayName);

    // So we reset the cache status
    modelFromCache = false;
    navModelFromCache = false;
    metadataFromCache = false;

    // So we can signal them as pending
    navModelDownloadProgress = 0.01;
    modelDownloadProgress = 0.01;
    metadataDownloadProgress = 0.01;

    // Sunny wants it responsive... Responsive it is...
    HandleModelDownloadProgressReport();

    // Start the download, we download the other models on emit of downloadComplete
    if (params.get("DrivingModelGeneration") != selectedModelToDownload->generation.toStdString())
      showResetParamsDialog();
    models_fetcher.download(selectedModelToDownload->downloadUri, selectedModelToDownload->fileName);

    // Disable select button until download completes
    currentModelLblBtn->setEnabled(false);
  }
  updateLabels();
}

void SoftwarePanelSP::checkNetwork() {
  const SubMaster &sm = *(uiStateSP()->sm);
  const auto device_state = sm["deviceState"].getDeviceState();
  const auto network_type = device_state.getNetworkType();
  is_wifi = network_type == cereal::DeviceState::NetworkType::WIFI;
  is_metered = device_state.getNetworkMetered();
}

void SoftwarePanelSP::updateLabels() {
  if (!isVisible()) {
    return;
  }

  if (!model_download_failed)
    failed_downloads_description = "";

  checkNetwork();
  currentModelLblBtn->setEnabled(!(is_onroad || (isDownloadingModel() || isDownloadingMetadata() || isDownloadingNavModel())));
  SoftwarePanel::updateLabels();
}

void SoftwarePanelSP::showResetParamsDialog() {
  const auto confirmMsg = tr("Download has started in the background.") + "\n" +
                          tr("We STRONGLY suggest you to reset calibration. Would you like to do that now?");
  const auto button_text = tr("Reset Calibration");

  // If user confirms, remove specified parameters
  if (showConfirmationDialog(confirmMsg, button_text, false)) {
    params.remove("CalibrationParams");
    params.remove("LiveTorqueParameters");
  }
}
