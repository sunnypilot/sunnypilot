#include "selfdrive/ui/qt/widgets/ssh_keys.h"

#include <QProcess>
#include <QMenu>

#include "selfdrive/common/params.h"
#include "selfdrive/ui/qt/api.h"
#include "selfdrive/ui/qt/widgets/input.h"

SshControl::SshControl() : ButtonControl("SSH Keys", "", "Warning: This grants SSH access to all public keys in your GitHub settings. Never enter a GitHub username other than your own. A comma employee will NEVER ask you to add their GitHub username.") {
  username_label.setAlignment(Qt::AlignRight | Qt::AlignVCenter);
  username_label.setStyleSheet("color: #aaaaaa");
  hlayout->insertWidget(1, &username_label);

  QObject::connect(this, &ButtonControl::clicked, [=]() {
    if (text() == "ADD") {
      QString username = InputDialog::getText("Enter your GitHub username", this);
      if (username.length() > 0) {
        setText("LOADING");
        setEnabled(false);
        getUserKeys(username);
      }
    } else {
      params.remove("GithubUsername");
      params.remove("GithubSshKeys");
      refresh();
    }
  });

  refresh();
}

void SshControl::refresh() {
  QString param = QString::fromStdString(params.get("GithubSshKeys"));
  if (param.length()) {
    username_label.setText(QString::fromStdString(params.get("GithubUsername")));
    setText("REMOVE");
  } else {
    username_label.setText("");
    setText("ADD");
  }
  setEnabled(true);
}

void SshControl::getUserKeys(const QString &username) {
  HttpRequest *request = new HttpRequest(this, false);
  QObject::connect(request, &HttpRequest::receivedResponse, [=](const QString &resp) {
    if (!resp.isEmpty()) {
      params.put("GithubUsername", username.toStdString());
      params.put("GithubSshKeys", resp.toStdString());
    } else {
      ConfirmationDialog::alert("Username '" + username + "' has no keys on GitHub", this);
    }
    refresh();
    request->deleteLater();
  });
  QObject::connect(request, &HttpRequest::failedResponse, [=] {
    ConfirmationDialog::alert("Username '" + username + "' doesn't exist on GitHub", this);
    refresh();
    request->deleteLater();
  });
  QObject::connect(request, &HttpRequest::timeoutResponse, [=] {
    ConfirmationDialog::alert("Request timed out", this);
    refresh();
    request->deleteLater();
  });

  request->sendRequest("https://github.com/" + username + ".keys");
}

// Features - Force Car Recognition
CarRecognition::CarRecognition() : AbstractControl("Force Car Recognition", "If the vehicle cannot be recognized due to a fingerprint problem, select the vehicle and force recognition.", "") {

  // setup widget
  hlayout->addStretch(1);

  //carname_label.setAlignment(Qt::AlignVCenter);
  carname_label.setStyleSheet("color: #aaaaaa; font-size: 45px;");
  hlayout->addWidget(&carname_label);
  QMenu *vehicle_select_menu = new QMenu();
  vehicle_select_menu->addAction("ELANTRA", [=]() {carname = "ELANTRA";});
  vehicle_select_menu->addAction("ELANTRA_2021", [=]() {carname = "ELANTRA_2021";});
  vehicle_select_menu->addAction("ELANTRA_HEV_2021", [=]() {carname = "ELANTRA_HEV_2021";});
  vehicle_select_menu->addAction("ELANTRA_GT_I30", [=]() {carname = "ELANTRA_GT_I30";});
  vehicle_select_menu->addAction("HYUNDAI_GENESIS", [=]() {carname = "HYUNDAI_GENESIS";});
  vehicle_select_menu->addAction("IONIQ", [=]() {carname = "IONIQ";});
  vehicle_select_menu->addAction("IONIQ_EV_LTD", [=]() {carname = "IONIQ_EV_LTD";});
  vehicle_select_menu->addAction("IONIQ_EV_2020", [=]() {carname = "IONIQ_EV_2020";});
  vehicle_select_menu->addAction("IONIQ_PHEV", [=]() {carname = "IONIQ_PHEV";});
  vehicle_select_menu->addAction("KONA", [=]() {carname = "KONA";});
  vehicle_select_menu->addAction("KONA_EV", [=]() {carname = "KONA_EV";});
  vehicle_select_menu->addAction("SANTA_FE", [=]() {carname = "SANTA_FE";});
  vehicle_select_menu->addAction("SONATA", [=]() {carname = "SONATA";});
  vehicle_select_menu->addAction("SONATA_LF", [=]() {carname = "SONATA_LF";});
  vehicle_select_menu->addAction("PALISADE", [=]() {carname = "PALISADE";});
  vehicle_select_menu->addAction("VELOSTER", [=]() {carname = "VELOSTER";});
  vehicle_select_menu->addAction("SONATA_HYBRID", [=]() {carname = "SONATA_HYBRID";});

  vehicle_select_menu->addAction("KIA_FORTE", [=]() {carname = "KIA_FORTE";});
  vehicle_select_menu->addAction("KIA_NIRO_EV", [=]() {carname = "KIA_NIRO_EV";});
  vehicle_select_menu->addAction("KIA_NIRO_HEV", [=]() {carname = "KIA_NIRO_HEV";});
  vehicle_select_menu->addAction("KIA_OPTIMA", [=]() {carname = "KIA_OPTIMA";});
  vehicle_select_menu->addAction("KIA_OPTIMA_H", [=]() {carname = "KIA_OPTIMA_H";});
  vehicle_select_menu->addAction("KIA_SELTOS", [=]() {carname = "KIA_SELTOS";});
  vehicle_select_menu->addAction("KIA_SORENTO", [=]() {carname = "KIA_SORENTO";});
  vehicle_select_menu->addAction("KIA_STINGER", [=]() {carname = "KIA_STINGER";});
  vehicle_select_menu->addAction("KIA_CEED", [=]() {carname = "KIA_CEED";});

  vehicle_select_menu->addAction("GENESIS_G70", [=]() {carname = "GENESIS_G70";});
  vehicle_select_menu->addAction("GENESIS_G80", [=]() {carname = "GENESIS_G80";});
  vehicle_select_menu->addAction("GENESIS_G80", [=]() {carname = "GENESIS_G90";});

  QPushButton *set_vehicle_btn = new QPushButton("SELECT");
  set_vehicle_btn->setMenu(vehicle_select_menu);
  hlayout->addWidget(set_vehicle_btn);

  btn.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btn.setFixedSize(200, 100);
  hlayout->addWidget(&btn);

  QObject::connect(&btn, &QPushButton::clicked, [=]() {
    if (btn.text() == "SET" && carname.length()) {
      params.put("CarModel", carname.toStdString());
      params.put("CarModelAbb", carname.toStdString());
      QProcess::execute("/data/openpilot/force_car_set.sh");
      refresh(carname);
    } else {
      carname = "";
      //params.put("CarModel", "");
      params.remove("CarModel");
      params.remove("CarModelAbb");
      refresh(carname);
    }
  });
  refresh(carname);
}

