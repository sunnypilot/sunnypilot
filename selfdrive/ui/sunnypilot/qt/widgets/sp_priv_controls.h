#pragma once

#include "selfdrive/ui/qt/widgets/controls.h"

QFrame *horizontal_line(QWidget *parent = nullptr);

class ParamControlSP : public ParamControl {
  Q_OBJECT

public:
  ParamControlSP(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent = nullptr);

  bool isToggled() { return params.getBool(key); }
};

class AbstractControlSP : public QFrame {
  Q_OBJECT

public:
  void setDescription(const QString &desc) {
    if (description) description->setText(desc);
  }

  void setTitle(const QString &title) {
    title_label->setText(title);
  }

  const QString getDescription() {
    return description->text();
  }

  public slots:
    void showDescription() {
    description->setVisible(true);
  }

  void hideDescription() {
    description->setVisible(false);
  }

  signals:
    void showDescriptionEvent();

protected:
  AbstractControlSP(const QString &title, const QString &desc = "", const QString &icon = "", QWidget *parent = nullptr);
  void hideEvent(QHideEvent *e) override;

  QHBoxLayout *hlayout;
  QPushButton *title_label;

private:
  QLabel *description = nullptr;
};

class ButtonParamControlSP : public AbstractControlSP {
  Q_OBJECT
public:
  ButtonParamControlSP(const QString &param, const QString &title, const QString &desc, const QString &icon,
                     const std::vector<QString> &button_texts, const int minimum_button_width = 300) : AbstractControlSP(title, desc, icon), button_texts(button_texts) {
    const QString style = R"(
      QPushButton {
        border-radius: 20px;
        font-size: 50px;
        font-weight: 450;
        height:150px;
        padding: 0 25 0 25;
        color: #FFFFFF;
      }
      QPushButton:pressed {
        background-color: #4a4a4a;
      }
      QPushButton:checked:enabled {
        background-color: #696868;
      }
      QPushButton:disabled {
        color: #33FFFFFF;
      }
      QPushButton:checked:disabled {
        background-color: #121212;
        color: #33FFFFFF;
      }
    )";
    key = param.toStdString();
    int value = atoi(params.get(key).c_str());

    button_group = new QButtonGroup(this);
    button_group->setExclusive(true);
    for (int i = 0; i < button_texts.size(); i++) {
      QPushButton *button = new QPushButton(button_texts[i], this);
      button->setCheckable(true);
      button->setChecked(i == value);
      button->setStyleSheet(style);
      button->setMinimumWidth(minimum_button_width);
      if (i == 0) hlayout->addSpacing(2);
      hlayout->addWidget(button);
      button_group->addButton(button, i);
    }

    hlayout->setAlignment(Qt::AlignLeft);

    QObject::connect(button_group, QOverload<int>::of(&QButtonGroup::buttonClicked), [=](int id) {
      params.put(key, std::to_string(id));
      emit buttonToggled(id);
    });
  }

  void setEnabled(bool enable) {
    for (auto btn : button_group->buttons()) {
      btn->setEnabled(enable);
    }
    button_group_enabled = enable;

    update();
  }

  void setCheckedButton(int id) {
    button_group->button(id)->setChecked(true);
  }

  void refresh() {
    int value = atoi(params.get(key).c_str());

    if (value >= button_texts.size()) {
      value = button_texts.size() - 1;
    }
    if (value < 0) {
      value = 0;
    }

    button_group->button(value)->setChecked(true);
  }

  void showEvent(QShowEvent *event) override {
    refresh();
  }

  void setButton(QString param) {
    key = param.toStdString();
    int value = atoi(params.get(key).c_str());
    for (int i = 0; i < button_group->buttons().size(); i++) {
      button_group->buttons()[i]->setChecked(i == value);
    }
  }

  void setDisabledSelectedButton(std::string val) {
    int value = atoi(val.c_str());
    for (int i = 0; i < button_group->buttons().size(); i++) {
      button_group->buttons()[i]->setEnabled(i != value);
    }
  }

