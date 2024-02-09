#include "selfdrive/ui/qt/offroad/sunnypilot/software_settings_sp.h"

SoftwarePanelSP::SoftwarePanelSP(QWidget* parent) : SoftwarePanel(parent) {
  // Get current model name and create new ButtonControl
  const auto current_model = GetModelName();
  currentModelLblBtn = new ButtonControl(tr("Driving Model"), tr("SELECT"), current_model);
  currentModelLblBtn->setValue(current_model);

  // Connect downloadProgress from models_fetcher to local slot
  connect(&models_fetcher, &ModelsFetcher::downloadProgress, this, [=](const double progress) {
    modelDownloadProgress = progress;
    HandleModelDownloadProgressReport();
  });

  // Connect click event from currentModelLblBtn to local slot
  connect(currentModelLblBtn, &ButtonControl::clicked, this, &SoftwarePanelSP::handleCurrentModelLblBtnClicked);

  ReplaceOrAddWidget(currentModelLbl, currentModelLblBtn);
}

QString SoftwarePanelSP::GetModelName() {
  if (selectedModelToDownload.has_value()) {
    return selectedModelToDownload->displayName;
  }

  if (params.getBool("CustomDrivingModel")) {
    return QString::fromStdString(params.get("DrivingModelName"));
  }

  return CURRENT_MODEL;
}

void SoftwarePanelSP::HandleModelDownloadProgressReport() {
  const auto _progress_str = QString::number(modelDownloadProgress, 'f', 2);
  const auto description = isDownloadingModel() ? QString("Downloading [%1]... (%2%)") : QString("%1 downloaded");

  // Update UI with new description
  currentModelLblBtn->setDescription(description.arg(GetModelName(), _progress_str));
  currentModelLblBtn->showDescription();
  currentModelLblBtn->setEnabled(!(is_onroad || isDownloadingModel()));

  // If not downloading and there is a selected model, update parameters
  if (!isDownloadingModel() && selectedModelToDownload.has_value()) {
    params.put("DrivingModelText", selectedModelToDownload->fullName.toStdString());
    params.put("DrivingModelName", selectedModelToDownload->displayName.toStdString());
    //params.put("DrivingModelUrl", selectedModelToDownload->downloadUri.toStdString());  // TODO: Placeholder for future implementations
    params.put("DrivingModelGeneration", selectedModelToDownload->generation.toStdString());
    params.put("NavModelText", selectedModelToDownload->fullNameNav.toStdString());
    selectedModelToDownload.reset();
    params.putBool("CustomDrivingModel", true);
  }
}

void SoftwarePanelSP::handleCurrentModelLblBtnClicked() {
  // Disabling label button and displaying fetching message
  currentModelLblBtn->setEnabled(false);
  currentModelLblBtn->setValue("Fetching models...");

  checkNetwork();
  const auto currentModelName = QString::fromStdString(params.get("DrivingModelName"));
  const bool is_release_sp = params.getBool("IsReleaseSPBranch");
  const auto models = models_fetcher.getModelsFromURL();

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

  const QString selectedModelName = MultiOptionDialog::getSelection(tr("Select a Driving Model"), modelNames, currentModelName, this);

  // Bail if no selected model or the user doesn't want to continue while on metered
  if (selectedModelName.isEmpty() || !canContinueOnMeteredDialog()) {
    return;
  }

  // Finding and setting the selected model
  for (auto &model: models) {
    if (model.displayName == selectedModelName) {
      selectedModelToDownload = model;
      params.putBool("CustomDrivingModel", false);
      break;
    }
  }

  // If decision is to download and there is a selected model, update UI and begin downloading
  if (selectedModelToDownload.has_value()) {
    currentModelLblBtn->setValue(selectedModelToDownload->displayName);
    currentModelLblBtn->setDescription(selectedModelToDownload->displayName);
    models_fetcher.download(selectedModelToDownload->downloadUri, selectedModelToDownload->fileName);
    models_fetcher.download(selectedModelToDownload->downloadUriNav, selectedModelToDownload->fileNameNav);

    // Disable select button until download completes
    currentModelLblBtn->setEnabled(false);
    showResetParamsDialog();
  }
}

void SoftwarePanelSP::checkNetwork() {
  const SubMaster &sm = *(uiState()->sm);
  const auto device_state = sm["deviceState"].getDeviceState();
  const auto network_type = device_state.getNetworkType();
  is_wifi = network_type == cereal::DeviceState::NetworkType::WIFI;
  is_metered = device_state.getNetworkMetered();
}

void SoftwarePanelSP::updateLabels() {
  if (!isVisible()) {
    return;
  }

  checkNetwork();
  currentModelLblBtn->setEnabled(!is_onroad);
  SoftwarePanel::updateLabels();
}

void SoftwarePanelSP::showResetParamsDialog() {
  const auto confirmMsg = tr("Download has started in the background.\nWe STRONGLY suggest you to reset calibration, would you like to do that now?");
  const auto button_text = tr("Reset Calibration");

  // If user confirms, remove specified parameters
  if (showConfirmationDialog(confirmMsg, button_text, false)) {
    params.remove("CalibrationParams");
    params.remove("LiveTorqueParameters");
  }
}
