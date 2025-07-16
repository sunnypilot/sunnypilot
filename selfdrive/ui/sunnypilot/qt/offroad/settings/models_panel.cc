/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include <algorithm>
#include <QJsonDocument>
#include <QStyle>

#include "common/model.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/models_panel.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/scrollview.h"

static const QString progressStyleActive = "QProgressBar {"
    "  font-size: 40px;"
    "  font-weight: 200;"
    "  padding: 1px;"
    "  border: 3px solid black;"
    "  border-radius: 10px;"
    "}"
    "QProgressBar::chunk {"
    "  background-color: #1e79e8;"
    "  border-radius: 10px;"
    "}";

static const QString progressStyleInactive = progressStyleActive +
    "QProgressBar::chunk {"
    "  background-color: transparent;"
    "}";

static const QString progressStyleDone = progressStyleActive +
    "QProgressBar {"
    "  color: #33ab4c;"
    "}"
    "QProgressBar::chunk {"
    "  background-color: transparent;"
    "}";

static const QString progressStyleError = progressStyleActive +
    "QProgressBar {"
    "  color: red;"
    "}"
    "QProgressBar::chunk {"
    "  background-color: transparent;"
    "}";

ModelsPanel::ModelsPanel(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);

  ListWidgetSP *list = new ListWidgetSP(this, false);
  ScrollViewSP *scroller = new ScrollViewSP(list, this);
  main_layout->addWidget(scroller);

  const auto current_model = GetActiveModelName();
  currentModelLblBtn = new ButtonControlSP(tr("Current Model"), tr("SELECT"), "", this);
  currentModelLblBtn->setValue(current_model);

  connect(currentModelLblBtn, &ButtonControlSP::clicked, this, &ModelsPanel::handleCurrentModelLblBtnClicked);
  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
      is_onroad = !offroad;
      updateLabels();
    });
  connect(uiStateSP(), &UIStateSP::uiUpdate, this, &ModelsPanel::updateLabels);
  list->addItem(currentModelLblBtn);

  // Create progress bars for downloads
  supercomboProgressBar = createProgressBar(this);
  QString supercomboType = tr("Driving Model");
  supercomboFrame = createModelDetailFrame(this, supercomboType, supercomboProgressBar);
  list->addItem(supercomboFrame);

  navigationProgressBar = createProgressBar(this);
  QString navigationType = tr("Navigation Model");
  navigationFrame = createModelDetailFrame(this, navigationType, navigationProgressBar);
  list->addItem(navigationFrame);

  visionProgressBar = createProgressBar(this);
  QString visionType = tr("Vision Model");
  visionFrame = createModelDetailFrame(this, visionType, visionProgressBar);
  list->addItem(visionFrame);

  policyProgressBar = createProgressBar(this);
  QString policyType = tr("Policy Model");
  policyFrame = createModelDetailFrame(this, policyType, policyProgressBar);
  list->addItem(policyFrame);

  list->addItem(horizontal_line());

  // LiveDelay toggle
  lagd_toggle_control = new ParamControlSP("LagdToggle", tr("Live Learning Steer Delay"), "", "../assets/offroad/icon_shell.png");
  lagd_toggle_control->showDescription();
  list->addItem(lagd_toggle_control);

  // Software delay control
  delay_control = new OptionControlSP("LagdToggledelay", tr("Adjust Software Delay"),
                                     tr("Adjust the software delay when Live Learning Steer Delay is toggled off."
                                        "\nThe default software delay value is 0.2"),
                                     "", {10, 30}, 1, false, nullptr, true);

  connect(delay_control, &OptionControlSP::updateLabels, [=]() {
    float value = QString::fromStdString(params.get("LagdToggledelay")).toFloat();
    delay_control->setLabel(QString::number(value, 'f', 2) + "s");
  });
  connect(lagd_toggle_control, &ParamControlSP::toggleFlipped, [=](bool state) {
    delay_control->setVisible(!state);
  });
  delay_control->showDescription();
  list->addItem(delay_control);
}

QProgressBar* ModelsPanel::createProgressBar(QWidget *parent) {
  QProgressBar *progressBar = new QProgressBar(parent);
  progressBar->setRange(0, 100);
  progressBar->setValue(0);
  progressBar->setTextVisible(true);
  progressBar->setAlignment(Qt::AlignVCenter);
  return progressBar;
}

