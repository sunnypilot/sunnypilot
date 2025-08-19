#pragma once

#include <QDialog>
#include <QLabel>
#include <QLineEdit>
#include <QString>
#include <QVBoxLayout>
#include <QWidget>
#include <QTreeWidget>

#include "common/params.h"
#include "selfdrive/ui/qt/widgets/keyboard.h"


struct TreeNode {
  QString folder;
  QString displayName;
  QString ref;
  int index;
};

struct TreeFolder {
  QString folder;
  QList<TreeNode> items;
};

class DialogBase : public QDialog {
  Q_OBJECT

protected:
  DialogBase(QWidget *parent);
  bool eventFilter(QObject *o, QEvent *e) override;

public slots:
  int exec() override;
};

class InputDialog : public DialogBase {
  Q_OBJECT

public:
  explicit InputDialog(const QString &title, QWidget *parent, const QString &subtitle = "", bool secret = false);
  static QString getText(const QString &title, QWidget *parent, const QString &subtitle = "",
                         bool secret = false, int minLength = -1, const QString &defaultText = "");
  QString text();
  void setMessage(const QString &message, bool clearInputField = true);
  void setMinLength(int length);
  void show();

private:
  int minLength;
  QLineEdit *line;
  Keyboard *k;
  QLabel *label;
  QLabel *sublabel;
  QVBoxLayout *main_layout;
  QPushButton *eye_btn;

private slots:
  void handleEnter();

signals:
  void cancel();
  void emitText(const QString &text);
};

class ConfirmationDialog : public DialogBase {
  Q_OBJECT

public:
  explicit ConfirmationDialog(const QString &prompt_text, const QString &confirm_text,
                              const QString &cancel_text, const bool rich, QWidget* parent);
  static bool alert(const QString &prompt_text, QWidget *parent);
  static bool confirm(const QString &prompt_text, const QString &confirm_text, QWidget *parent);
  static bool rich(const QString &prompt_text, QWidget *parent);
};

class MultiOptionDialog : public DialogBase {
  Q_OBJECT

public:
  explicit MultiOptionDialog(const QString &prompt_text, const QStringList &l, const QString &current, QWidget *parent);
  static QString getSelection(const QString &prompt_text, const QStringList &l, const QString &current, QWidget *parent);
  QString selection;
};

class TreeOptionDialog : public DialogBase {
  Q_OBJECT

public:
  explicit TreeOptionDialog(const QString &prompt_text, const QList<TreeFolder> &items, const QString &current, const QString &favParam, QWidget *parent = nullptr);
  static QString getSelection(const QString &prompt_text, const QList<TreeFolder> &items, const QString &current, const QString &favParam, QWidget *parent = nullptr);
  void handleFavorites(const QString &displayName, const QString &ref, QPushButton* btn);
  QTreeWidgetItem* addChildItem(const QString &displayName, const QString &ref, QTreeWidgetItem* folderItem, QPushButton* btn = nullptr, bool addAtTop = false);
  QString selection;

private:
  QTreeWidget *treeWidget;
  QPushButton *confirm_btn;
  Params params;
  QMap<QString, QList<QPushButton*>> *mapFavs;
  QStringList *favRefs;
  QTreeWidgetItem *favorites;

  QIcon iconBlank;
  QIcon iconFilled;
};
