#include <QApplication>
#include <QLabel>
#include <QPushButton>
#include <QScrollBar>
#include <QVBoxLayout>
#include <QWidget>
#include <QtConcurrent>
#include <cstdio>
#include <sstream>

#include "common/params.h"
#include "common/swaglog.h"
#include "system/hardware/hw.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/qt_window.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

std::string executeCommand(const char* cmd) {
  std::array<char, 128> buffer{};
  std::ostringstream result;
  std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
  if (!pipe) {
    LOGW("Failed to open pipe");
    throw std::runtime_error("popen() failed!");
  }
  while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
    result << buffer.data();
  }
  return result.str();
}

int main(int argc, char *argv[]) {
  initApp(argc, argv);
  QApplication a(argc, argv);
  QWidget window;
  setMainWindow(&window);

  QGridLayout *main_layout = new QGridLayout(&window);
  main_layout->setMargin(50);

  QLabel *label = new QLabel(argv[1]);
  label->setWordWrap(true);
  label->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::MinimumExpanding);
  ScrollView *scroll = new ScrollView(label);
  scroll->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
  main_layout->addWidget(scroll, 0, 0, Qt::AlignTop);

  // Scroll to the bottom
  QObject::connect(scroll->verticalScrollBar(), &QAbstractSlider::rangeChanged, [=]() {
    scroll->verticalScrollBar()->setValue(scroll->verticalScrollBar()->maximum());
  });

  QPushButton *btn = new QPushButton();
  QPushButton *update_btn = new QPushButton();
  update_btn->setText(QObject::tr("Update"));
#ifdef __aarch64__
  btn->setText(QObject::tr("Reboot"));
  QFutureWatcher<void> watcher;
  QObject::connect(btn, &QPushButton::clicked, [=]() {
    Hardware::reboot();
  });
  QObject::connect(update_btn, &QPushButton::clicked, [=, &watcher]() {
    btn->setEnabled(false);
    update_btn->setEnabled(false);
    update_btn->setText(QObject::tr("Updating..."));
    const std::string git_branch = Params().get("GitBranch");
    const std::string git_remote = Params().get("GitRemote");
    const std::string to_home_dir = "cd /data/openpilot";
    const std::string check_remote = "git remote | grep origin-update";
    const std::string reset_remote = "git remote remove origin-update && git remote add origin-update " + git_remote + " 2>&1";
    const std::string add_remote = "git remote add origin-update " + git_remote + " 2>&1";
    const std::string fetch_remote = "git fetch origin-update " + git_branch + " 2>&1";
    const std::string reset_branch = "git reset --hard origin-update/" + git_branch + " 2>&1";

    std::string remote_cmd = add_remote;
    if (!std::system((to_home_dir + " && " + check_remote).c_str())) {
      remote_cmd = reset_remote;
    }
    const std::string cmd = to_home_dir + "; " + remote_cmd + "; " + fetch_remote + "; " + reset_branch;

    QFuture<void> future = QtConcurrent::run([=]() {
      std::string output = executeCommand(cmd.c_str());
      //LOGW("CHECK OUTPUT PLS\n%s", output.c_str());
      QMetaObject::invokeMethod(label, "setText", Qt::QueuedConnection,
                                Q_ARG(QString, QString::fromStdString(output)));
    });
    QObject::connect(&watcher, &QFutureWatcher<void>::finished, [=]() {
      btn->setEnabled(true);
      update_btn->setEnabled(true);
      update_btn->setText("Ready to Reboot");
    });
    watcher.setFuture(future);
  });
#else
  update_btn->setEnabled(false);
  btn->setText(QObject::tr("Exit"));
  QObject::connect(btn, &QPushButton::clicked, &a, &QApplication::quit);
#endif
  main_layout->addWidget(btn, 0, 0, Qt::AlignRight | Qt::AlignBottom);
  main_layout->addWidget(update_btn, 0, 0, Qt::AlignLeft | Qt::AlignBottom);

  window.setStyleSheet(R"(
    * {
      outline: none;
      color: white;
      background-color: black;
      font-size: 60px;
    }
    QPushButton {
      padding: 50px;
      padding-right: 100px;
      padding-left: 100px;
      border: 2px solid white;
      border-radius: 20px;
      margin-right: 40px;
    }
    QPushButton:disabled {
      color: #33FFFFFF;
      border: 2px solid #33FFFFFF;
    }
  )");

  return a.exec();
}
