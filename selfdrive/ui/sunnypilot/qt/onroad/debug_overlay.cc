#include "selfdrive/ui/sunnypilot/qt/onroad/debug_overlay.h"
#include "selfdrive/ui/qt/util.h"  // for InterFont
#include <QPalette>
#include <QTimer>

DebugOverlay::DebugOverlay(QWidget *parent) : QWidget(parent) {
  setAttribute(Qt::WA_TransparentForMouseEvents);
  QVBoxLayout *layout = new QVBoxLayout(this);
  layout->setContentsMargins(20, 20, 20, 20);
  text_edit = new QTextEdit(this);
  text_edit->setReadOnly(true);
  text_edit->setFrameStyle(QFrame::NoFrame);
  text_edit->setStyleSheet("color: white; background: transparent; font-size: 60px;");
  layout->addWidget(text_edit);
  update_timer.start();
  periodic_timer = new QTimer(this);
  connect(periodic_timer, &QTimer::timeout, this, &DebugOverlay::onUpdateTimer);
  periodic_timer->start(500);
}

void DebugOverlay::updateState(const UIStateType &s) {
  bool show = params.getBool("ShowDABInspector");
  setVisible(show);
  latest_state = &s;
}

void DebugOverlay::onUpdateTimer() {
  if (!isVisible() || latest_state == nullptr) return;

  const auto lp_sp = (*latest_state->sm)["longitudinalPlanSP"].getLongitudinalPlanSP();
  double clear_road = lp_sp.getDabClearRoad();
  double boost = lp_sp.getDabAccelBoost();
  double weight = lp_sp.getDabWeight();
  double curviness = lp_sp.getDabCurviness();
  double lead_car_gate = lp_sp.getDabLeadCarGate();
  double tts_gate = lp_sp.getDabTtsGate();
  double curv_gate = lp_sp.getDabCurvGate();
  double phantom_brake_gate = lp_sp.getDabPhantomBrakeGate();
  double slow_radar_gate = lp_sp.getDabSlowRadarGate();
  double helper_accel = lp_sp.getDabHelperAccel();

  QString text;
  text += QString("ClearRoad: %1\n").arg(clear_road, 0, 'f', 2);
  text += QString("BoostA: %1  Weight: %2\n").arg(boost, 0, 'f', 2).arg(weight, 0, 'f', 2);
  text += QString("Curviness: %1\n").arg(curviness, 0, 'f', 2);
  text += QString("LeadCarGate: %1\n").arg(lead_car_gate, 0, 'f', 2);
  text += QString("TtsGate: %1\n").arg(tts_gate, 0, 'f', 2);
  text += QString("CurvGate: %1\n").arg(curv_gate, 0, 'f', 2);
  text += QString("PhantomBrakeGate: %1\n").arg(phantom_brake_gate, 0, 'f', 2);
  text += QString("SlowRadarGate: %1\n").arg(slow_radar_gate, 0, 'f', 2);
  text += QString("SlowHelperAccel: %1\n").arg(helper_accel, 0, 'f', 2);

  text_edit->setPlainText(text);
}
