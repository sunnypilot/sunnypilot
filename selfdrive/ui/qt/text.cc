#include <QLabel>
#include <QPushButton>
#include <QScrollBar>
#include <QVBoxLayout>
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

QLabel *label;

// The format is intentional, even if on PC doesn't look aligned. Font differences are likely the cause. On device it looks fine.
QString text = QString("%1\n%2\n%3\n%4\n%5\n%6\n%7")
              .arg(" ________________________________________________________")
              .arg("|\t\t\t\t\t\t|")
              .arg("|\t" + QObject::tr("Update downloaded. Ready to reboot.") + "\t|")
              .arg("|\t\t\t\t\t\t|")
              .arg("|\t" + QObject::tr("Update: Check and Download Update") + "\t\t|")
              .arg("|\t" + QObject::tr("Reboot: Reboot Device") + "\t\t\t|")
              .arg("| _______________________________________________________\t|");

void setupErrorMessageLabel(QVBoxLayout *main_layout) {
  label->setWordWrap(true);
  label->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::MinimumExpanding);
  label->setAlignment(Qt::AlignTop | Qt::AlignLeft);
  auto *scroll = new ScrollView(label);
  scroll->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
  main_layout->addWidget(scroll);

  // Scroll to the bottom
  QObject::connect(scroll->verticalScrollBar(), &QAbstractSlider::rangeChanged, [=]() {
    scroll->verticalScrollBar()->setValue(scroll->verticalScrollBar()->maximum());
  });
}

void setupActionButton(QGridLayout *button_grid) {
  auto *left_buttons = new QHBoxLayout();
  auto *right_buttons = new QHBoxLayout();
  
  auto *btn = new QPushButton();
  auto *update_btn = new QPushButton();
  update_btn->setText(QObject::tr("Update"));
  auto *reinstall_btn = new QPushButton();
  reinstall_btn->setText(QObject::tr("Launch Setup"));
#ifdef __aarch64__
  btn->setText(QObject::tr("Reboot"));
  auto *watcher = new QFutureWatcher<void>();
  QObject::connect(btn, &QPushButton::clicked, [=]() {
    Hardware::reboot();
  });
  QObject::connect(update_btn, &QPushButton::clicked, [=]() {
    btn->setEnabled(false);
    update_btn->setEnabled(false);
    reinstall_btn->setEnabled(false);
    update_btn->setText(QObject::tr("Updating..."));
    const std::string git_branch = Params().get("GitBranch");
    const std::string git_remote = Params().get("GitRemote");
    const std::string to_home_dir = "cd /data/openpilot";
    const std::string check_remote = "git remote | grep origin-update";
    const std::string reset_remote = "git remote remove origin-update && git remote add origin-update " + git_remote;
    const std::string add_remote = "git remote add origin-update " + git_remote;
    const std::string fetch_remote = "git fetch origin-update " + git_branch;
    const std::string reset_branch = "git reset --hard origin-update/" + git_branch + " 2>&1";

    std::string remote_cmd = add_remote;
    if (!std::system((to_home_dir + " && " + check_remote).c_str())) {
      remote_cmd = reset_remote;
    }
    const std::string cmd = to_home_dir + "; " + remote_cmd + "; " + fetch_remote + "; " + reset_branch;

    QFuture<void> future = QtConcurrent::run([=]() {
      std::string output = executeCommand(cmd.c_str());
      auto formatted = QString::fromStdString(output) + text;
      QMetaObject::invokeMethod(label, "clear", Qt::QueuedConnection);
      QMetaObject::invokeMethod(label, "setText", Qt::QueuedConnection, Q_ARG(QString, formatted));
    });
    watcher->setFuture(future);
  });
  QObject::connect(watcher, &QFutureWatcher<void>::finished, [=]() {
    btn->setEnabled(true);
    update_btn->setEnabled(true);
    reinstall_btn->setEnabled(true);
    update_btn->setText(QObject::tr("Update"));
  });

  QObject::connect(reinstall_btn, &QPushButton::clicked, [=]() {
    btn->setEnabled(false);
    update_btn->setEnabled(false);
    reinstall_btn->setEnabled(false);
    reinstall_btn->setText(QObject::tr("Starting setup..."));
    
    const std::string delete_continue = "sudo rm /data/continue.sh";
    const std::string restart_op = "sudo systemctl restart comma";
    
    const std::string cmd = delete_continue + "; " + restart_op + "; ";

    // Start setup command asynchronously
    QtConcurrent::run([=]() {
        executeCommand(cmd.c_str());
    });
    QApplication::quit();
  });

#else
  update_btn->setEnabled(false);
  btn->setText(QObject::tr("Exit"));
  QObject::connect(btn, &QPushButton::clicked, &app, &QApplication::quit);
#endif
  left_buttons->addWidget(update_btn);
  left_buttons->addWidget(reinstall_btn);
  right_buttons->addWidget(btn);
  
  button_grid->addLayout(left_buttons, 0, 0, Qt::AlignLeft | Qt::AlignBottom);
  button_grid->addLayout(right_buttons, 0, 1, Qt::AlignRight | Qt::AlignBottom);
}

int main(int argc, char *argv[]) {
  initApp(argc, argv);
  QApplication app(argc, argv);
  QWidget window;
  setMainWindow(&window);

  auto *main_layout = new QVBoxLayout(&window);
  main_layout->setMargin(50);

  // Setup the text area layout
  auto *text_layout = new QVBoxLayout();
  label = new QLabel(argv[1]);
  setupErrorMessageLabel(text_layout);
  main_layout->addLayout(text_layout);

  // Setup the button area layout
  auto *button_layout = new QGridLayout();
  setupActionButton(button_layout);
  main_layout->addLayout(button_layout);

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
    QPushButton:pressed {
      background-color: #4a4a4a;
    }
    QPushButton:disabled {
      color: #33FFFFFF;
      border: 2px solid #33FFFFFF;
    }
  )");

  return QApplication::exec();
}
