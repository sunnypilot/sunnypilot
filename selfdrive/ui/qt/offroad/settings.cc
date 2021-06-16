#include "settings.h"

#include <cassert>
#include <string>
#include <QProcess>

#ifndef QCOM
#include "selfdrive/ui/qt/offroad/networking.h"
#endif
#include "selfdrive/common/params.h"
#include "selfdrive/common/util.h"
#include "selfdrive/hardware/hw.h"
#include "selfdrive/ui/qt/widgets/controls.h"
#include "selfdrive/ui/qt/widgets/input.h"
#include "selfdrive/ui/qt/widgets/offroad_alerts.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"
#include "selfdrive/ui/qt/widgets/ssh_keys.h"
#include "selfdrive/ui/qt/widgets/toggle.h"
#include "selfdrive/ui/ui.h"
#include "selfdrive/ui/qt/util.h"

TogglesPanel::TogglesPanel(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *toggles_list = new QVBoxLayout();

  QList<ParamControl*> toggles;

  toggles.append(new ParamControl("OpenpilotEnabledToggle",
                                  "오픈파일럿 사용",
                                  "어댑티브 크루즈 컨트롤 및 차선 유지 지원을 위해 오픈파일럿 시스템을 사용하십시오. 이 기능을 사용하려면 항상 주의를 기울여야 합니다. 이 설정을 변경하는 것은 자동차의 전원이 꺼졌을 때 적용됩니다.",
                                  "../assets/offroad/icon_openpilot.png",
                                  this));
  toggles.append(new ParamControl("IsLdwEnabled",
                                  "차선이탈 경보 사용",
                                  "50km/h이상의 속도로 주행하는 동안 방향 지시등이 활성화되지 않은 상태에서 차량이 감지된 차선 위를 넘어갈 경우 원래 차선으로 다시 방향을 전환하도록 경고를 보냅니다.",
                                  "../assets/offroad/icon_warning.png",
                                  this));
  toggles.append(new ParamControl("IsRHD",
                                  "우핸들 운전방식 사용",
                                  "오픈파일럿이 좌측 교통 규칙을 준수하도록 허용하고 우측 운전석에서 운전자 모니터링을 수행하십시오.",
                                  "../assets/offroad/icon_openpilot_mirrored.png",
                                  this));
  toggles.append(new ParamControl("IsMetric",
                                  "미터법 사용",
                                  "mi/h 대신 km/h 단위로 속도를 표시합니다.",
                                  "../assets/offroad/icon_metric.png",
                                  this));
  toggles.append(new ParamControl("CommunityFeaturesToggle",
                                  "커뮤니티 기능 사용",
                                  "comma.ai에서 유지 또는 지원하지 않고 표준 안전 모델에 부합하는 것으로 확인되지 않은 오픈 소스 커뮤니티의 기능을 사용하십시오. 이러한 기능에는 커뮤니티 지원 자동차와 커뮤니티 지원 하드웨어가 포함됩니다. 이러한 기능을 사용할 때는 각별히 주의해야 합니다.",
                                  "../assets/offroad/icon_shell.png",
                                  this));

  toggles.append(new ParamControl("UploadRaw",
                                 "주행 로그 업로드",
                                 "업로드 프로세스 활성화 시 모든 로그 및 풀 해상도 비디오를 업로드합니다.(WiFi 사용중에만 작동) 기능이 꺼진 경우, my.comma.ai/useradmin에 업로드를 위해 개별 로그는 기록될 수 있습니다.",
                                 "../assets/offroad/icon_network.png",
                                 this));

  ParamControl *record_toggle = new ParamControl("RecordFront",
                                                 "운전자 영상 녹화 및 업로드",
                                                 "운전자 모니터링 카메라에서 데이터를 업로드하고 운전자 모니터링 알고리즘을 개선하십시오.",
                                                 "../assets/offroad/icon_network.png",
                                                 this);
  toggles.append(record_toggle);
  toggles.append(new ParamControl("EndToEndToggle",
                                   "차선 비활성화 모드 (알파)",
                                   "이 모드에서 오픈파일럿은 차선을 따라 주행하지 않고 사람이 운전하는 것 처럼 주행합니다.",
                                   "../assets/offroad/icon_road.png",
                                   this));

  if (Hardware::TICI()) {
    toggles.append(new ParamControl("EnableWideCamera",
                                    "Enable use of Wide Angle Camera",
                                    "Use wide angle camera for driving and ui.",
                                    "../assets/offroad/icon_openpilot.png",
                                    this));
    QObject::connect(toggles.back(), &ToggleControl::toggleFlipped, [=](bool state) {
      Params().remove("CalibrationParams");
    });

    toggles.append(new ParamControl("EnableLteOnroad",
                                    "Enable LTE while onroad",
                                    "",
                                    "../assets/offroad/icon_network.png",
                                    this));
  }

  toggles.append(new ParamControl("OpkrEnableDriverMonitoring",
                                  "운전자 모니터링 사용",
                                  "운전자 감시 모니터링을 사용합니다.",
                                  "../assets/offroad/icon_shell.png",
                                  this));
  toggles.append(new ParamControl("OpkrEnableLogger",
                                  "주행로그 기록 사용",
                                  "로컬에서 데이터 분석을 위해 주행로그를 기록합니다. 로거만 활성화 되며 서버로 업로드 되지 않습니다.",
                                  "../assets/offroad/icon_shell.png",
                                  this));
  toggles.append(new ParamControl("OpkrEnableUploader",
                                  "주행로그 서버 전송",
                                  "시스템로그 및 기타 주행데이터를 서버로 전송하기 위해 업로드 프로세스를 활성화 합니다. 오프로드 상태에서만 업로드 합니다.",
                                  "../assets/offroad/icon_shell.png",
                                  this));
  toggles.append(new ParamControl("CommaStockUI",
                                  "Comma Stock UI 사용",
                                  "주행화면을 콤마의 순정 UI를 사용합니다. 주행화면 좌측상단의 박스를 눌러도 실시간 전환 가능합니다.",
                                  "../assets/offroad/icon_shell.png",
                                  this));

  bool record_lock = Params().getBool("RecordFrontLock");
  record_toggle->setEnabled(!record_lock);

  for(ParamControl *toggle : toggles){
    if(toggles_list->count() != 0){
      toggles_list->addWidget(horizontal_line());
    }
    toggles_list->addWidget(toggle);
  }

  setLayout(toggles_list);
}

