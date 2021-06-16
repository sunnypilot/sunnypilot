#pragma once

#include <QPushButton>

#include "selfdrive/hardware/hw.h"
#include "selfdrive/ui/qt/widgets/controls.h"

// SSH enable toggle
class SshToggle : public ToggleControl {
  Q_OBJECT

public:
  SshToggle() : ToggleControl("SSH 접속 사용", "", "", Hardware::get_ssh_enabled()) {
    QObject::connect(this, &SshToggle::toggleFlipped, [=](bool state) {
      Hardware::set_ssh_enabled(state);
    });
  }
};

// SSH key management widget
class SshControl : public AbstractControl {
  Q_OBJECT

public:
  SshControl();

private:
  Params params;

  QPushButton btn;
  QLabel username_label;

  void refresh();
  void getUserKeys(const QString &username);
};


class SshLegacyToggle : public ToggleControl {
  Q_OBJECT

public:
  SshLegacyToggle() : ToggleControl("기존 공개KEY 사용", "SSH 접속시 기존 공개KEY(0.8.2이하)를 사용합니다.", "", Params().getBool("OpkrSSHLegacy")) {
    QObject::connect(this, &SshLegacyToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrSSHLegacy", &value, 1);
    });
  }
};

class GetoffAlertToggle : public ToggleControl {
  Q_OBJECT

public:
  GetoffAlertToggle() : ToggleControl("운행종료시 이온탈착 알림 사용", "운행종료 후 이온을 분리하라는 알림을 보냅니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrEnableGetoffAlert")) {
    QObject::connect(this, &GetoffAlertToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrEnableGetoffAlert", &value, 1);
    });
  }
};

class AutoResumeToggle : public ToggleControl {
  Q_OBJECT

public:
  AutoResumeToggle() : ToggleControl("자동출발 기능 사용", "SCC 사용중 정차시 자동출발 기능을 사용합니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrAutoResume")) {
    QObject::connect(this, &AutoResumeToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrAutoResume", &value, 1);
    });
  }
};

class VariableCruiseToggle : public ToggleControl {
  Q_OBJECT

public:
  VariableCruiseToggle() : ToggleControl("가변 크루즈 사용", "SCC 사용중 크루즈 버튼을 이용하여 가감속을 보조합니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrVariableCruise")) {
    QObject::connect(this, &VariableCruiseToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrVariableCruise", &value, 1);
    });
  }
};

class CruiseGapAdjustToggle : public ToggleControl {
  Q_OBJECT

public:
  CruiseGapAdjustToggle() : ToggleControl("정차시 크루즈 갭 자동변경", "정차시 빠른 출발을 위해 크루즈갭을 1칸으로 변경하며, 출발후 일정조건에 따라 다시 원래의 크루즈갭으로 돌아갑니다.", "../assets/offroad/icon_shell.png", Params().getBool("CruiseGapAdjust")) {
    QObject::connect(this, &CruiseGapAdjustToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("CruiseGapAdjust", &value, 1);
    });
  }
};

class AutoEnabledToggle : public ToggleControl {
  Q_OBJECT

public:
  AutoEnabledToggle() : ToggleControl("자동 인게이지 활성", "디스인게이지 상태에서 크루즈 버튼상태가 대기상태(CRUISE표시만 나오고 속도 지정이 안된상태)일 경우 자동 인게이지를 활성화 합니다.", "../assets/offroad/icon_shell.png", Params().getBool("AutoEnable")) {
    QObject::connect(this, &AutoEnabledToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("AutoEnable", &value, 1);
    });
  }
};

class CruiseAutoResToggle : public ToggleControl {
  Q_OBJECT

public:
  CruiseAutoResToggle() : ToggleControl("자동 RES 사용", "크루즈 사용중 브레이크를 밟아 대기모드 상태로 변한경우(CANCEL은 해당없음) 브레이크 페달 해제시 다시 이전 속도로 세팅합니다. 크루즈 속도가 세팅되어 있고 차량속도가 30km/h 이상 혹은 앞차가 인식될 경우 작동합니다.", "../assets/offroad/icon_shell.png", Params().getBool("CruiseAutoRes")) {
    QObject::connect(this, &CruiseAutoResToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("CruiseAutoRes", &value, 1);
    });
  }
};

class BatteryChargingControlToggle : public ToggleControl {
  Q_OBJECT

public:
  BatteryChargingControlToggle() : ToggleControl("배터리 충전 제어기능 사용", "배터리 충전제어 기능을 사용합니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrBatteryChargingControl")) {
    QObject::connect(this, &BatteryChargingControlToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrBatteryChargingControl", &value, 1);
    });
  }
};

