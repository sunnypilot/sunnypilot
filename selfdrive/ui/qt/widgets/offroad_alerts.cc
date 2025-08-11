#include "selfdrive/ui/qt/widgets/offroad_alerts.h"

#include <algorithm>
#include <string>
#include <vector>
#include <utility>

#include <QHBoxLayout>
#include <QJsonDocument>
#include <QJsonObject>

#include "common/util.h"
#include "system/hardware/hw.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

AbstractAlert::AbstractAlert(bool hasRebootBtn, QWidget *parent) : QFrame(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setMargin(50);
  main_layout->setSpacing(30);

  QWidget *widget = new QWidget;
  scrollable_layout = new QVBoxLayout(widget);
  widget->setStyleSheet("background-color: transparent;");
  main_layout->addWidget(new ScrollView(widget));

  // bottom footer, dismiss + reboot buttons
  QHBoxLayout *footer_layout = new QHBoxLayout();
  main_layout->addLayout(footer_layout);

  QPushButton *dismiss_btn = new QPushButton(tr("Close"));
  dismiss_btn->setFixedSize(400, 125);
  footer_layout->addWidget(dismiss_btn, 0, Qt::AlignBottom | Qt::AlignLeft);
  QObject::connect(dismiss_btn, &QPushButton::clicked, this, &AbstractAlert::dismiss);

  snooze_btn = new QPushButton(tr("Snooze Update"));
  snooze_btn->setVisible(false);
  snooze_btn->setFixedSize(550, 125);
  footer_layout->addWidget(snooze_btn, 0, Qt::AlignBottom | Qt::AlignRight);
  QObject::connect(snooze_btn, &QPushButton::clicked, [=]() {
    params.putBool("SnoozeUpdate", true);
  });
  QObject::connect(snooze_btn, &QPushButton::clicked, this, &AbstractAlert::dismiss);
  snooze_btn->setStyleSheet(R"(color: white; background-color: #4F4F4F;)");

  if (hasRebootBtn) {
    QPushButton *rebootBtn = new QPushButton(tr("Reboot and Update"));
    rebootBtn->setFixedSize(600, 125);
    footer_layout->addWidget(rebootBtn, 0, Qt::AlignBottom | Qt::AlignRight);
    QObject::connect(rebootBtn, &QPushButton::clicked, [=]() { Hardware::reboot(); });
  }

  setStyleSheet(R"(
    * {
      font-size: 48px;
      color: white;
    }
    QFrame {
      border-radius: 30px;
      background-color: #393939;
    }
    QPushButton {
      color: black;
      font-weight: 500;
      border-radius: 30px;
      background-color: white;
    }
  )");
}

int OffroadAlert::refresh() {
  // build widgets for each offroad alert on first refresh
  if (alerts.empty()) {
    QString json = util::read_file("../selfdrived/alerts_offroad.json").c_str();
    QJsonObject obj = QJsonDocument::fromJson(json.toUtf8()).object();

    // descending sort labels by severity
    std::vector<std::pair<std::string, int>> sorted;
    for (auto it = obj.constBegin(); it != obj.constEnd(); ++it) {
      sorted.push_back({it.key().toStdString(), it.value()["severity"].toInt()});
    }
    std::sort(sorted.begin(), sorted.end(), [=](auto &l, auto &r) { return l.second > r.second; });

    for (auto &[key, severity] : sorted) {
      QLabel *l = new QLabel(this);
      alerts[key] = l;
      l->setMargin(60);
      l->setWordWrap(true);
      l->setStyleSheet(QString("background-color: %1").arg(severity ? "#E22C2C" : "#292929"));
      scrollable_layout->addWidget(l);
    }
    scrollable_layout->addStretch(1);
  }

  int alertCount = 0;
  for (const auto &[key, label] : alerts) {
    QString text;
    std::string bytes = params.get(key);
    if (bytes.size()) {
      auto doc_par = QJsonDocument::fromJson(bytes.c_str());
      text = tr(doc_par["text"].toString().toUtf8().data());
      auto extra = doc_par["extra"].toString();
      if (!extra.isEmpty()) {
        text = text.arg(extra);
      }
    }
    label->setText(text);
    label->setVisible(!text.isEmpty());
    alertCount += !text.isEmpty();
  }
  snooze_btn->setVisible(!alerts["Offroad_ConnectivityNeeded"]->text().isEmpty());
  return alertCount;
}

UpdateAlert::UpdateAlert(QWidget *parent) : AbstractAlert(true, parent) {
  releaseNotes = new QLabel(this);
  releaseNotes->setWordWrap(true);
  releaseNotes->setAlignment(Qt::AlignTop);
  scrollable_layout->addWidget(releaseNotes);
}

bool UpdateAlert::refresh() {
  bool updateAvailable = params.getBool("UpdateAvailable");
  if (updateAvailable) {
    releaseNotes->setText(params.get("UpdaterNewReleaseNotes").c_str());
  }
  return updateAvailable;
}