DevicePanel::DevicePanel(QWidget* parent) : QWidget(parent) {
  QVBoxLayout *device_layout = new QVBoxLayout;
  Params params = Params();

  QString dongle = QString::fromStdString(params.get("DongleId", false));
  device_layout->addWidget(new LabelControl("Dongle ID", dongle));
  device_layout->addWidget(horizontal_line());

  QString serial = QString::fromStdString(params.get("HardwareSerial", false));
  device_layout->addWidget(new LabelControl("Serial", serial));

  // offroad-only buttons
  QList<ButtonControl*> offroad_btns;

  offroad_btns.append(new ButtonControl("운전자 영상", "미리보기",
                                        "운전자 모니터링 카메라를 미리 보고 장치 장착 위치를 최적화하여 최상의 운전자 모니터링 환경을 제공하십시오. (차량이 꺼져 있어야 합니다.)",
                                        [=]() { emit showDriverView(); }, "", this));

  QString resetCalibDesc = "오픈파일럿을 사용하려면 장치를 왼쪽 또는 오른쪽으로 4°, 위 또는 아래로 5° 이내에 장착해야 합니다. 오픈파일럿이 지속적으로 보정되고 있으므로 재설정할 필요가 거의 없습니다.";
  ButtonControl *resetCalibBtn = new ButtonControl("캘리브레이션정보", "확인", resetCalibDesc, [=]() {
    QString desc = "[기준값: L/R 4°및 UP/DN 5°이내]";
    std::string calib_bytes = Params().get("CalibrationParams");
    if (!calib_bytes.empty()) {
      try {
        AlignedBuffer aligned_buf;
        capnp::FlatArrayMessageReader cmsg(aligned_buf.align(calib_bytes.data(), calib_bytes.size()));
        auto calib = cmsg.getRoot<cereal::Event>().getLiveCalibration();
        if (calib.getCalStatus() != 0) {
          double pitch = calib.getRpyCalib()[1] * (180 / M_PI);
          double yaw = calib.getRpyCalib()[2] * (180 / M_PI);
          desc += QString("\n장치가 %1° %2 그리고 %3° %4 위치해 있습니다.")
                                .arg(QString::number(std::abs(pitch), 'g', 1), pitch > 0 ? "위로" : "아래로",
                                     QString::number(std::abs(yaw), 'g', 1), yaw > 0 ? "오른쪽으로" : "왼쪽으로");
        }
      } catch (kj::Exception) {
        qInfo() << "캘리브레이션 파라미터 유효하지 않음";
      }
    }
    if (ConfirmationDialog::confirm(desc)) {
      //Params().remove("CalibrationParams");
    }
  }, "", this);
  connect(resetCalibBtn, &ButtonControl::showDescription, [=]() {
    QString desc = resetCalibDesc;
    std::string calib_bytes = Params().get("CalibrationParams");
    if (!calib_bytes.empty()) {
      try {
        AlignedBuffer aligned_buf;
        capnp::FlatArrayMessageReader cmsg(aligned_buf.align(calib_bytes.data(), calib_bytes.size()));
        auto calib = cmsg.getRoot<cereal::Event>().getLiveCalibration();
        if (calib.getCalStatus() != 0) {
          double pitch = calib.getRpyCalib()[1] * (180 / M_PI);
          double yaw = calib.getRpyCalib()[2] * (180 / M_PI);
          desc += QString("\n장치가 %1° %2 그리고 %3° %4 위치해 있습니다.")
                                .arg(QString::number(std::abs(pitch), 'g', 1), pitch > 0 ? "위로" : "아래로",
                                     QString::number(std::abs(yaw), 'g', 1), yaw > 0 ? "오른쪽으로" : "왼쪽으로");
        }
      } catch (kj::Exception) {
        qInfo() << "캘리브레이션 파라미터 유효하지 않음";
      }
    }
    resetCalibBtn->setDescription(desc);
  });
  offroad_btns.append(resetCalibBtn);

  offroad_btns.append(new ButtonControl("트레이닝가이드 보기", "다시보기",
                                        "오픈파일럿에 대한 규칙, 기능, 제한내용 등을 확인하세요.", [=]() {
    if (ConfirmationDialog::confirm("트레이닝 가이드를 다시 확인하시겠습니까?", this)) {
      Params().remove("CompletedTrainingVersion");
      emit reviewTrainingGuide();
    }
  }, "", this));

  QString brand = params.getBool("Passive") ? "대시캠" : "오픈파일럿";
  offroad_btns.append(new ButtonControl(brand + " 제거", "제거", "", [=]() {
    if (ConfirmationDialog::confirm("제거하시겠습니까?", this)) {
      Params().putBool("DoUninstall", true);
    }
  }, "", this));

  for(auto &btn : offroad_btns){
    device_layout->addWidget(horizontal_line());
    QObject::connect(parent, SIGNAL(offroadTransition(bool)), btn, SLOT(setEnabled(bool)));
    device_layout->addWidget(btn);
  }

  device_layout->addWidget(horizontal_line());

  // cal reset and param init buttons
  QHBoxLayout *cal_param_init_layout = new QHBoxLayout();
  cal_param_init_layout->setSpacing(50);

  QPushButton *calinit_btn = new QPushButton("캘리브레이션 리셋");
  cal_param_init_layout->addWidget(calinit_btn);
  QObject::connect(calinit_btn, &QPushButton::released, [=]() {
    if (ConfirmationDialog::confirm("캘리브레이션을 초기화할까요? 자동 재부팅됩니다.", this)) {
      Params().remove("CalibrationParams");
      Params().remove("LiveParameters");
      QTimer::singleShot(1000, []() {
        Hardware::reboot();
      });
    }
  });

  QPushButton *paraminit_btn = new QPushButton("파라미터 초기화");
  cal_param_init_layout->addWidget(paraminit_btn);
  QObject::connect(paraminit_btn, &QPushButton::released, [=]() {
    if (ConfirmationDialog::confirm("파라미터를 초기상태로 되돌립니다. 진행하시겠습니까?", this)) {
      QProcess::execute("/data/openpilot/init_param.sh");
    }
  });

  // preset1 buttons
  QHBoxLayout *presetone_layout = new QHBoxLayout();
  presetone_layout->setSpacing(50);

  QPushButton *presetoneload_btn = new QPushButton("프리셋1 불러오기");
  presetone_layout->addWidget(presetoneload_btn);
  QObject::connect(presetoneload_btn, &QPushButton::released, [=]() {
    if (ConfirmationDialog::confirm("프리셋1을 불러올까요?", this)) {
      QProcess::execute("/data/openpilot/load_preset1.sh");
    }
  });

  QPushButton *presetonesave_btn = new QPushButton("프리셋1 저장하기");
  presetone_layout->addWidget(presetonesave_btn);
  QObject::connect(presetonesave_btn, &QPushButton::released, [=]() {
    if (ConfirmationDialog::confirm("프리셋1을 저장할까요?", this)) {
      QProcess::execute("/data/openpilot/save_preset1.sh");
    }
  });

  // preset2 buttons
  QHBoxLayout *presettwo_layout = new QHBoxLayout();
  presettwo_layout->setSpacing(50);

  QPushButton *presettwoload_btn = new QPushButton("프리셋2 불러오기");
  presettwo_layout->addWidget(presettwoload_btn);
  QObject::connect(presettwoload_btn, &QPushButton::released, [=]() {
    if (ConfirmationDialog::confirm("프리셋2을 불러올까요?", this)) {
      QProcess::execute("/data/openpilot/load_preset2.sh");
    }
  });

  QPushButton *presettwosave_btn = new QPushButton("프리셋2 저장하기");
  presettwo_layout->addWidget(presettwosave_btn);
  QObject::connect(presettwosave_btn, &QPushButton::released, [=]() {
    if (ConfirmationDialog::confirm("프리셋2을 저장할까요?", this)) {
      QProcess::execute("/data/openpilot/save_preset2.sh");
    }
  });

  // power buttons
  QHBoxLayout *power_layout = new QHBoxLayout();
  power_layout->setSpacing(50);

  QPushButton *reboot_btn = new QPushButton("재시작");
  power_layout->addWidget(reboot_btn);
  QObject::connect(reboot_btn, &QPushButton::released, [=]() {
    if (ConfirmationDialog::confirm("재시작하시겠습니까?", this)) {
      Hardware::reboot();
    }
  });

  QPushButton *poweroff_btn = new QPushButton("전원끄기");
  poweroff_btn->setStyleSheet("background-color: #E22C2C;");
  power_layout->addWidget(poweroff_btn);
  QObject::connect(poweroff_btn, &QPushButton::released, [=]() {
    if (ConfirmationDialog::confirm("전원을 끄시겠습니까?", this)) {
      Hardware::poweroff();
    }
  });

  device_layout->addLayout(cal_param_init_layout);

  device_layout->addWidget(horizontal_line());

  device_layout->addLayout(presetone_layout);
  device_layout->addLayout(presettwo_layout);

  device_layout->addWidget(horizontal_line());

  device_layout->addLayout(power_layout);

  setLayout(device_layout);
  setStyleSheet(R"(
    QPushButton {
      padding: 20;
      height: 120px;
      border-radius: 15px;
      background-color: #393939;
    }
  )");
}

