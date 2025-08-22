/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include <algorithm>
#include <QJsonDocument>
#include <QStyle>
#include <QtConcurrent/QtConcurrent>
#include <QDir>

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

  refreshAvailableModelsBtn = new ButtonControlSP(tr("Refresh Model List"), tr("REFRESH"), "", this);
  connect(refreshAvailableModelsBtn, &ButtonControlSP::clicked, this, [=]() {
    params.put("ModelManager_LastSyncTime", "0");
    ConfirmationDialog::alert(tr("Fetching Latest Models"), this);
  });

  list->addItem(refreshAvailableModelsBtn);

  clearModelCacheBtn = new ButtonControlSP(tr("Clear Model Cache"), tr("CLEAR"), "", this);
  connect(clearModelCacheBtn, &ButtonControlSP::clicked, this, &ModelsPanel::clearModelCache);

  list->addItem(clearModelCacheBtn);

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
  int liveDelayMaxInt = 30;
  std::string liveDelayBytes = params.get("LiveDelay");
  if (!liveDelayBytes.empty()) {
    capnp::FlatArrayMessageReader msg(kj::ArrayPtr<const capnp::word>(
      reinterpret_cast<const capnp::word*>(liveDelayBytes.data()),
      liveDelayBytes.size() / sizeof(capnp::word)));
    auto event = msg.getRoot<cereal::Event>();
    if (event.hasLiveDelay()) {
      auto liveDelay = event.getLiveDelay();
      float lateralDelay = liveDelay.getLateralDelay();
      liveDelayMaxInt = static_cast<int>(lateralDelay * 100.0f) + 20;
    }
  }
  delay_control = new OptionControlSP("LagdToggleDelay", tr("Adjust Software Delay"),
                                     tr("Adjust the software delay when Live Learning Steer Delay is toggled off."
                                        "\nThe default software delay value is 0.2"),
                                     "", {5, liveDelayMaxInt}, 1, false, nullptr, true, true);

  connect(delay_control, &OptionControlSP::updateLabels, [=]() {
    float value = QString::fromStdString(params.get("LagdToggleDelay")).toFloat();
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

  struct ModelEntry {
    QString folder;
    QString displayName;
    int index;
  };
  QList<ModelEntry> sortedModels;
  QSet<QString> modelFolders;
  const auto bundles = model_manager.getAvailableBundles();

  for (const auto &bundle : bundles) {
    auto overrides = bundle.getOverrides();
    QString gen;
    for (const auto &override : overrides) {
      if (override.getKey() == "folder") {
        gen = QString::fromStdString(override.getValue().cStr());
      }
    }

    modelFolders.insert(gen);
    sortedModels.append(ModelEntry{
      gen,
      QString::fromStdString(bundle.getDisplayName()),
      static_cast<int>(bundle.getIndex())
    });
  }

  std::sort(sortedModels.begin(), sortedModels.end(),
    [](const ModelEntry &a, const ModelEntry &b) {
      return a.index > b.index;
    });

  // Create a list of folder-maxIndex pairs for sorting
  QList<QPair<QString, int>> folderMaxIndices;
  for (const auto &folder : modelFolders) {
    int maxIndex = -1;
    for (const auto &model : sortedModels) {
      if (model.folder == folder) {
        maxIndex = std::max(maxIndex, model.index);
      }
    }
    folderMaxIndices.append(qMakePair(folder, maxIndex));
  }

  // Sort folders by their highest model index
  std::sort(folderMaxIndices.begin(), folderMaxIndices.end(),
      [](const QPair<QString, int> &a, const QPair<QString, int> &b) {
          return a.second > b.second;
      });

  // Create the final items list using sorted folders
  QList<QPair<QString, QStringList>> items;
  for (const auto &folderPair : folderMaxIndices) {
    QStringList folderModels;
    for (const auto &model : sortedModels) {
      if (model.folder == folderPair.first) {
        folderModels.append(model.displayName);
      }
    }
    items.append(qMakePair(folderPair.first, folderModels));
  }

  items.insert(0, qMakePair(QString(""), QStringList{DEFAULT_MODEL}));

  currentModelLblBtn->setValue(GetActiveModelInternalName());

  const QString selectedBundleName = TreeOptionDialog::getSelection(
    tr("Select a Model"), items, GetActiveModelName(), this);

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
                   "Disable to use a fixed steering response time. Keeping this on provides the stock openpilot experience.");
  bool lagdEnabled = params.getBool("LagdToggle");
  if (lagdEnabled) {
    std::string liveDelayBytes = params.get("LiveDelay");
    if (!liveDelayBytes.empty()) {
      capnp::FlatArrayMessageReader msg(kj::ArrayPtr<const capnp::word>(
        reinterpret_cast<const capnp::word*>(liveDelayBytes.data()),
        liveDelayBytes.size() / sizeof(capnp::word)));
      auto event = msg.getRoot<cereal::Event>();
      if (event.hasLiveDelay()) {
        auto liveDelay = event.getLiveDelay();
        float lateralDelay = liveDelay.getLateralDelay();
        desc += QString("<br><br><b><span style=\"color:#e0e0e0\">%1</span></b> <span style=\"color:#e0e0e0\">%2 s</span>")
                .arg(tr("Live Steer Delay:")).arg(QString::number(lateralDelay, 'f', 3));
      }
    }
  } else {
    std::string carParamsBytes = params.get("CarParamsPersistent");
    if (!carParamsBytes.empty()) {
      capnp::FlatArrayMessageReader msg(kj::ArrayPtr<const capnp::word>(
        reinterpret_cast<const capnp::word*>(carParamsBytes.data()),
        carParamsBytes.size() / sizeof(capnp::word)));
      auto carParams = msg.getRoot<cereal::CarParams>();
      float steerDelay = carParams.getSteerActuatorDelay();
      float softwareDelay = QString::fromStdString(params.get("LagdToggleDelay")).toFloat();
      float totalLag = steerDelay + softwareDelay;
      desc += QString("<br><br><span style=\"color:#e0e0e0\">"
                      "<b>%1</b> %2 s + <b>%3</b> %4 s = <b>%5</b> %6 s</span>")
           .arg(tr("Actuator Delay:"), QString::number(steerDelay, 'f', 2),
                tr("Software Delay:"), QString::number(softwareDelay, 'f', 2),
                tr("Total Delay:"), QString::number(totalLag, 'f', 2));
    }
  }
  lagd_toggle_control->setDescription(desc);

  delay_control->setVisible(!params.getBool("LagdToggle"));
  if (delay_control->isVisible()) {
    float value = QString::fromStdString(params.get("LagdToggleDelay")).toFloat();
    delay_control->setLabel(QString::number(value, 'f', 2) + "s");
  }

  clearModelCacheBtn->setValue(QString::number(calculateCacheSize(), 'f', 2) + " MB");
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

void ModelsPanel::clearModelCache() {
  QString confirmMsg = tr("This will delete ALL downloaded models from the cache"
                            "<br/><u>except the currently active model</u>."
                            "<br/><br/>Are you sure you want to continue?");
  QString content("<body><h2 style=\"text-align: center;\">" + tr("Driving Model Selector") + "</h2><br>"
                "<p style=\"text-align: center; margin: 0 128px; font-size: 50px;\">" + confirmMsg + "</p></body>");
  if (showConfirmationDialog(
    content,
    tr("Clear Cache"))) {
      params.putBool("ModelManager_ClearCache", true);
    }
}

double ModelsPanel::calculateCacheSize() {
  QFuture<qint64> future_ModelCacheSize = QtConcurrent::run([=]() {

    QDir model_dir(QString::fromStdString(Path::model_root()));
    QFileInfoList model_files = model_dir.entryInfoList(QDir::Files | QDir::NoDotAndDotDot);
    qint64 totalSize = 0;
    for (const QFileInfo &model_file : model_files) {
        if (model_file.isFile()) {
            totalSize += model_file.size();
        }
    }
    return totalSize;
  });
  return static_cast<double>(future_ModelCacheSize) / (1024.0 * 1024.0);
}

void ModelsPanel::showEvent(QShowEvent *event) {
  lagd_toggle_control->showDescription();
  if (delay_control->isVisible()) {
    delay_control->showDescription();
  }
}
