/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <deque>
#include <chrono>
#include <map>
#include <optional>
#include <string>
#include <tuple>
#include <vector>
#include <QDir>
#include <QFileInfo>
#include <QtConcurrent/QtConcurrent>

#include "selfdrive/ui/qt/network/wifi_manager.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/osm/locations_fetcher.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/sunnypilot/ui.h"
#include "system/hardware/hw.h"

constexpr int FAST_REFRESH_INTERVAL = 1000; // ms
constexpr int SLOW_REFRESH_INTERVAL = 5000; // ms

static const QString MAP_PATH = Hardware::PC() ? QDir::homePath() + "/.comma/media/0/osm/offline/" : "/data/media/0/osm/offline/";

class OsmPanel : public QFrame {
  Q_OBJECT

public:
  explicit OsmPanel(QWidget *parent = nullptr);

private:
  QStackedLayout *main_layout = nullptr;
  QWidget *osmScreen = nullptr;
  Params params;
  Params mem_params{Hardware::PC() ? "" : "/dev/shm/params"};
  std::map<std::string, ParamControlSP *> toggles;
  std::optional<QFuture<quint64> > mapSizeFuture;
  const SubMaster &sm = *uiStateSP()->sm;


  bool is_onroad = false;
  std::string mapd_version;

  bool isWifi() const { return sm["deviceState"].getDeviceState().getNetworkType() == cereal::DeviceState::NetworkType::WIFI; }
  bool isMetered() const { return sm["deviceState"].getDeviceState().getNetworkMetered(); }
  bool osm_download_in_progress = false;
  bool download_failed_state = false;
  quint64 mapsDirSize = 0;

  QLabel *osmUpdateLbl;
  ButtonControlSP *osmDownloadBtn;
  ButtonControlSP *osmUpdateBtn;
  ButtonControlSP *usStatesBtn;
  ButtonControlSP *osmDeleteMapsBtn;

  ButtonControlSP *setupOsmDeleteMapsButton(QWidget *parent);;
  ButtonControlSP *setupOsmUpdateButton(QWidget *parent);
  ButtonControlSP *setupOsmDownloadButton(QWidget *parent);
  ButtonControlSP *setupUsStatesButton(QWidget *parent);

  QTimer *timer;
  std::string osm_download_locations;
  //  void updateButtonControlSP(ButtonControlSP *btnControl, QWidget *parent, const QString &initTitle, const QString &allStatesOption);

  void showEvent(QShowEvent *event) override;
  void hideEvent(QHideEvent *event) override;
  void updateLabels();
  void updateDownloadProgress();
  static int extractIntFromJson(const QJsonObject &json, const QString &key);
  QString processUpdateStatus(bool pending_update_check, int total_files, int downloaded_files, const QJsonObject &json, bool failed_state);
  QString search(const QString &query, const QStringList &list, const QString &prompt_text);

  ConfirmationDialog *confirmationDialog;
  LabelControlSP *mapdVersion;
  LabelControlSP *offlineMapsStatus;
  LabelControlSP *offlineMapsETA;
  LabelControlSP *offlineMapsElapsed;
  std::optional<std::chrono::system_clock::time_point> lastDownloadedTimePoint;
  LocationsFetcher locationsFetcher;

  void updateMapSize();

  bool showConfirmationDialog(QWidget *parent,
                              const QString &message = QString(),
                              const QString &confirmButtonText = QString()) const {
    const auto _is_metered = isMetered();
    const QString warning_message = _is_metered ? tr("\n\nWarning: You are on a metered connection!") : QString();
    QString final_message = message.isEmpty() ? tr("This will start the download process and it might take a while to complete.") : message;
    final_message += warning_message; // Append the warning message if the connection is metered

    const QString final_buttonText = confirmButtonText.isEmpty() ? (_is_metered ? tr("Continue on Metered") : tr("Start Download")) : confirmButtonText;

    return ConfirmationDialog::confirm(final_message, final_buttonText, parent);
  }

  // Refactored methods
  std::vector<std::tuple<QString, QString, QString, QString> > getOsmLocations(const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    return locationsFetcher.getOsmLocations(customLocation);
  }

  std::vector<std::tuple<QString, QString, QString, QString> > getUsStatesLocations(const std::tuple<QString, QString> &customLocation = defaultLocation) const {
    return locationsFetcher.getUsStatesLocations(customLocation);
  }