SoftwarePanel::SoftwarePanel(QWidget* parent) : QFrame(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  setLayout(main_layout);
  setStyleSheet(R"(QLabel {font-size: 50px;})");

  fs_watch = new QFileSystemWatcher(this);
  QObject::connect(fs_watch, &QFileSystemWatcher::fileChanged, [=](const QString path) {
    int update_failed_count = Params().get<int>("UpdateFailedCount").value_or(0);
    if (path.contains("UpdateFailedCount") && update_failed_count > 0) {
      lastUpdateTimeLbl->setText("failed to fetch update");
      updateButton->setText("확인");
      updateButton->setEnabled(true);
    } else if (path.contains("LastUpdateTime")) {
      updateLabels();
    }
  });
}

void SoftwarePanel::showEvent(QShowEvent *event) {
  updateLabels();
}

void SoftwarePanel::updateLabels() {
  Params params = Params();
  std::string brand = params.getBool("Passive") ? "대시캠" : "오픈파일럿";
  QList<QPair<QString, std::string>> dev_params = {
    //{"Git Branch", params.get("GitBranch")},
    //{"Git Commit", params.get("GitCommit").substr(0, 10)},
    {"Panda Firmware", params.get("PandaFirmwareHex")},
    {"OS Version", Hardware::get_os_version()},
  };

  QString version = QString::fromStdString(brand + " v" + params.get("Version").substr(0, 14)).trimmed();
  QString remote = QString::fromStdString(params.get("GitRemote").substr(19)).trimmed();
  QString branch = QString::fromStdString(params.get("GitBranch")).trimmed();
  QString lastUpdateTime = "";

  std::string last_update_param = params.get("LastUpdateTime");
  if (!last_update_param.empty()){
    QDateTime lastUpdateDate = QDateTime::fromString(QString::fromStdString(last_update_param + "Z"), Qt::ISODate);
    lastUpdateTime = timeAgo(lastUpdateDate);
  }

  if (labels.size() < dev_params.size()) {
    versionLbl = new LabelControl("Version", version, QString::fromStdString(params.get("ReleaseNotes")).trimmed());
    layout()->addWidget(versionLbl);
    layout()->addWidget(horizontal_line());
    remoteLbl = new LabelControl("Git Remote", remote, "");
    layout()->addWidget(remoteLbl);
    layout()->addWidget(horizontal_line());
    branchLbl = new LabelControl("Git Branch", branch, "");
    layout()->addWidget(branchLbl);
    layout()->addWidget(horizontal_line());

    lastUpdateTimeLbl = new LabelControl("Last Update Check", lastUpdateTime, "");
    layout()->addWidget(lastUpdateTimeLbl);
    layout()->addWidget(horizontal_line());

    updateButton = new ButtonControl("Check for Update", "확인", "", [=]() {
      Params params = Params();
      if (params.getBool("IsOffroad")) {
        fs_watch->addPath(QString::fromStdString(params.getParamsPath()) + "/d/LastUpdateTime");
        fs_watch->addPath(QString::fromStdString(params.getParamsPath()) + "/d/UpdateFailedCount");
        updateButton->setText("확인중");
        updateButton->setEnabled(false);
      }
      std::system("pkill -1 -f selfdrive.updated");
    }, "", this);
    layout()->addWidget(updateButton);
    layout()->addWidget(horizontal_line());

    layout()->addWidget(new GitHash());
    const char* gitpull = "/data/openpilot/gitpull.sh ''";
    layout()->addWidget(new ButtonControl("Git Pull", "실행", "리모트 Git에서 변경사항이 있으면 로컬에 반영 후 자동 재부팅 됩니다. 변경사항이 없으면 재부팅하지 않습니다. 로컬 파일이 변경된경우 리모트Git 내역을 반영 못할수도 있습니다. 참고바랍니다.",
                                        [=]() { 
                                          if (ConfirmationDialog::confirm("Git에서 변경사항 적용 후 자동 재부팅 됩니다. 없으면 재부팅하지 않습니다. 진행하시겠습니까?")){
                                            std::system(gitpull);
                                          }
                                        }));

    layout()->addWidget(horizontal_line());

    const char* git_reset = "/data/openpilot/git_reset.sh ''";
    layout()->addWidget(new ButtonControl("Git Reset", "실행", "로컬변경사항을 강제 초기화 후 리모트 최신 커밋내역을 적용합니다. 로컬 변경사항이 사라지니 주의 바랍니다.",
                                        [=]() { 
                                          if (ConfirmationDialog::confirm("로컬변경사항을 강제 초기화 후 리모트Git의 최신 커밋내역을 적용합니다. 진행하시겠습니까?")){
                                            std::system(git_reset);
                                          }
                                        }));


    layout()->addWidget(horizontal_line());

    const char* gitpull_cancel = "/data/openpilot/gitpull_cancel.sh ''";
    layout()->addWidget(new ButtonControl("Git Pull 취소", "실행", "Git Pull을 취소하고 이전상태로 되돌립니다. 커밋내역이 여러개인경우 최신커밋 바로 이전상태로 되돌립니다.",
                                        [=]() { 
                                          if (ConfirmationDialog::confirm("GitPull 이전 상태로 되돌립니다. 진행하시겠습니까?")){
                                            std::system(gitpull_cancel);
                                          }
                                        }));

    layout()->addWidget(horizontal_line());

    const char* panda_flashing = "/data/openpilot/panda_flashing.sh ''";
    layout()->addWidget(new ButtonControl("판다 플래싱", "실행", "판다플래싱이 진행되면 판다의 녹색LED가 빠르게 깜빡이며 완료되면 자동 재부팅 됩니다. 절대로 장치의 전원을 끄거나 임의로 분리하지 마시기 바랍니다.",
                                        [=]() {
                                          if (ConfirmationDialog::confirm("판다플래싱을 진행하시겠습니까?")) {
                                            std::system(panda_flashing);
                                          }
                                        }));
    layout()->addWidget(horizontal_line());
  } else {
    versionLbl->setText(version);
    remoteLbl->setText(remote);
    branchLbl->setText(branch);
    lastUpdateTimeLbl->setText(lastUpdateTime);
    updateButton->setText("확인");
    updateButton->setEnabled(true);
  }

  for (int i = 0; i < dev_params.size(); i++) {
    const auto &[name, value] = dev_params[i];
    QString val = QString::fromStdString(value).trimmed();
    if (labels.size() > i) {
      labels[i]->setText(val);
    } else {
      labels.push_back(new LabelControl(name, val));
      layout()->addWidget(labels[i]);
      if (i < (dev_params.size() - 1)) {
        layout()->addWidget(horizontal_line());
      }
    }
  }
}