QFrame* ModelsPanel::createModelDetailFrame(QWidget *parent, QString &typeName, QProgressBar *progressBar) {
  QFrame *frame = new QFrame(parent);
  QHBoxLayout *layout = new QHBoxLayout(frame);
  layout->setContentsMargins(0, 0, 0, 0);
  layout->setSpacing(50);
  layout->addWidget(new QLabel(typeName));
  layout->addWidget(progressBar);
  frame->setVisible(false);
  return frame;
}

/**
 * @brief Updates the UI with bundle download progress information
 * Reads status from modelManagerSP cereal message and displays status for all models
 */
void ModelsPanel::handleBundleDownloadProgress() {
  supercomboFrame->setVisible(false);
  visionFrame->setVisible(false);
  policyFrame->setVisible(false);
  navigationFrame->setVisible(false);

  using DS = cereal::ModelManagerSP::DownloadStatus;
  if (!model_manager.hasSelectedBundle() && !model_manager.hasActiveBundle()) {
    return;
  }

  const bool showSelectedBundle = model_manager.hasSelectedBundle() && (isDownloading() || model_manager.getSelectedBundle().getStatus() == DS::FAILED);
  const auto &bundle = showSelectedBundle ? model_manager.getSelectedBundle() : model_manager.getActiveBundle();
  const auto &models = bundle.getModels();
  download_status = bundle.getStatus();
  const auto download_status_changed = prev_download_status != download_status;
  QStringList status;

  // Get status for each model type in order
  for (const auto &model: models) {
    QString modelName = QString::fromStdString(bundle.getDisplayName());

    QProgressBar *progressBar = nullptr;
    QFrame *modelFrame = nullptr;

    switch (model.getType()) {
      case cereal::ModelManagerSP::Model::Type::SUPERCOMBO:
        progressBar = supercomboProgressBar;
        modelFrame = supercomboFrame;
        break;
      case cereal::ModelManagerSP::Model::Type::NAVIGATION:
        progressBar = navigationProgressBar;
        modelFrame = navigationFrame;
        break;
      case cereal::ModelManagerSP::Model::Type::VISION:
        progressBar = visionProgressBar;
        modelFrame = visionFrame;
        break;
      case cereal::ModelManagerSP::Model::Type::POLICY:
        progressBar = policyProgressBar;
        modelFrame = policyFrame;
        break;
    }

    const auto &progress = model.getArtifact().getDownloadProgress();
    QString line;

    if (progress.getStatus() == cereal::ModelManagerSP::DownloadStatus::DOWNLOADING) {
      progressBar->setStyleSheet(progressStyleActive);
      progressBar->setValue(progress.getProgress());
      progressBar->setFormat(QString("  %1% - %2").arg(static_cast<int>(progress.getProgress())).arg(modelName));
      device()->resetInteractiveTimeout();
    } else if (progress.getStatus() == cereal::ModelManagerSP::DownloadStatus::DOWNLOADED) {
      progressBar->setStyleSheet(progressStyleDone);
      progressBar->setFormat(tr("  %1 - %2").arg(modelName, download_status_changed ? tr("downloaded") : tr("ready")));
    } else if (progress.getStatus() == cereal::ModelManagerSP::DownloadStatus::CACHED) {
      progressBar->setStyleSheet(progressStyleDone);
      progressBar->setFormat(tr("  %1 - %2").arg(modelName, download_status_changed ? tr("from cache") : tr("ready")));
    } else if (progress.getStatus() == cereal::ModelManagerSP::DownloadStatus::FAILED) {
      progressBar->setStyleSheet(progressStyleError);
      progressBar->setFormat(tr("  download failed - %1").arg(modelName));
    } else {
      progressBar->setStyleSheet(progressStyleInactive);
      progressBar->setFormat(tr("  pending - %1").arg(modelName));
    }
    // keep navigation hidden for now to avoid confusion
    if (model.getType() != cereal::ModelManagerSP::Model::Type::NAVIGATION) {
      modelFrame->setVisible(true);
    }
  }
  prev_download_status = download_status;
}

/**
 * @brief Gets the name of the currently selected model bundle
 * @return Display name of the selected bundle or default model name
 */
QString ModelsPanel::GetActiveModelName() {
  if (model_manager.hasActiveBundle()) {
    return QString::fromStdString(model_manager.getActiveBundle().getDisplayName());
  }

  return DEFAULT_MODEL;
}

/**
 * @brief Gets the short name of the currently selected model bundle
 * @return Display short name of the selected bundle or default model name
 */
QString ModelsPanel::GetActiveModelInternalName() {
  if (model_manager.hasActiveBundle()) {
    return QString::fromStdString(model_manager.getActiveBundle().getInternalName());
  }
  return DEFAULT_MODEL;
}