class BlindSpotDetectToggle : public ToggleControl {
  Q_OBJECT

public:
  BlindSpotDetectToggle() : ToggleControl("후측방 감지 아이콘 표시", "후측방에 차가 감지되면 화면에 아이콘을 띄웁니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrBlindSpotDetect")) {
    QObject::connect(this, &BlindSpotDetectToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrBlindSpotDetect", &value, 1);
    });
  }
};

class MadModeEnabledToggle : public ToggleControl {
  Q_OBJECT

public:
  MadModeEnabledToggle() : ToggleControl("MainSW 오픈파일럿 ON/OFF", "크루즈 MainSW를 이용하여 오파를 활성화 합니다.", "../assets/offroad/icon_shell.png", Params().getBool("MadModeEnabled")) {
    QObject::connect(this, &MadModeEnabledToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("MadModeEnabled", &value, 1);
    });
  }
};

class WhitePandaSupportToggle : public ToggleControl {
  Q_OBJECT

public:
  WhitePandaSupportToggle() : ToggleControl("화이트판다 지원", "화이트판다 사용시 기능을 켜십시오", "../assets/offroad/icon_shell.png", Params().getBool("WhitePandaSupport")) {
    QObject::connect(this, &WhitePandaSupportToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("WhitePandaSupport", &value, 1);
    });
  }
};

class SteerWarningFixToggle : public ToggleControl {
  Q_OBJECT

public:
  SteerWarningFixToggle() : ToggleControl("조향경고 해제", "차량에서 조향에러가 발생하여 오파 실행이 불가능할 때 기능을 켜십시오(일부 차량 Only). 주행 중 정상적인 에러환경에서 발생시에는 기능을 켜지 마십시오.", "../assets/offroad/icon_shell.png", Params().getBool("SteerWarningFix")) {
    QObject::connect(this, &SteerWarningFixToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("SteerWarningFix", &value, 1);
    });
  }
};

class SteerWindDownToggle : public ToggleControl {
  Q_OBJECT

public:
  SteerWindDownToggle() : ToggleControl("Steer Wind Down", "Steer Warning 시 토크를 서서히 다운시킵니다. 일부 차량의 경우 조향각 제한등이 나타날 수 있으니 에러상관없이 최대조향각을 쓰려면 기능을 끄십시오.", "../assets/offroad/icon_shell.png", Params().getBool("SteerWindDown")) {
    QObject::connect(this, &SteerWindDownToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("SteerWindDown", &value, 1);
    });
  }
};

class AutoScreenDimmingToggle : public ToggleControl {
  Q_OBJECT

public:
  AutoScreenDimmingToggle() : ToggleControl("주행화면 Dimming 제어", "주행시 최소한의 밝기를 유지하여 배터리 소모량 및 발열을 줄이며, 이벤트 발생 시 밝기를 높여 일시적으로 가시성을 확보합니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrAutoScreenDimming")) {
    QObject::connect(this, &AutoScreenDimmingToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrAutoScreenDimming", &value, 1);
    });
  }
};

class LiveSteerRatioToggle : public ToggleControl {
  Q_OBJECT

public:
  LiveSteerRatioToggle() : ToggleControl("Live SteerRatio 사용", "가변/고정 SR 대신 Live SteerRatio를 사용합니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrLiveSteerRatio")) {
    QObject::connect(this, &LiveSteerRatioToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrLiveSteerRatio", &value, 1);
    });
  }
};

class VariableSteerMaxToggle : public ToggleControl {
  Q_OBJECT

public:
  VariableSteerMaxToggle() : ToggleControl("가변 SteerMax 사용", "곡률에 따른 가변 SteerMax을 사용합니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrVariableSteerMax")) {
    QObject::connect(this, &VariableSteerMaxToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrVariableSteerMax", &value, 1);
    });
  }
};

class VariableSteerDeltaToggle : public ToggleControl {
  Q_OBJECT

public:
  VariableSteerDeltaToggle() : ToggleControl("가변 SteerDelta 사용", "곡률에 따른 가변 SteerDelta를 사용합니다.( DeltaUp ~ 5까지 변화, DeltaDown ~ 10까지 변화", "../assets/offroad/icon_shell.png", Params().getBool("OpkrVariableSteerDelta")) {
    QObject::connect(this, &VariableSteerDeltaToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrVariableSteerDelta", &value, 1);
    });
  }
};

