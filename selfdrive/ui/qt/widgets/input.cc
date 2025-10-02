#include "selfdrive/ui/qt/widgets/input.h"

#include <QPushButton>
#include <QButtonGroup>
#include <QScroller>

#include "system/hardware/hw.h"
#include "selfdrive/ui/qt/util.h"
#include "selfdrive/ui/qt/qt_window.h"
#include "selfdrive/ui/qt/widgets/scrollview.h"


DialogBase::DialogBase(QWidget *parent) : QDialog(parent) {
  Q_ASSERT(parent != nullptr);
  parent->installEventFilter(this);

  setStyleSheet(R"(
    * {
      outline: none;
      color: white;
      font-family: Inter;
    }
    DialogBase {
      background-color: black;
    }
    QPushButton {
      height: 160;
      font-size: 55px;
      font-weight: 400;
      border-radius: 10px;
      color: white;
      background-color: #333333;
    }
    QPushButton:pressed {
      background-color: #444444;
    }
  )");
}

bool DialogBase::eventFilter(QObject *o, QEvent *e) {
  if (o == parent() && e->type() == QEvent::Hide) {
    reject();
  }
  return QDialog::eventFilter(o, e);
}

int DialogBase::exec() {
  setMainWindow(this);
  return QDialog::exec();
}

InputDialog::InputDialog(const QString &title, QWidget *parent, const QString &subtitle, bool secret) : DialogBase(parent) {
  main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 55, 50, 50);
  main_layout->setSpacing(0);

  // build header
  QHBoxLayout *header_layout = new QHBoxLayout();

  QVBoxLayout *vlayout = new QVBoxLayout;
  header_layout->addLayout(vlayout);
  label = new QLabel(title, this);
  label->setStyleSheet("font-size: 90px; font-weight: bold;");
  vlayout->addWidget(label, 1, Qt::AlignTop | Qt::AlignLeft);

  if (!subtitle.isEmpty()) {
    sublabel = new QLabel(subtitle, this);
    sublabel->setStyleSheet("font-size: 55px; font-weight: light; color: #BDBDBD;");
    vlayout->addWidget(sublabel, 1, Qt::AlignTop | Qt::AlignLeft);
  }

  QPushButton* cancel_btn = new QPushButton(tr("Cancel"));
  cancel_btn->setFixedSize(386, 125);
  cancel_btn->setStyleSheet(R"(
    QPushButton {
      font-size: 48px;
      border-radius: 10px;
      color: #E4E4E4;
      background-color: #333333;
    }
    QPushButton:pressed {
      background-color: #444444;
    }
  )");
  header_layout->addWidget(cancel_btn, 0, Qt::AlignRight);
  QObject::connect(cancel_btn, &QPushButton::clicked, this, &InputDialog::reject);
  QObject::connect(cancel_btn, &QPushButton::clicked, this, &InputDialog::cancel);

  main_layout->addLayout(header_layout);

  // text box
  main_layout->addStretch(2);

  QWidget *textbox_widget = new QWidget;
  textbox_widget->setObjectName("textbox");
  QHBoxLayout *textbox_layout = new QHBoxLayout(textbox_widget);
  textbox_layout->setContentsMargins(50, 0, 50, 0);

  textbox_widget->setStyleSheet(R"(
    #textbox {
      margin-left: 50px;
      margin-right: 50px;
      border-radius: 0;
      border-bottom: 3px solid #BDBDBD;
    }
    * {
      border: none;
      font-size: 80px;
      font-weight: light;
      background-color: transparent;
    }
  )");

  line = new QLineEdit();
  line->setStyleSheet("lineedit-password-character: 8226; lineedit-password-mask-delay: 1500;");
  textbox_layout->addWidget(line, 1);

  if (secret) {
    eye_btn = new QPushButton();
    eye_btn->setCheckable(true);
    eye_btn->setFixedSize(150, 120);
    QObject::connect(eye_btn, &QPushButton::toggled, [=](bool checked) {
      if (checked) {
        eye_btn->setIcon(QIcon(ASSET_PATH + "icons/eye_closed.svg"));
        eye_btn->setIconSize(QSize(81, 54));
        line->setEchoMode(QLineEdit::Password);
      } else {
        eye_btn->setIcon(QIcon(ASSET_PATH + "icons/eye_open.svg"));
        eye_btn->setIconSize(QSize(81, 44));
        line->setEchoMode(QLineEdit::Normal);
      }
    });
    eye_btn->toggle();
    eye_btn->setChecked(false);
    textbox_layout->addWidget(eye_btn);
  }

  main_layout->addWidget(textbox_widget, 0, Qt::AlignBottom);
  main_layout->addSpacing(25);

  k = new Keyboard(this);
  QObject::connect(k, &Keyboard::emitEnter, this, &InputDialog::handleEnter);
  QObject::connect(k, &Keyboard::emitBackspace, this, [=]() {
    line->backspace();
  });
  QObject::connect(k, &Keyboard::emitKey, this, [=](const QString &key) {
    line->insert(key.left(1));
  });

  main_layout->addWidget(k, 2, Qt::AlignBottom);
}