void ModelsPanel::updateModelManagerState() {
  const SubMaster &sm = *(uiStateSP()->sm);
  model_manager = sm["modelManagerSP"].getModelManagerSP();
}

/**
 * @brief Handles the model bundle selection button click
 * Displays available bundles, allows selection, and initiates download
 */
void ModelsPanel::handleCurrentModelLblBtnClicked() {
  currentModelLblBtn->setEnabled(false);
  currentModelLblBtn->setValue(tr("Fetching models..."));

  // Create mapping of bundle indices to display names
  QMap<uint32_t, QString> index_to_bundle;
  const auto bundles = model_manager.getAvailableBundles();
  for (const auto &bundle: bundles) {
    index_to_bundle.insert(bundle.getIndex(), QString::fromStdString(bundle.getDisplayName()));
  }

  // Sort bundles by index in descending order
  QStringList bundleNames;
  // Add "Default" as the first option
  bundleNames.append(DEFAULT_MODEL);

  auto indices = index_to_bundle.keys();
  std::sort(indices.begin(), indices.end(), std::greater<uint32_t>());
  for (const auto &index: indices) {
    bundleNames.append(index_to_bundle[index]);
  }

  currentModelLblBtn->setValue(GetActiveModelInternalName());

  const QString selectedBundleName = MultiOptionDialog::getSelection(
    tr("Select a Model"), bundleNames, GetActiveModelName(), this);

  if (selectedBundleName.isEmpty() || !canContinueOnMeteredDialog()) {
    return;
  }

  // Handle "Stock" selection differently
  if (selectedBundleName == DEFAULT_MODEL) {
    params.remove("ModelManager_ActiveBundle");
    currentModelLblBtn->setValue(tr("Default"));
    showResetParamsDialog();
  } else {
    // Find selected bundle and initiate download
    for (const auto &bundle: bundles) {
      if (QString::fromStdString(bundle.getDisplayName()) == selectedBundleName) {
        params.put("ModelManager_DownloadIndex", std::to_string(bundle.getIndex()));
        if (bundle.getGeneration() != model_manager.getActiveBundle().getGeneration()) {
          showResetParamsDialog();
        }
        break;
      }
    }
  }

  updateLabels();
}

/**
 * @brief Updates the UI elements based on current state
 */
void ModelsPanel::updateLabels() {
  if (!isVisible()) {
    return;
  }

  updateModelManagerState();
  handleBundleDownloadProgress();
  currentModelLblBtn->setEnabled(!is_onroad && !isDownloading());
  currentModelLblBtn->setValue(GetActiveModelInternalName());

  // Update lagdToggle description with current value
  QString desc = tr("Enable this for the car to learn and adapt its steering response time. "
                   "Disable to use a fixed steering response time. Keeping this on provides the stock openpilot experience. "
                   "The Current value is updated automatically when the vehicle is Onroad.");
  QString current = QString::fromStdString(params.get("LagdToggleDesc", false));
  if (!current.isEmpty()) {
    desc += "<br><br><b><span style=\"color:#e0e0e0\">" + tr("Current:") + "</span></b> <span style=\"color:#e0e0e0\">" + current + "</span>";
  }
  lagd_toggle_control->setDescription(desc);
  lagd_toggle_control->showDescription();

  delay_control->setVisible(!params.getBool("LagdToggle"));
  if (delay_control->isVisible()) {
    float value = QString::fromStdString(params.get("LagdToggledelay")).toFloat();
    delay_control->setLabel(QString::number(value, 'f', 2) + "s");
    delay_control->showDescription();
  }
}

/**
 * @brief Shows dialog prompting user to reset calibration after model download
 */
void ModelsPanel::showResetParamsDialog() {
  const auto confirmMsg = QString("%1<br><br><b>%2</b><br><br><b>%3</b>")
                          .arg(tr("Model download has started in the background."))
                          .arg(tr("We STRONGLY suggest you to reset calibration."))
                          .arg(tr("Would you like to do that now?"));
  const auto button_text = tr("Reset Calibration");

  QString content("<body><h2 style=\"text-align: center;\">" + tr("Driving Model Selector") + "</h2><br>"
                  "<p style=\"text-align: center; margin: 0 128px; font-size: 50px;\">" + confirmMsg + "</p></body>");

  if (showConfirmationDialog(content, button_text, false)) {
    params.remove("CalibrationParams");
    params.remove("LiveTorqueParameters");
  }
}