class LiveTuneToggle : public ToggleControl {
  Q_OBJECT

public:
  LiveTuneToggle() : ToggleControl("라이브 튜너 사용", "이 옵션을 켜면 제어값이 실시간으로 적용됩니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrLiveTune")) {
    QObject::connect(this, &LiveTuneToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrLiveTune", &value, 1);
    });
  }
};

class ShaneFeedForward : public ToggleControl {
  Q_OBJECT

public:
  ShaneFeedForward() : ToggleControl("Shane FeedForward 사용", "Shane의 FeedForward를 사용합니다. 조향각에 따라 직선주로에서는 토크를 낮추고, 곡선주로에서는 동적으로 조정합니다.", "../assets/offroad/icon_shell.png", Params().getBool("ShaneFeedForward")) {
    QObject::connect(this, &ShaneFeedForward::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("ShaneFeedForward", &value, 1);
    });
  }
};

class DrivingRecordToggle : public ToggleControl {
  Q_OBJECT

public:
  DrivingRecordToggle() : ToggleControl("자동 화면녹화 기능 사용", "운전 중 화면 녹화/중지를 자동으로 수행합니다. 출발 후 녹화가 시작되며 차량이 정지하면 녹화가 종료됩니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrDrivingRecord")) {
    QObject::connect(this, &DrivingRecordToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrDrivingRecord", &value, 1);
    });
  }
};

class TurnSteeringDisableToggle : public ToggleControl {
  Q_OBJECT

public:
  TurnSteeringDisableToggle() : ToggleControl("턴시그널 사용시 조향해제 사용", "차선변경속도 이하로 주행할 때 턴시그널을 사용시 자동조향을 일시해제 합니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrTurnSteeringDisable")) {
    QObject::connect(this, &TurnSteeringDisableToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrTurnSteeringDisable", &value, 1);
    });
  }
};

class HotspotOnBootToggle : public ToggleControl {
  Q_OBJECT

public:
  HotspotOnBootToggle() : ToggleControl("부팅시 핫스팟 자동실행", "부팅 후 핫스팟을 자동으로 실행합니다.", "", Params().getBool("OpkrHotspotOnBoot")) {
    QObject::connect(this, &HotspotOnBootToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrHotspotOnBoot", &value, 1);
    });
  }
};

class CruiseOverMaxSpeedToggle : public ToggleControl {
  Q_OBJECT

public:
  CruiseOverMaxSpeedToggle() : ToggleControl("설정속도를 초과속도에 동기화", "현재속도가 설정속도를 넘어설 경우 설정속도를 현재속도에 동기화합니다.", "../assets/offroad/icon_shell.png", Params().getBool("CruiseOverMaxSpeed")) {
    QObject::connect(this, &CruiseOverMaxSpeedToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("CruiseOverMaxSpeed", &value, 1);
    });
  }
};

class DebugUiOneToggle : public ToggleControl {
  Q_OBJECT

public:
  DebugUiOneToggle() : ToggleControl("DEBUG UI 1", "", "../assets/offroad/icon_shell.png", Params().getBool("DebugUi1")) {
    QObject::connect(this, &DebugUiOneToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("DebugUi1", &value, 1);
    });
  }
};

class DebugUiTwoToggle : public ToggleControl {
  Q_OBJECT

public:
  DebugUiTwoToggle() : ToggleControl("DEBUG UI 2", "", "../assets/offroad/icon_shell.png", Params().getBool("DebugUi2")) {
    QObject::connect(this, &DebugUiTwoToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("DebugUi2", &value, 1);
    });
  }
};

class LongLogToggle : public ToggleControl {
  Q_OBJECT

public:
  LongLogToggle() : ToggleControl("LONG LOG 표시", "화면에 가변크루즈 로그 대신 롱 튜닝 디버그용 로그를 표시합니다.", "../assets/offroad/icon_shell.png", Params().getBool("LongLogDisplay")) {
    QObject::connect(this, &LongLogToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("LongLogDisplay", &value, 1);
    });
  }
};

class PrebuiltToggle : public ToggleControl {
  Q_OBJECT

public:
  PrebuiltToggle() : ToggleControl("Prebuilt 파일 생성", "Prebuilt 파일을 생성하며 부팅속도를 단축시킵니다. UI수정을 한 경우 기능을 끄십시오.", "../assets/offroad/icon_shell.png", Params().getBool("PutPrebuiltOn")) {
    QObject::connect(this, &PrebuiltToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("PutPrebuiltOn", &value, 1);
    });
  }
};