QWidget * network_panel(QWidget * parent) {
#ifdef QCOM
  QVBoxLayout *layout = new QVBoxLayout;
  layout->setSpacing(30);

  layout->addWidget(new OpenpilotView());
  layout->addWidget(horizontal_line());
  // wifi + tethering buttons
  layout->addWidget(new ButtonControl("WiFi 설정", "열기", "",
                                      [=]() { HardwareEon::launch_wifi(); }));
  layout->addWidget(horizontal_line());

  layout->addWidget(new ButtonControl("테더링 설정", "열기", "",
                                      [=]() { HardwareEon::launch_tethering(); }));
  layout->addWidget(horizontal_line());

  layout->addWidget(new HotspotOnBootToggle());

  layout->addWidget(horizontal_line());

  // SSH key management
  layout->addWidget(new SshToggle());
  layout->addWidget(horizontal_line());
  layout->addWidget(new SshControl());
  layout->addWidget(horizontal_line());
  layout->addWidget(new SshLegacyToggle());

  layout->addStretch(1);

  QWidget *w = new QWidget;
  w->setLayout(layout);
#else
  Networking *w = new Networking(parent);
#endif
  return w;
}

QWidget * user_panel(QWidget * parent) {
  QVBoxLayout *layout = new QVBoxLayout;

  // OPKR
  layout->addWidget(new LabelControl("UI설정", ""));
  layout->addWidget(new AutoShutdown());
  layout->addWidget(new ForceShutdown());
  //layout->addWidget(new AutoScreenDimmingToggle());
  layout->addWidget(new AutoScreenOff());
  layout->addWidget(new VolumeControl());
  layout->addWidget(new BrightnessControl());
  layout->addWidget(new GetoffAlertToggle());
  layout->addWidget(new BatteryChargingControlToggle());
  layout->addWidget(new ChargingMin());
  layout->addWidget(new ChargingMax());
  layout->addWidget(new FanSpeedGain());
  layout->addWidget(new DrivingRecordToggle());
  layout->addWidget(new RecordCount());
  layout->addWidget(new RecordQuality());
  const char* record_del = "rm -f /storage/emulated/0/videos/*";
  layout->addWidget(new ButtonControl("녹화파일 전부 삭제", "실행", "저장된 녹화파일을 모두 삭제합니다.",
                                      [=]() { 
                                        if (ConfirmationDialog::confirm("저장된 녹화파일을 모두 삭제합니다. 진행하시겠습니까?")){
                                          std::system(record_del);
                                        }
                                      }));
  const char* realdata_del = "rm -rf /storage/emulated/0/realdata/*";
  layout->addWidget(new ButtonControl("주행로그 전부 삭제", "실행", "저장된 주행로그를 모두 삭제합니다.",
                                      [=]() { 
                                        if (ConfirmationDialog::confirm("저장된 주행로그를 모두 삭제합니다. 진행하시겠습니까?")){
                                          std::system(realdata_del);
                                        }
                                      }));
  layout->addWidget(new MonitoringMode());
  layout->addWidget(new MonitorEyesThreshold());
  layout->addWidget(new NormalEyesThreshold());
  layout->addWidget(new BlinkThreshold());
  layout->addWidget(new RunNaviOnBootToggle());

  layout->addWidget(horizontal_line());
  layout->addWidget(new LabelControl("주행설정", ""));
  layout->addWidget(new AutoResumeToggle());
  layout->addWidget(new VariableCruiseToggle());
  layout->addWidget(new VariableCruiseProfile());
  layout->addWidget(new CruisemodeSelInit());
  layout->addWidget(new LaneChangeSpeed());
  layout->addWidget(new LaneChangeDelay());
  layout->addWidget(new LeftCurvOffset());
  layout->addWidget(new RightCurvOffset());
  layout->addWidget(new BlindSpotDetectToggle());
  layout->addWidget(new MaxAngleLimit());
  layout->addWidget(new SteerAngleCorrection());
  layout->addWidget(new TurnSteeringDisableToggle());
  layout->addWidget(new CruiseOverMaxSpeedToggle());
  layout->addWidget(new SpeedLimitOffset());
  layout->addWidget(new CruiseGapAdjustToggle());
  layout->addWidget(new AutoEnabledToggle());
  layout->addWidget(new CruiseAutoResToggle());
  layout->addWidget(new RESChoice());
  layout->addWidget(new SteerWindDownToggle());
  layout->addWidget(new MadModeEnabledToggle());

  layout->addWidget(horizontal_line());
  layout->addWidget(new LabelControl("개발자", ""));
  layout->addWidget(new DebugUiOneToggle());
  layout->addWidget(new DebugUiTwoToggle());
  layout->addWidget(new LongLogToggle());
  layout->addWidget(new PrebuiltToggle());
  layout->addWidget(new FPTwoToggle());
  layout->addWidget(new LDWSToggle());
  layout->addWidget(new GearDToggle());
  layout->addWidget(new ComIssueToggle());
  layout->addWidget(new WhitePandaSupportToggle());
  layout->addWidget(new SteerWarningFixToggle());
  const char* cal_ok = "cp -f /data/openpilot/selfdrive/assets/addon/param/CalibrationParams /data/params/d/";
  layout->addWidget(new ButtonControl("캘리브레이션 강제 활성화", "실행", "실주행으로 캘리브레이션을 설정하지 않고 이온을 초기화 한경우 인게이지 확인용도로 캘리브레이션을 강제 설정합니다.",
                                      [=]() { 
                                        if (ConfirmationDialog::confirm("캘리브레이션을 강제로 설정합니다. 인게이지 확인용이니 실 주행시에는 초기화 하시기 바랍니다.")){
                                          std::system(cal_ok);
                                        }
                                      }));
  layout->addWidget(horizontal_line());
  layout->addWidget(new CarRecognition());
  //layout->addWidget(new CarForceSet());
  //QString car_model = QString::fromStdString(Params().get("CarModel", false));
  //layout->addWidget(new LabelControl("현재차량모델", ""));
  //layout->addWidget(new LabelControl(car_model, ""));

  layout->addWidget(horizontal_line());
  layout->addWidget(new LabelControl("판다 값", "주의要"));
  layout->addWidget(new MaxSteer());
  layout->addWidget(new MaxRTDelta());
  layout->addWidget(new MaxRateUp());
  layout->addWidget(new MaxRateDown());
  const char* p_edit_go = "/data/openpilot/p_edit.sh ''";
  layout->addWidget(new ButtonControl("판다값 변경 적용", "실행", "판다 값을 변경합니다. 기본값: MAX_STEER = 384, RT_DELTA = 112, MAX_RATE_UP = 3, MAX_RATE_DOWN = 7",
                                      [=]() { 
                                        if (ConfirmationDialog::confirm("변경된 판다값을 적용합니다. 진행하시겠습니까? 자동 재부팅됩니다.")){
                                          std::system(p_edit_go);
                                        }
                                      }));

  layout->addStretch(1);

  QWidget *w = new QWidget;
  w->setLayout(layout);

  return w;
}