void CarRecognition::refresh(QString carname) {
  QString param = QString::fromStdString(params.get("CarModelAbb"));
  if (carname.length()) {
    carname_label.setText(carname);
    btn.setText("REMOVE");
  } else if (param.length()) {
    carname_label.setText(QString::fromStdString(params.get("CarModelAbb")));
    btn.setText("REMOVE");
  } else {
    carname_label.setText("");
    btn.setText("SET");
  }
}

CarForceSet::CarForceSet() : AbstractControl("Force Car Recognition", "If the vehicle is not recognized due to a fingerprint problem, enter the vehicle name to force recognition.\n\nInput method) Refer to the following and enter only the vehicle name in capital letters.\nELANTRA, ELANTRA_2021, ELANTRA_HEV_2021, ELANTRA_GT_I30, HYUNDAI_GENESIS, IONIQ, IONIQ_EV_LTD, IONIQ_EV_2020, IONIQ_PHEV, KONA, KONA_EV, SANTA_FE, SONATA, SONATA_LF, PALISADE, VELOSTER, SONATA_HYBRID, KIA_FORTE, KIA_NIRO_EV, KIA_NIRO_HEV, KIA_OPTIMA, KIA_OPTIMA_H, KIA_SELTOS, KIA_SORENTO, KIA_STINGER, KIA_CEED, GENESIS_G70, GENESIS_G80, GENESIS_G80", "../assets/offroad/icon_shell.png") {

  // setup widget
  //hlayout->addStretch(1);

  //carname_label.setAlignment(Qt::AlignVCenter);
  //carname_label.setStyleSheet("color: #aaaaaa");
  //hlayout->addWidget(&carname_label);

  btnc.setStyleSheet(R"(
    padding: 0;
    border-radius: 50px;
    font-size: 35px;
    font-weight: 500;
    color: #E4E4E4;
    background-color: #393939;
  )");
  btnc.setFixedSize(250, 100);
  hlayout->addWidget(&btnc);

  QObject::connect(&btnc, &QPushButton::clicked, [=]() {
    if (btnc.text() == "SET") {
      carname = InputDialog::getText("Check the vehicle name by clicking on the previous menu", this);
      if (carname.length() > 0) {
        btnc.setText("DONE");
        btnc.setEnabled(false);
        params.put("CarModel", carname.toStdString());
        QProcess::execute("/data/openpilot/force_car_set.sh");
      }
    } else {
      params.remove("CarModel");
      refreshc();
    }
  });

  refreshc();
}

void CarForceSet::refreshc() {
  QString paramc = QString::fromStdString(params.get("CarModel"));
  if (paramc.length()) {
    //carname_label.setText(QString::fromStdString(params.get("CarModel")));
    btnc.setText("REMOVE");
  } else {
    //carname_label.setText("");
    btnc.setText("SET");
  }
  btnc.setEnabled(true);
}