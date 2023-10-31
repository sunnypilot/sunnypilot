#include "selfdrive/ui/qt/offroad/sunnypilot/osm_settings.h"

OsmPanel::OsmPanel(QWidget *parent) : QFrame(parent) {
  main_layout = new QStackedLayout(this);

  ListWidget *list = new ListWidget(this, false);
  // param, title, desc, icon
  std::vector<std::tuple<QString, QString, QString, QString>> toggle_defs{
    {
      "OsmLocalDb",
      tr("Use Offline Database"),
      "",
      "../assets/offroad/icon_blank.png",
    }
  };

  for (auto &[param, title, desc, icon] : toggle_defs) {
    auto toggle = new ParamControl(param, title, desc, icon, this);

    list->addItem(toggle);
    toggles[param.toStdString()] = toggle;
  }

  osmUpdateLbl = new QLabel(tr("Database updates can be downloaded while the car is off."));
  osmUpdateLbl->setStyleSheet("font-size: 50px; font-weight: 400; text-align: left; padding-top: 30px; padding-bottom: 30px;");
  list->addItem(osmUpdateLbl);

  osmUpdateBtn = new ButtonControl(tr("OpenStreetMap Database Update"), tr("CHECK"));
  connect(osmUpdateBtn, &ButtonControl::clicked, [=]() {
    if (ConfirmationDialog::confirm(tr("Are you sure you want to reboot and perform a database update?\nEstimated time: 30-90 minutes"), tr("Reboot"), parent)) {
      params.putBool("OsmDbUpdatesCheck", true);
      Hardware::reboot();
    }
  });
  list->addItem(osmUpdateBtn);

  osmDownloadBtn = new ButtonControl(tr("OpenStreetMap Database"), tr("SELECT"));
  connect(osmDownloadBtn, &ButtonControl::clicked, [=]() {
    std::vector<std::tuple<QString, QString, QString, QString>> locations = getOsmLocations();
    QString initTitle = QString::fromStdString(params.get("OsmLocationTitle"));
    QString currentTitle = ((initTitle == "== None ==") || (initTitle.length() == 0)) ? "== None ==" : initTitle;

    QStringList locationTitles;
    for (auto& loc : locations) {
      locationTitles.push_back(std::get<0>(loc));
    }

    QString selection = MultiOptionDialog::getSelection(tr("Select your location"), locationTitles, currentTitle, this);
    if (!selection.isEmpty()) {
      params.put("OsmLocal", "1");
      params.put("OsmLocationTitle", selection.toStdString());
      for (auto& loc : locations) {
        if (std::get<0>(loc) == selection) {
          params.put("OsmLocationName", std::get<1>(loc).toStdString());
          params.put("OsmWayTest", std::get<2>(loc).toStdString());
          params.put("OsmLocationUrl", std::get<3>(loc).toStdString());
          break;
        }
      }
      osmDownloadBtn->setValue(selection);
      if (selection != "== None ==") {
        if (ConfirmationDialog::confirm(tr("Are you sure you want to reboot to start downloading the selected database? Estimated time: 30-90 minutes"), tr("Reboot"), parent)) {
          params.putBool("OsmDbUpdatesCheck", true);
          Hardware::reboot();
        }
      }
    }
    updateLabels();
  });
  list->addItem(osmDownloadBtn);

  connect(uiState(), &UIState::offroadTransition, [=](bool offroad) {
    is_onroad = !offroad;
    updateLabels();
  });

  updateLabels();

  osmScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(osmScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  vlayout->addWidget(new ScrollView(list, this), 1);
  main_layout->addWidget(osmScreen);
}

void OsmPanel::showEvent(QShowEvent *event) {
  updateLabels();
}

void OsmPanel::updateLabels() {
  if (!isVisible()) {
    return;
  }

  QString name = QString::fromStdString(params.get("OsmLocationName"));
  if (!name.isEmpty()) {
    osmUpdateBtn->setVisible(!is_onroad);
  } else {
    params.remove("OsmLocal");
    osmUpdateBtn->setVisible(false);
  }
  osmUpdateLbl->setVisible(is_onroad);
  osmDownloadBtn->setEnabled(!is_onroad);

  osmDownloadBtn->setValue(QString::fromStdString(params.get("OsmLocationTitle")));

  update();
}