QWidget * tuning_panel(QWidget * parent) {
  QVBoxLayout *layout = new QVBoxLayout;

  // OPKR
  layout->addWidget(new LabelControl("튜닝메뉴", ""));
  layout->addWidget(new CameraOffset());
  layout->addWidget(new LiveSteerRatioToggle());
  layout->addWidget(new SRBaseControl());
  layout->addWidget(new SRMaxControl());
  layout->addWidget(new SteerActuatorDelay());
  layout->addWidget(new SteerRateCost());
  layout->addWidget(new SteerLimitTimer());
  layout->addWidget(new TireStiffnessFactor());
  layout->addWidget(new SteerMaxBase());
  layout->addWidget(new SteerMaxMax());
  layout->addWidget(new SteerMaxv());
  layout->addWidget(new VariableSteerMaxToggle());
  layout->addWidget(new SteerDeltaUpBase());
  layout->addWidget(new SteerDeltaUpMax());
  layout->addWidget(new SteerDeltaDownBase());
  layout->addWidget(new SteerDeltaDownMax());
  layout->addWidget(new VariableSteerDeltaToggle());
  layout->addWidget(new SteerThreshold());

  layout->addWidget(horizontal_line());

  layout->addWidget(new LabelControl("제어메뉴", ""));
  layout->addWidget(new LateralControl());
  layout->addWidget(new LiveTuneToggle());
  QString lat_control = QString::fromStdString(Params().get("LateralControlMethod", false));
  if (lat_control == "0") {
    layout->addWidget(new PidKp());
    layout->addWidget(new PidKi());
    layout->addWidget(new PidKd());
    layout->addWidget(new PidKf());
    layout->addWidget(new IgnoreZone());
    layout->addWidget(new ShaneFeedForward());
  } else if (lat_control == "1") {
    layout->addWidget(new InnerLoopGain());
    layout->addWidget(new OuterLoopGain());
    layout->addWidget(new TimeConstant());
    layout->addWidget(new ActuatorEffectiveness());
  } else if (lat_control == "2") {
    layout->addWidget(new Scale());
    layout->addWidget(new LqrKi());
    layout->addWidget(new DcGain());
  }

  layout->addStretch(1);

  QWidget *w = new QWidget;
  w->setLayout(layout);

  return w;
}