protected:
  void paintEvent(QPaintEvent *event) override {
    QPainter p(this);
    p.setRenderHint(QPainter::Antialiasing);

    // Calculate the total width and height for the background rectangle
    int w = 0;
    int h = 150;

    for (int i = 0; i < hlayout->count(); ++i) {
      QPushButton *button = qobject_cast<QPushButton *>(hlayout->itemAt(i)->widget());
      if (button) {
        w += button->width();
      }
    }

    // Draw the rectangle
    QRect rect(0 + 2, h - 24, w, h);
    p.setPen(QPen(QColor(button_group_enabled ? "#696868" : "#121212"), 3));
    p.drawRoundedRect(rect, 20, 20);
  }

signals:
  void buttonToggled(int btn_id);

private:
  std::string key;
  Params params;
  QButtonGroup *button_group;
  std::vector<QString> button_texts;

  bool button_group_enabled = true;
};

class ListWidgetSP : public ListWidget {
  Q_OBJECT

public:
  explicit ListWidgetSP(QWidget *parent = 0, const bool split_line = true) : ListWidget(parent), _split_line(split_line) {
  }

  void AddWidgetAt(const int index, QWidget *new_widget) { inner_layout.insertWidget(index, new_widget); }
  void RemoveWidgetAt(const int index) {                              
    if (QLayoutItem* item; (item = inner_layout.takeAt(index)) != nullptr) { 
      if(item->widget()) delete item->widget();                              
      delete item;                                                           
    }                                                                        
  }
  using ListWidget::addItem;
  void ReplaceOrAddWidget(QWidget *old_widget, QWidget *new_widget) {
    if (const int index = inner_layout.indexOf(old_widget); index != -1) {
      RemoveWidgetAt(index);
      AddWidgetAt(index, new_widget);
    } else {
      AddWidgetAt(0, new_widget);
    }
  }
  
private:
  void paintEvent(QPaintEvent *) override {
    QPainter p(this);
    p.setPen(Qt::gray);
    for (int i = 0; i < inner_layout.count() - 1; ++i) {
      QWidget *widget = inner_layout.itemAt(i)->widget();
      if ((widget == nullptr || widget->isVisible()) && _split_line) {
        QRect r = inner_layout.itemAt(i)->geometry();
        int bottom = r.bottom() + inner_layout.spacing() / 2;
        p.drawLine(r.left() + 40, bottom, r.right() - 40, bottom);
      }
    }
  }

  bool _split_line = false;
};

class OptionControlSP : public AbstractControlSP {
  Q_OBJECT

private:
  struct MinMaxValue {
    int min_value;
    int max_value;
  };

public:
  OptionControlSP(const QString &param, const QString &title, const QString &desc, const QString &icon,
                  const MinMaxValue &range, const int per_value_change = 1) : _title(title), AbstractControlSP(title, desc, icon) {
    const QString style = R"(
      QPushButton {
        border-radius: 20px;
        font-size: 60px;
        font-weight: 500;
        width: 150px;
        height: 150px;
        padding: -3 25 3 25;
        color: #FFFFFF;
        font-weight: bold;
      }
      QPushButton:pressed {
        color: #5C5C5C;
      }
      QPushButton:disabled {
        color: #5C5C5C;
      }
    )";

    label.setStyleSheet(label_enabled_style);
    label.setFixedWidth(300);
    label.setAlignment(Qt::AlignCenter);

    const std::vector<QString> button_texts{"－", "＋"};

    key = param.toStdString();
    value = atoi(params.get(key).c_str());