  static QString formatTime(const long timeInSeconds) {
    const long minutes = timeInSeconds / 60;
    const long seconds = timeInSeconds % 60;

    QString formattedTime;
    if (minutes > 0) {
      formattedTime = QString::number(minutes) + tr("m ");
    }
    formattedTime += QString::number(seconds) + tr("s");
    return formattedTime;
  }

  static QString calculateElapsedTime(const QJsonObject &jsonData, const std::chrono::system_clock::time_point &startTime) {
    using namespace std::chrono;
    if (!jsonData.contains("total_files") || !jsonData.contains("downloaded_files"))
      return tr("Calculating...");

    const int totalFiles = jsonData["total_files"].toInt();
    const int downloadedFiles = jsonData["downloaded_files"].toInt();

    if (downloadedFiles >= totalFiles || totalFiles <= 0) return tr("Downloaded");

    const long elapsed = duration_cast<seconds>(system_clock::now() - startTime).count();

    if (elapsed == 0 || downloadedFiles == 0) return tr("Calculating...");

    return formatTime(elapsed);
  }

  static QString calculateETA(const QJsonObject &jsonData, const std::chrono::system_clock::time_point &startTime) {
    using namespace std::chrono;
    static steady_clock::time_point lastUpdateTime = steady_clock::now();
    static std::deque<double> rateHistory;

    constexpr int minDataPoints = 3;
    constexpr int historySize = 10;

    static QString lastETA = tr("Calculating ETA...");

    if (duration_cast<seconds>(steady_clock::now() - lastUpdateTime).count() < 1) {
      return lastETA;
    }

    if (!jsonData.contains("total_files") || !jsonData.contains("downloaded_files"))
      return lastETA;

    const int totalFiles = jsonData["total_files"].toInt();
    const int downloadedFiles = jsonData["downloaded_files"].toInt();

    if (totalFiles <= 0 || downloadedFiles >= totalFiles) {
      return totalFiles <= 0 ? tr("Ready") : tr("Downloaded");
    }

    const long elapsed = duration_cast<seconds>(system_clock::now() - startTime).count();
    if (elapsed == 0 || downloadedFiles == 0) return lastETA;

    const double rate = downloadedFiles / static_cast<double>(elapsed);
    if (rateHistory.size() >= historySize) rateHistory.pop_front();
    rateHistory.push_back(rate);

    if (rateHistory.size() < minDataPoints) return lastETA;

    double weightedSum = 0;
    for (int i = 0, weight = 1; i < rateHistory.size(); ++i, ++weight) {
      weightedSum += rateHistory[i] * weight;
    }
    const double avgRate = 2 * weightedSum / (rateHistory.size() * (rateHistory.size() + 1));

    const long remainingTime = static_cast<long>((totalFiles - downloadedFiles) / avgRate);
    if (remainingTime <= 0) return lastETA;

    lastETA = tr("Time remaining: ") + formatTime(remainingTime);
    lastUpdateTime = steady_clock::now();
    return lastETA;
  }

  static QString formatDownloadStatus(const QJsonObject &json) {
    if (!json.contains("total_files") || !json.contains("downloaded_files"))
      return "";

    const int total_files = json["total_files"].toInt();
    const int downloaded_files = json["downloaded_files"].toInt();

    if (total_files <= 0) return tr("Ready");
    if (downloaded_files >= total_files) return tr("Downloaded");

    const int percentage = static_cast<int>(100.0 * downloaded_files / total_files);
    return QString::asprintf("%d/%d (%d%%)", downloaded_files, total_files, percentage);
  }

  QString formatSize(quint64 size) const {
    if (size == 0 && (!mapSizeFuture.has_value() || mapSizeFuture.value().isRunning())) {
      return tr("Calculating...");
    }

    constexpr qint64 kb = 1024;
    constexpr qint64 mb = 1024 * kb;
    constexpr qint64 gb = 1024 * mb;

    if (size < gb) {
      const double sizeMB = size / static_cast<double>(mb);
      return QString::number(sizeMB, 'f', 2) + " MB";
    } else {
      const double sizeGB = size / static_cast<double>(gb);
      return QString::number(sizeGB, 'f', 2) + " GB";
    }
  }

  static quint64 getDirSize(QString dirPath) {
    quint64 size = 0;
    const QString actualDirPath = dirPath.startsWith("~") ? dirPath.replace(0, 1, QDir::homePath()) : dirPath;
    QDirIterator it(actualDirPath, QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot | QDir::NoSymLinks, QDirIterator::Subdirectories);
    while (it.hasNext()) {
      it.next();
      if (it.fileInfo().isFile()) {
        size += it.fileInfo().size();
      }
    }
    return size;
  }
};