void SettingsWindow::showEvent(QShowEvent *event) {
  if (layout()) {
    panel_widget->setCurrentIndex(0);
    nav_btns->buttons()[0]->setChecked(true);
    return;
  }

  // setup two main layouts
  QVBoxLayout *sidebar_layout = new QVBoxLayout();
  sidebar_layout->setMargin(0);
  panel_widget = new QStackedWidget();
  panel_widget->setStyleSheet(R"(
    border-radius: 30px;
    background-color: #292929;
  )");

  // close button
  QPushButton *close_btn = new QPushButton("닫기");
  close_btn->setStyleSheet(R"(
    font-size: 60px;
    font-weight: bold;
    border 1px grey solid;
    border-radius: 100px;
    background-color: #292929;
  )");
  close_btn->setFixedSize(200, 200);
  sidebar_layout->addSpacing(45);
  sidebar_layout->addWidget(close_btn, 0, Qt::AlignCenter);
  QObject::connect(close_btn, &QPushButton::released, this, &SettingsWindow::closeSettings);

  // setup panels
  DevicePanel *device = new DevicePanel(this);
  QObject::connect(device, &DevicePanel::reviewTrainingGuide, this, &SettingsWindow::reviewTrainingGuide);
  QObject::connect(device, &DevicePanel::showDriverView, this, &SettingsWindow::showDriverView);

  QPair<QString, QWidget *> panels[] = {
    {"장치", device},
    {"네트워크", network_panel(this)},
    {"토글메뉴", new TogglesPanel(this)},
    {"소프트웨어", new SoftwarePanel()},
    {"사용자설정", user_panel(this)},
    {"튜닝", tuning_panel(this)},
  };

  sidebar_layout->addSpacing(45);
  nav_btns = new QButtonGroup();
  for (auto &[name, panel] : panels) {
    QPushButton *btn = new QPushButton(name);
    btn->setCheckable(true);
    btn->setChecked(nav_btns->buttons().size() == 0);
    btn->setStyleSheet(R"(
      QPushButton {
        color: grey;
        border: none;
        background: none;
        font-size: 65px;
        font-weight: 500;
        padding-top: 18px;
        padding-bottom: 18px;
      }
      QPushButton:checked {
        color: white;
      }
    )");

    nav_btns->addButton(btn);
    sidebar_layout->addWidget(btn, 0, Qt::AlignRight);

    panel->setContentsMargins(50, 25, 50, 25);

    ScrollView *panel_frame = new ScrollView(panel, this);
    panel_widget->addWidget(panel_frame);

    QObject::connect(btn, &QPushButton::released, [=, w = panel_frame]() {
      panel_widget->setCurrentWidget(w);
    });
  }
  sidebar_layout->setContentsMargins(50, 50, 100, 50);

  // main settings layout, sidebar + main panel
  QHBoxLayout *settings_layout = new QHBoxLayout();

  sidebar_widget = new QWidget;
  sidebar_widget->setLayout(sidebar_layout);
  sidebar_widget->setFixedWidth(500);
  settings_layout->addWidget(sidebar_widget);
  settings_layout->addWidget(panel_widget);

  setLayout(settings_layout);
  setStyleSheet(R"(
    * {
      color: white;
      font-size: 50px;
    }
    SettingsWindow {
      background-color: black;
    }
  )");
}

void SettingsWindow::hideEvent(QHideEvent *event){
#ifdef QCOM
  HardwareEon::close_activities();
#endif

  // TODO: this should be handled by the Dialog classes
  QList<QWidget*> children = findChildren<QWidget *>();
  for(auto &w : children){
    if(w->metaObject()->superClass()->className() == QString("QDialog")){
      w->close();
    }
  }
}