class LDWSToggle : public ToggleControl {
  Q_OBJECT

public:
  LDWSToggle() : ToggleControl("LDWS 차량 설정", "", "../assets/offroad/icon_shell.png", Params().getBool("LdwsCarFix")) {
    QObject::connect(this, &LDWSToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("LdwsCarFix", &value, 1);
    });
  }
};

class FPTwoToggle : public ToggleControl {
  Q_OBJECT

public:
  FPTwoToggle() : ToggleControl("FingerPrint 2.0 설정", "핑거프린트2.0을 활성화 합니다. ECU인식으로 차량을 활성화 합니다.", "../assets/offroad/icon_shell.png", Params().getBool("FingerprintTwoSet")) {
    QObject::connect(this, &FPTwoToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("FingerprintTwoSet", &value, 1);
    });
  }
};

class GearDToggle : public ToggleControl {
  Q_OBJECT

public:
  GearDToggle() : ToggleControl("드라이브기어 강제인식", "기어인식문제로 인게이지가 되지 않을 때 사용합니다. 근본적으로 CABANA데이터를 분석해야 하지만, 임시적으로 해결합니다.", "../assets/offroad/icon_shell.png", Params().getBool("JustDoGearD")) {
    QObject::connect(this, &GearDToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("JustDoGearD", &value, 1);
    });
  }
};

class ComIssueToggle : public ToggleControl {
  Q_OBJECT

public:
  ComIssueToggle() : ToggleControl("프로세스간 통신오류 알람 끄기", "화이트판다 사용시 프로세스간 통신오류 알람을 끄기 위해 이옵션을 켜십시오.", "../assets/offroad/icon_shell.png", Params().getBool("ComIssueGone")) {
    QObject::connect(this, &ComIssueToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("ComIssueGone", &value, 1);
    });
  }
};

class RunNaviOnBootToggle : public ToggleControl {
  Q_OBJECT

public:
  RunNaviOnBootToggle() : ToggleControl("부팅 후 네비 자동 실행", "부팅후 네비게이션(티맵)을 자동 실행합니다.", "../assets/offroad/icon_shell.png", Params().getBool("OpkrRunNaviOnBoot")) {
    QObject::connect(this, &RunNaviOnBootToggle::toggleFlipped, [=](int state) {
      char value = state ? '1' : '0';
      Params().put("OpkrRunNaviOnBoot", &value, 1);
    });
  }
};

// 오픈파일럿 미리보기
class OpenpilotView : public AbstractControl {
  Q_OBJECT

public:
  OpenpilotView();

private:
  QPushButton btn;
  Params params;
  
  void refresh();
};

// 차량 강제등록
class CarRecognition : public AbstractControl {
  Q_OBJECT

public:
  CarRecognition();

private:
  QPushButton btn;
  QString carname;
  QLabel carname_label;
  Params params;
  
  void refresh(QString carname);
};

class CarForceSet : public AbstractControl {
  Q_OBJECT

public:
  CarForceSet();

private:
  QPushButton btnc;
  QString carname;
  //QLabel carname_label;
  Params params;
  
  void refreshc();
};


