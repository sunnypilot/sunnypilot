#include <QApplication>
#include <QLabel>
#include <QPushButton>
#include <QScrollBar>
#include <QVBoxLayout>
#include <QWidget>
#include <QtConcurrent>

#include "common/params.h"
#include "system/hardware/hw.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/qt_window.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"

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
    const std::string cmd1 = "git remote remove origin-update";
    const std::string cmd2 = "git remote add origin-update " + Params().get("GitRemote");
    const std::string cmd3 = "git fetch origin-update " + git_branch;
    const std::string cmd4 = "git reset --hard origin-update/" + git_branch;

    QFuture<void> future = QtConcurrent::run([=]() {
      std::system(("cd /data/openpilot && " + cmd1 + " && " + cmd2 + " && " + cmd3 + " && " + cmd4).c_str());
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