QString InputDialog::getText(const QString &prompt, QWidget *parent, const QString &subtitle,
                             bool secret, int minLength, const QString &defaultText) {
  InputDialog d(prompt, parent, subtitle, secret);
  d.line->setText(defaultText);
  d.setMinLength(minLength);
  const int ret = d.exec();
  return ret ? d.text() : QString();
}

QString InputDialog::text() {
  return line->text();
}

void InputDialog::show() {
  setMainWindow(this);
}

void InputDialog::handleEnter() {
  if (line->text().length() >= minLength) {
    done(QDialog::Accepted);
    emitText(line->text());
  } else {
    setMessage(tr("Need at least %n character(s)!", "", minLength), false);
  }
}

void InputDialog::setMessage(const QString &message, bool clearInputField) {
  label->setText(message);
  if (clearInputField) {
    line->setText("");
  }
}

void InputDialog::setMinLength(int length) {
  minLength = length;
}

// ConfirmationDialog

ConfirmationDialog::ConfirmationDialog(const QString &prompt_text, const QString &confirm_text, const QString &cancel_text,
                                       const bool rich, QWidget *parent) : DialogBase(parent) {
  QFrame *container = new QFrame(this);
  container->setStyleSheet(R"(
    QFrame { background-color: #1B1B1B; color: #C9C9C9; }
    #confirm_btn { background-color: #465BEA; }
    #confirm_btn:pressed { background-color: #3049F4; }
  )");
  QVBoxLayout *main_layout = new QVBoxLayout(container);
  main_layout->setContentsMargins(32, rich ? 32 : 120, 32, 32);

  QLabel *prompt = new QLabel(prompt_text, this);
  prompt->setWordWrap(true);
  prompt->setAlignment(rich ? Qt::AlignLeft : Qt::AlignHCenter);
  prompt->setStyleSheet((rich ? "font-size: 42px; font-weight: light;" : "font-size: 70px; font-weight: bold;") + QString(" margin: 45px;"));
  main_layout->addWidget(rich ? (QWidget*)new ScrollView(prompt, this) : (QWidget*)prompt, 1, Qt::AlignTop);

  // cancel + confirm buttons
  QHBoxLayout *btn_layout = new QHBoxLayout();
  btn_layout->setSpacing(30);
  main_layout->addLayout(btn_layout);

  if (cancel_text.length()) {
    QPushButton* cancel_btn = new QPushButton(cancel_text);
    btn_layout->addWidget(cancel_btn);
    QObject::connect(cancel_btn, &QPushButton::clicked, this, &ConfirmationDialog::reject);
  }

  if (confirm_text.length()) {
    QPushButton* confirm_btn = new QPushButton(confirm_text);
    confirm_btn->setObjectName("confirm_btn");
    btn_layout->addWidget(confirm_btn);
    QObject::connect(confirm_btn, &QPushButton::clicked, this, &ConfirmationDialog::accept);
  }

  QVBoxLayout *outer_layout = new QVBoxLayout(this);
  int margin = rich ? 100 : 200;
  outer_layout->setContentsMargins(margin, margin, margin, margin);
  outer_layout->addWidget(container);
}

bool ConfirmationDialog::alert(const QString &prompt_text, QWidget *parent) {
  ConfirmationDialog d(prompt_text, tr("Ok"), "", false, parent);
  return d.exec();
}

bool ConfirmationDialog::confirm(const QString &prompt_text, const QString &confirm_text, QWidget *parent) {
  ConfirmationDialog d(prompt_text, confirm_text, tr("Cancel"), false, parent);
  return d.exec();
}

bool ConfirmationDialog::rich(const QString &prompt_text, QWidget *parent) {
  ConfirmationDialog d(prompt_text, tr("Ok"), "", true, parent);
  return d.exec();
}

// MultiOptionDialog

MultiOptionDialog::MultiOptionDialog(const QString &prompt_text, const QStringList &l, const QString &current, QWidget *parent) : DialogBase(parent) {
  QFrame *container = new QFrame(this);
  container->setStyleSheet(R"(
    QFrame { background-color: #1B1B1B; }
    #confirm_btn[enabled="false"] { background-color: #2B2B2B; }
    #confirm_btn:enabled { background-color: #465BEA; }
    #confirm_btn:enabled:pressed { background-color: #3049F4; }
  )");

  QVBoxLayout *main_layout = new QVBoxLayout(container);
  main_layout->setContentsMargins(55, 50, 55, 50);

  QLabel *title = new QLabel(prompt_text, this);
  title->setStyleSheet("font-size: 70px; font-weight: 500;");
  main_layout->addWidget(title, 0, Qt::AlignLeft | Qt::AlignTop);
  main_layout->addSpacing(25);

  QWidget *listWidget = new QWidget(this);
  QVBoxLayout *listLayout = new QVBoxLayout(listWidget);
  listLayout->setSpacing(20);
  listWidget->setStyleSheet(R"(
    QPushButton {
      height: 135;
      padding: 0px 50px;
      text-align: left;
      font-size: 55px;
      font-weight: 300;
      border-radius: 10px;
      background-color: #4F4F4F;
    }
    QPushButton:checked { background-color: #465BEA; }
  )");

  QButtonGroup *group = new QButtonGroup(listWidget);
  group->setExclusive(true);

  QPushButton *confirm_btn = new QPushButton(tr("Select"));
  confirm_btn->setObjectName("confirm_btn");
  confirm_btn->setEnabled(false);

  for (const QString &s : l) {
    QPushButton *selectionLabel = new QPushButton(s);
    selectionLabel->setCheckable(true);
    selectionLabel->setChecked(s == current);
    QObject::connect(selectionLabel, &QPushButton::toggled, [=](bool checked) {
      if (checked) selection = s;
      if (selection != current) {
        confirm_btn->setEnabled(true);
      } else {
        confirm_btn->setEnabled(false);
      }
    });

    group->addButton(selectionLabel);
    listLayout->addWidget(selectionLabel);
  }
  // add stretch to keep buttons spaced correctly
  listLayout->addStretch(1);

  ScrollView *scroll_view = new ScrollView(listWidget, this);
  scroll_view->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);

  main_layout->addWidget(scroll_view);
  main_layout->addSpacing(35);

  // cancel + confirm buttons
  QHBoxLayout *blayout = new QHBoxLayout;
  main_layout->addLayout(blayout);
  blayout->setSpacing(50);

  QPushButton *cancel_btn = new QPushButton(tr("Cancel"));
  QObject::connect(cancel_btn, &QPushButton::clicked, this, &ConfirmationDialog::reject);
  QObject::connect(confirm_btn, &QPushButton::clicked, this, &ConfirmationDialog::accept);
  blayout->addWidget(cancel_btn);
  blayout->addWidget(confirm_btn);

  QVBoxLayout *outer_layout = new QVBoxLayout(this);
  outer_layout->setContentsMargins(50, 50, 50, 50);
  outer_layout->addWidget(container);
}

QString MultiOptionDialog::getSelection(const QString &prompt_text, const QStringList &l, const QString &current, QWidget *parent) {
  MultiOptionDialog d(prompt_text, l, current, parent);
  if (d.exec()) {
    return d.selection;
  }
  return "";
}

TreeOptionDialog::TreeOptionDialog(const QString &prompt_text, const QList<TreeFolder> &items,
                                   const QString &current, const QString &favParam, QWidget *parent) : DialogBase(parent) {
  QFrame *container = new QFrame(this);
  container->setStyleSheet(R"(
    QFrame { background-color: #1B1B1B; }
    #confirm_btn[enabled="false"] { background-color: #2B2B2B; }
    #confirm_btn:enabled { background-color: #465BEA; }
    #confirm_btn:enabled:pressed { background-color: #3049F4; }
    QTreeWidget {
      background-color: transparent;
      border: none;
    }
    QTreeWidget::item {
      height: 135;
      padding: 0px 50px;
      margin: 5px;
      text-align: left;
      font-size: 55px;
      font-weight: 300;
      border-radius: 10px;
      background-color: #4F4F4F;
      color: white;
    }
    QTreeWidget::item:selected {
      background-color: #465BEA;
    }
    QTreeWidget::branch {
      background-color: transparent;
    }
  )");

  QVBoxLayout *main_layout = new QVBoxLayout(container);
  main_layout->setContentsMargins(55, 50, 55, 50);

  QLabel *title = new QLabel(prompt_text, this);
  title->setStyleSheet("font-size: 70px; font-weight: 500;");
  main_layout->addWidget(title, 0, Qt::AlignLeft | Qt::AlignTop);
  main_layout->addSpacing(25);

  iconBlank = QIcon("../../sunnypilot/selfdrive/assets/icons/star-empty.png");
  iconFilled = QIcon ("../../sunnypilot/selfdrive/assets/icons/star-filled.png");

  treeWidget = new QTreeWidget(this);
  treeWidget->setHeaderHidden(true);
  treeWidget->setIndentation(50);
  treeWidget->setExpandsOnDoubleClick(false); // Disable double-click expansion
  treeWidget->setAnimated(true);
  treeWidget->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
  treeWidget->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
  treeWidget->setVerticalScrollMode(QAbstractItemView::ScrollPerPixel);
  treeWidget->setDragEnabled(false);
  treeWidget->setMouseTracking(true);

  // Connect single-click to expand/collapse
  QObject::connect(treeWidget, &QTreeWidget::itemClicked, [=](QTreeWidgetItem *item, int) {
    if (item->childCount() > 0) {
      item->setExpanded(!item->isExpanded());
      treeWidget->scrollToItem(item->child(0), QAbstractItemView::EnsureVisible);
    }
  });

  QScroller::grabGesture(treeWidget->viewport(), QScroller::LeftMouseButtonGesture);

  // Create initial list of favorites from param
  const QString favs = QString::fromStdString(params.get(favParam.toStdString()));
  mapFavs = new QMap<QString, QList<QPushButton*>>();
  favRefs = new QStringList(favs.split(";"));
  for (const QString &item : *favRefs)
  {
    mapFavs->insert( item, {});
  }

  // Populate tree
  QListIterator<TreeFolder> iter(items);
  while (iter.hasNext()) {
    TreeFolder currItem = iter.next();
    QString prevFolder;
    QString currentFolder;
    if (currItem.folder.isEmpty()) {
      for (const TreeNode &item : currItem.items) {
        QTreeWidgetItem *topLevel = new QTreeWidgetItem();
        topLevel->setText(0, item.displayName);
        topLevel->setData(0, Qt::UserRole, item.ref);
        topLevel->setFlags(topLevel->flags() | Qt::ItemIsSelectable);
        treeWidget->addTopLevelItem(topLevel);
        if (item.ref == current) {
          topLevel->setSelected(true);
        }
      }
    } else {
      QList<QTreeWidgetItem*> folders = treeWidget->findItems(currItem.folder, Qt::MatchExactly, 0);
      QTreeWidgetItem *folderItem = nullptr;
      if (folders.isEmpty()) {
        folderItem = new QTreeWidgetItem(treeWidget);
      } else {
        folderItem = folders.first();
      }
      folderItem->setIcon(0, QIcon(QPixmap("../assets/icons/menu.png")));
      folderItem->setText(0, "  " + currItem.folder);
      folderItem->setFlags(folderItem->flags() | Qt::ItemIsAutoTristate);
      folderItem->setFlags(folderItem->flags() & ~Qt::ItemIsSelectable);

      for (const TreeNode item : currItem.items)
      {
        QTreeWidgetItem *childItem = addChildItem(item.displayName, item.ref, folderItem);
        if (item.ref == current) {
          childItem->setSelected(true);
          folderItem->setExpanded(true);
        }
      }
    }
  }

  // Create favorites folder
  favorites = new QTreeWidgetItem();
  favorites->setIcon(0, QIcon(QPixmap("../assets/icons/menu.png")));
  favorites->setText(0, "  " + tr("Favorites"));
  favorites->setFlags(favorites->flags() | Qt::ItemIsAutoTristate);
  favorites->setFlags(favorites->flags() & ~Qt::ItemIsSelectable);
  treeWidget->insertTopLevelItem(1, favorites);

  // Create favorite nodes
  for (int i = favRefs->size() - 1; i >= 0; --i) {
    QString item = favRefs->at(i);
    if (item.isEmpty()) continue;

    QTreeWidgetItemIterator treeIt(treeWidget);
    QTreeWidgetItem *nodeItem = nullptr;
    while (*treeIt) {
      if (item == (*treeIt)->data(0, Qt::UserRole).toString()) {
        nodeItem = (*treeIt);
        break;
      }
      ++treeIt;
    }
    if (nodeItem == nullptr) continue;

    QTreeWidgetItem *childItem = addChildItem(nodeItem->text(0),
      nodeItem->data(0, Qt::UserRole).toString(), favorites);
    if (item == current) {
      treeWidget->collapseAll();
      childItem->setSelected(true);
      favorites->setExpanded(true);
    }
  }

  confirm_btn = new QPushButton(tr("Select"));
  confirm_btn->setObjectName("confirm_btn");
  confirm_btn->setEnabled(false);

  QObject::connect(treeWidget, &QTreeWidget::itemSelectionChanged, [=]() {
    QList<QTreeWidgetItem*> selectedItems = treeWidget->selectedItems();
    if (!selectedItems.isEmpty()) {
      selection = selectedItems.first()->data(0, Qt::UserRole).toString();
      confirm_btn->setEnabled(selection != current);
    }
  });

  ScrollView *scroll_view = new ScrollView(treeWidget, this);
  scroll_view->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);

  main_layout->addWidget(scroll_view);
  main_layout->addSpacing(35);

  // cancel + confirm buttons
  QHBoxLayout *blayout = new QHBoxLayout;
  main_layout->addLayout(blayout);
  blayout->setSpacing(50);

  QPushButton *cancel_btn = new QPushButton(tr("Cancel"));
  QObject::connect(cancel_btn, &QPushButton::clicked, this, &ConfirmationDialog::reject);
  QObject::connect(confirm_btn, &QPushButton::clicked, this, &ConfirmationDialog::accept);
  blayout->addWidget(cancel_btn);
  blayout->addWidget(confirm_btn);

  QVBoxLayout *outer_layout = new QVBoxLayout(this);
  outer_layout->setContentsMargins(50, 50, 50, 50);
  outer_layout->addWidget(container);
}

QString TreeOptionDialog::getSelection(const QString &prompt_text, const QList<TreeFolder> &items,
                                     const QString &current, const QString &favParam, QWidget *parent) {
  TreeOptionDialog d(prompt_text, items, current, favParam, parent);
  if (d.exec()) {
    return d.selection;
  }
  return "";
}

/**
 * Handles the addition or removal of items from the "favorites" list based on the provided reference identifier.
 *
 * @param displayName The text label associated with the item to be added or removed in the favorites.
 * @param ref A unique reference key identifying the item.
 * @param btn A pointer to the QPushButton associated with the item. The button's icon is updated to indicate
 *            whether the item is currently favorited or not.
 *
 * If the item is already in the favorites, it is removed from the list, its associated buttons have their
 * icons reset, and the favorites tree is updated accordingly. If the item is not in the favorites, it is
 * added to the list, a new associated button is created, and the favorites tree is updated. The current
 * state of the favorites is stored in the Params object as a semicolon-separated string.
 */
void TreeOptionDialog::handleFavorites(const QString &displayName, const QString &ref, QPushButton *btn) {
  if (mapFavs->keys().contains(ref)) { // Remove from favorites
    for (auto *itemBtn:mapFavs->value(ref))
    {
      itemBtn->setIcon(iconBlank);
    }
    mapFavs->remove(ref);
    favRefs->removeAll(ref);
    for (int i = 0; i < favorites->childCount(); ++i) {
      QTreeWidgetItem* child = favorites->child(i);
      if (child && child->data(0, Qt::UserRole).toString() == ref) {
        favorites->removeChild(child);
      }
    }
  } else { // Add to favorites
    QPushButton *favBtn = new QPushButton();
    btn->setIcon(iconFilled);
    mapFavs->insert(ref, {btn, favBtn});
    favRefs->append(ref);
    addChildItem(displayName, ref, favorites, favBtn, true);
  }

  const QString favs =favRefs->join(";");
  params.put("ModelManager_Favs", favs.toStdString());
}

/**
 * Adds a child item to a given folder item within the QTreeWidget.
 *
 * @param displayName The text to display for the child item.
 * @param ref A reference string that uniquely identifies the child item.
 * @param folderItem The parent folder item to which the child item will be added.
 * @param btn A pointer to a QPushButton associated with the child item. If nullptr, a new button will be created.
 * @param addAtTop If true, the child item is added as the first child of the folder item; otherwise, it is appended to the end.
 * @return A pointer to the created QTreeWidgetItem representing the child item.
 */
QTreeWidgetItem* TreeOptionDialog::addChildItem(const QString &displayName, const QString &ref, QTreeWidgetItem *folderItem, QPushButton *btn, bool addAtTop) {
  QTreeWidgetItem *childItem = new QTreeWidgetItem();
  if (btn == nullptr) {
    btn = new QPushButton();
  }
  if (mapFavs->keys().contains(ref)) {
    btn->setIcon(iconFilled);
    (*mapFavs)[ref].append(btn);
  } else {
    btn->setIcon(iconBlank);
  }
  btn->setIconSize(QSize(100, 100));
  QWidget *buttonContainer = new QWidget();
  QHBoxLayout *layout = new QHBoxLayout(buttonContainer);
  layout->addWidget(btn, 0, Qt::AlignRight);
  childItem->setText(0, displayName);
  childItem->setData(0, Qt::UserRole, ref);
  childItem->setFlags(childItem->flags() | Qt::ItemIsSelectable);
  if (addAtTop) {
    folderItem->insertChild(0, childItem);
  } else {
    folderItem->addChild(childItem);
  }
  treeWidget->setItemWidget(childItem, 0, buttonContainer);

  connect(btn, &QPushButton::clicked, btn, [=]() {
    handleFavorites(displayName, ref, btn);
  });
  return childItem;
}