    button_group = new QButtonGroup(this);
    button_group->setExclusive(true);
    for (int i = 0; i < button_texts.size(); i++) {
      QPushButton *button = new QPushButton(button_texts[i], this);
      button->setStyleSheet(style + ((i == 0) ? "QPushButton { text-align: left; }" :
                                                "QPushButton { text-align: right; }"));
      hlayout->addWidget(button, 0, ((i == 0) ? Qt::AlignLeft : Qt::AlignRight) | Qt::AlignVCenter);
      if (i == 0) {
        hlayout->addWidget(&label, 0, Qt::AlignCenter);
      }
      button_group->addButton(button, i);

      QObject::connect(button, &QPushButton::clicked, [=]() {
        int change_value = (i == 0) ? -per_value_change : per_value_change;
        key = param.toStdString();
        value = atoi(params.get(key).c_str());
        value += change_value;
        value = std::clamp(value, range.min_value, range.max_value);
        params.put(key, QString::number(value).toStdString());

        button_group->button(0)->setEnabled(!(value <= range.min_value));
        button_group->button(1)->setEnabled(!(value >= range.max_value));

        updateLabels();

        if (request_update) {
          emit updateOtherToggles();
        }
      });
    }

    hlayout->setAlignment(Qt::AlignLeft);
  }

  void setUpdateOtherToggles(bool _update) {
    request_update = _update;
  }

  inline void setLabel(const QString &text) { label.setText(text); }

  void setEnabled(bool enabled) {
    for (auto btn : button_group->buttons()) {
      btn->setEnabled(enabled);
    }
    label.setEnabled(enabled);
    label.setStyleSheet(enabled ? label_enabled_style : label_disabled_style);
    button_enabled = enabled;

    update();
  }

protected:
  void paintEvent(QPaintEvent *event) override {
    QPainter p(this);
    p.setRenderHint(QPainter::Antialiasing);

    // Calculate the total width and height for the background rectangle
    int w = 0;
    int h = 150;

    for (int i = 0; i < hlayout->count(); ++i) {
      QWidget *widget = qobject_cast<QWidget *>(hlayout->itemAt(i)->widget());
      if (widget) {
        w += widget->width();
      }
    }

    // Draw the rectangle
    QRect rect(0, !_title.isEmpty() ? (h - 24) : 20, w, h);
    p.setBrush(QColor(button_enabled ? "#b24a4a4a" : "#121212")); // Background color
    p.setPen(QPen(Qt::NoPen));
    p.drawRoundedRect(rect, 20, 20);
  }

signals:
  void updateLabels();
  void updateOtherToggles();

private:
  std::string key;
  int value;
  QButtonGroup *button_group;
  QLabel label;
  Params params;
  std::map<QString, QString> option_label = {};
  bool request_update = false;
  QString _title = "";

  const QString label_enabled_style = "font-size: 50px; font-weight: 450; color: #FFFFFF;";
  const QString label_disabled_style = "font-size: 50px; font-weight: 450; color: #5C5C5C;";

  bool button_enabled = true;
};

class SubPanelButton : public QPushButton {
  Q_OBJECT

public:
  explicit SubPanelButton(const QString &text, const int minimum_button_width = 800, QWidget *parent = nullptr) : QPushButton(text, parent) {
    const QString buttonStyle = R"(
      QPushButton {
        border-radius: 20px;
        font-size: 50px;
        font-weight: 450;
        height: 150px;
        padding: 0 25px 0 25px;
        color: #FFFFFF;
      }
      QPushButton:enabled {
        background-color: #393939;
      }
      QPushButton:pressed {
        background-color: #4A4A4A;
      }
      QPushButton:disabled {
        background-color: #121212;
        color: #5C5C5C;
      }
    )";

    setStyleSheet(buttonStyle);
    setFixedWidth(minimum_button_width);
  }
};

class PanelBackButton : public QPushButton {
  Q_OBJECT

public:
  explicit PanelBackButton(const QString &label = "Back", QWidget *parent = nullptr) : QPushButton(label, parent) {
    setObjectName("back_btn");
    setFixedSize(400, 100);
  }
};
