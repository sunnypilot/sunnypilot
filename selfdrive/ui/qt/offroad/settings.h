#pragma once

#include <map>
#include <string>

#include <QButtonGroup>
#include <QFrame>
#include <QLabel>
#include <QPushButton>
#include <QStackedWidget>
#include <QTimer>
#include <QWidget>


#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/widgets/controls.h"

// ********** settings window + top-level panels **********
class SettingsWindow : public QFrame {
  Q_OBJECT

public:
  explicit SettingsWindow(QWidget *parent = 0);
  void setCurrentPanel(int index, const QString &param = "");

protected:
  void showEvent(QShowEvent *event) override;

signals:
  void closeSettings();
  void reviewTrainingGuide();
  void showDriverView();
  void expandToggleDescription(const QString &param);

private:
  QPushButton *sidebar_alert_widget;
  QWidget *sidebar_widget;
  QButtonGroup *nav_btns;
  QStackedWidget *panel_widget;
};

class DevicePanel : public ListWidget {
  Q_OBJECT
public:
  explicit DevicePanel(SettingsWindow *parent);
signals:
  void reviewTrainingGuide();
  void showDriverView();

private slots:
  void poweroff();
  void reboot();
  void updateCalibDescription();
  void onPinFileChanged(const QString &file_path);
  void refreshPin();

private:
  Params params;

  ButtonControl *fleetManagerPin;
  const char *pin_title = "Fleet Manager PIN: ";
  QString pin = "OFF";
  QFileSystemWatcher *fs_watch;
};

class TogglesPanel : public ListWidget {
  Q_OBJECT
public:
  explicit TogglesPanel(SettingsWindow *parent);
  void showEvent(QShowEvent *event) override;

public slots:
  void expandToggleDescription(const QString &param);
  void updateToggles();

private:
  Params params;
  std::map<std::string, ParamControl*> toggles;
  ButtonParamControl *long_personality_setting;

  ParamWatcher *param_watcher;
  void updateButtons();
};

class SoftwarePanel : public ListWidget {
  Q_OBJECT
public:
  explicit SoftwarePanel(QWidget* parent = nullptr);

private:
  void showEvent(QShowEvent *event) override;
  void updateLabels();
  void checkForUpdates();

  bool is_onroad = false;

  QLabel *onroadLbl;
  QLabel *osmUpdateLbl;
  LabelControl *currentModelLbl;
  LabelControl *versionLbl;
  ButtonControl *installBtn;
  ButtonControl *downloadBtn;
  ButtonControl *targetBranchBtn;
  ButtonControl *osmDownloadBtn;
  ButtonControl *osmUpdateBtn;

  Params params;
  ParamWatcher *fs_watch;

  inline std::vector<std::tuple<QString, QString, QString, QString>> getOsmLocations() {
    // location_title, location_name, waypoint, url
    std::vector<std::tuple<QString, QString, QString, QString>> locations{
      {
        "== None ==",
        "",
        "",
        "",
      },
      {
        "Australia",
        "australia",
        "514911884",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EathcAhPP8dHiTdBiFPIGYoB7zwlUR79OkSTH5dnS-9Shg?e=9cS6er&download=1",
      },
      {
        "Brazil",
        "brazil",
        "124199196",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EXWcrd8ukahDtoFDXVOxvkYBjGGa9b29fVvRdJlADv3YdA?e=jwabo2&download=1",
      },
      {
        "Canada",
        "canada",
        "68588664",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/ETpwTMZftJpCkep2goPmzUQBl5SW_YfHBKLTd7w5CUagkA?e=dshC10&download=1",
      },
      {
        "GCC States",
        "gcc-states",
        "69021390",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EWtFOVR9mj5CoRpATYR0_tUBWNEcy5jeasp8zO0ZYdduRg?e=Cg0l2Z&download=1",
      },
      {
        "Germany",
        "germany",
        "461526153",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EbNzQuA8jHBCuGch1WY4cuoBJfK1S6m5odj5qMnOu3HA3Q?e=cNDn30&download=1",
      },
      {
        "Malaysia, Singapore, Brunei",
        "malaysia-singapore-brunei",
        "1112741782",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EQb9bq_YkE1NuFx0jp-52zoBnAbdo4nyLXMnEY1pUbCB8g?e=CoFiUJ&download=1",
      },
      {
        "New Zealand",
        "new-zealand",
        "154430132",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EVI6eMuNa4dJpXg-r92Vw1EBq5RxR83_7Z5C56AYftg8xQ?e=xouRBl&download=1",
      },
      {
        "South Africa",
        "south-africa",
        "2729449",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EQzbZeus-yBNsgP1KQyLn9wBYZVMMknVoHdB7_ewulLbdA?e=DrnKkb&download=1",
      },
      {
        "Spain",
        "spain",
        "4263034",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/Ee21EfLqZxxLjksDCB_2dscBXKN9Kch8ZOYz3cIWnVpBTg?e=LWBJ1n&download=1",
      },
      {
        "Taiwan",
        "taiwan",
        "198637969",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EXgP3Z5_lsBPiQe-aXOOSY4Bu-r54Z_3kKKmT8-IqLO42A?e=tOhUYw&download=1",
      },
      {
        "Turkey",
        "turkey",
        "698359658",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EWJRrYpV7I1IvOW0LUWrDsUBjEjuKRTla0hA4yRbsVX2xw?e=RGcu8n&download=1",
      },
      {
        "US - Florida",
        "florida",
        "147221754",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/ET9rAvCaretAnO4TjocAddkBFxAziblxblAn9YWzGk5hTw?e=tts5Oz&download=1",
      },
      {
        "US - Midwest",
        "us-midwest",
        "1059596607",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EaDYnugxokRHhOukMndJuZMBKz-kzPfM6C_-iQcki-r94Q?e=oUX6hz&download=1",
      },
      {
        "US - Northeast",
        "us-northeast",
        "575213527",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/ERrlIKNuT4ZIuUOfr4a3BwABLfd7X1wSq9nUrk9buKrIgA?e=HHIT8R&download=1",
      },
      {
        "US - Pacific",
        "us-pacific",
        "112909709",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/EQOzoMksk9tAluahQ2qm3rQBHOZD03qFU8Aw4o-TFUTuJA?e=CcBOxL&download=1",
      },
      {
        "US - South",
        "us-south",
        "243729876",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/ETizacxh8lFNk8NMVRyKCEsBMMYZl1iq0r-D4IWoOAd_DQ?e=EVIElm&download=1",
      },
      {
        "US - West",
        "us-west",
        "30023440",
        "https://thecorgirosie-my.sharepoint.com/:u:/g/personal/databases_sunnypilot_com/ETTRiSKwlEVKoRHtylruy7wBKgITKXdaCUAkJMuGAN2_mA?e=7jlglL&download=1",
      },
    };
    return locations;
  }
};