// UI 설정
class AutoShutdown : public AbstractControl {
  Q_OBJECT

public:
  AutoShutdown();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class ForceShutdown : public AbstractControl {
  Q_OBJECT

public:
  ForceShutdown();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class AutoScreenOff : public AbstractControl {
  Q_OBJECT

public:
  AutoScreenOff();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class VolumeControl : public AbstractControl {
  Q_OBJECT

public:
  VolumeControl();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class BrightnessControl : public AbstractControl {
  Q_OBJECT

public:
  BrightnessControl();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class ChargingMin : public AbstractControl {
  Q_OBJECT

public:
  ChargingMin();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};
class ChargingMax : public AbstractControl {
  Q_OBJECT

public:
  ChargingMax();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};


// 주행 설정
class CruisemodeSelInit : public AbstractControl {
  Q_OBJECT

public:
  CruisemodeSelInit();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class VariableCruiseProfile : public AbstractControl {
  Q_OBJECT

public:
  VariableCruiseProfile();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class LaneChangeSpeed : public AbstractControl {
  Q_OBJECT

public:
  LaneChangeSpeed();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class LaneChangeDelay : public AbstractControl {
  Q_OBJECT

public:
  LaneChangeDelay();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class LeftCurvOffset : public AbstractControl {
  Q_OBJECT

public:
  LeftCurvOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};
class RightCurvOffset : public AbstractControl {
  Q_OBJECT

public:
  RightCurvOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class MaxAngleLimit : public AbstractControl {
  Q_OBJECT

public:
  MaxAngleLimit();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SpeedLimitOffset : public AbstractControl {
  Q_OBJECT

public:
  SpeedLimitOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

// 튜닝 설정
class CameraOffset : public AbstractControl {
  Q_OBJECT

public:
  CameraOffset();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SRBaseControl : public AbstractControl {
  Q_OBJECT

public:
  SRBaseControl();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};
class SRMaxControl : public AbstractControl {
  Q_OBJECT

public:
  SRMaxControl();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerActuatorDelay : public AbstractControl {
  Q_OBJECT

public:
  SteerActuatorDelay();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerRateCost : public AbstractControl {
  Q_OBJECT

public:
  SteerRateCost();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerLimitTimer : public AbstractControl {
  Q_OBJECT

public:
  SteerLimitTimer();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class TireStiffnessFactor : public AbstractControl {
  Q_OBJECT

public:
  TireStiffnessFactor();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerMaxBase : public AbstractControl {
  Q_OBJECT

public:
  SteerMaxBase();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerMaxMax : public AbstractControl {
  Q_OBJECT

public:
  SteerMaxMax();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerMaxv : public AbstractControl {
  Q_OBJECT

public:
  SteerMaxv();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerDeltaUpBase : public AbstractControl {
  Q_OBJECT

public:
  SteerDeltaUpBase();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerDeltaUpMax : public AbstractControl {
  Q_OBJECT

public:
  SteerDeltaUpMax();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerDeltaDownBase : public AbstractControl {
  Q_OBJECT

public:
  SteerDeltaDownBase();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerDeltaDownMax : public AbstractControl {
  Q_OBJECT

public:
  SteerDeltaDownMax();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};


// 제어 설정
class LateralControl : public AbstractControl {
  Q_OBJECT

public:
  LateralControl();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class PidKp : public AbstractControl {
  Q_OBJECT

public:
  PidKp();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class PidKi : public AbstractControl {
  Q_OBJECT

public:
  PidKi();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class PidKd : public AbstractControl {
  Q_OBJECT

public:
  PidKd();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class PidKf : public AbstractControl {
  Q_OBJECT

public:
  PidKf();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class IgnoreZone : public AbstractControl {
  Q_OBJECT

public:
  IgnoreZone();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class OuterLoopGain : public AbstractControl {
  Q_OBJECT

public:
  OuterLoopGain();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class InnerLoopGain : public AbstractControl {
  Q_OBJECT

public:
  InnerLoopGain();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class TimeConstant : public AbstractControl {
  Q_OBJECT

public:
  TimeConstant();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class ActuatorEffectiveness : public AbstractControl {
  Q_OBJECT

public:
  ActuatorEffectiveness();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class Scale : public AbstractControl {
  Q_OBJECT

public:
  Scale();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class LqrKi : public AbstractControl {
  Q_OBJECT

public:
  LqrKi();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class DcGain : public AbstractControl {
  Q_OBJECT

public:
  DcGain();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerAngleCorrection : public AbstractControl {
  Q_OBJECT

public:
  SteerAngleCorrection();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class MaxSteer : public AbstractControl {
  Q_OBJECT

public:
  MaxSteer();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class MaxRTDelta : public AbstractControl {
  Q_OBJECT

public:
  MaxRTDelta();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class MaxRateUp : public AbstractControl {
  Q_OBJECT

public:
  MaxRateUp();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class MaxRateDown : public AbstractControl {
  Q_OBJECT

public:
  MaxRateDown();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class SteerThreshold : public AbstractControl {
  Q_OBJECT

public:
  SteerThreshold();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class RecordCount : public AbstractControl {
  Q_OBJECT

public:
  RecordCount();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class RecordQuality : public AbstractControl {
  Q_OBJECT

public:
  RecordQuality();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class GitHash : public AbstractControl {
  Q_OBJECT

public:
  GitHash();

private:
  QLabel local_hash;
  QLabel remote_hash;
  Params params;
};

class RESChoice : public AbstractControl {
  Q_OBJECT

public:
  RESChoice();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class MonitoringMode : public AbstractControl {
  Q_OBJECT

public:
  MonitoringMode();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class MonitorEyesThreshold : public AbstractControl {
  Q_OBJECT

public:
  MonitorEyesThreshold();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class NormalEyesThreshold : public AbstractControl {
  Q_OBJECT

public:
  NormalEyesThreshold();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class BlinkThreshold : public AbstractControl {
  Q_OBJECT

public:
  BlinkThreshold();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};

class FanSpeedGain : public AbstractControl {
  Q_OBJECT

public:
  FanSpeedGain();

private:
  QPushButton btnplus;
  QPushButton btnminus;
  QLabel label;
  Params params;
  
  void refresh();
};