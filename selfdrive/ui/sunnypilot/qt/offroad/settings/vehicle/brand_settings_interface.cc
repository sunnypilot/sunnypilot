/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/brand_settings_interface.h"

BrandSettingsInterface::BrandSettingsInterface(QWidget *parent) : QWidget(parent)
{
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(0, 0, 0, 0);

  title = new QLabel(tr("<span style='font-family: \"Noto Color Emoji\";'>🚗</span> Brand vehicle settings <span style='font-family: Noto Color Emoji;'>⚙️</span>"));
  // title->setStyleSheet("font-size: 50px; font-weight: 500;");
  //  設定字體大小與粗細
  title->setStyleSheet(
      "font-size: 50px; "
      "font-weight: 500; ");
  // 置中對齊
  title->setAlignment(Qt::AlignCenter);
  main_layout->addWidget(title, Qt::AlignHCenter);

  list = new ListWidget(this, false);
  list->setSpacing(20);
  main_layout->addWidget(list);
}

void BrandSettingsInterface::updatePanel(bool _offroad)
{
  offroad = _offroad;
  updateSettings();
}

void BrandSettingsInterface::SetToggles(const std::vector<std::tuple<QString, QString, QString, QString, bool>> &toggle_defs)
{
  ListWidget *widget = new ListWidget(this);
  for (auto &[param, t_title, t_desc, t_icon, t_needs_restart] : toggle_defs)
  {
    // 建立 ParamControl
    ParamControl *toggle = new ParamControl(param, t_title, t_desc, t_icon, this);

    // 判斷是否鎖定
    bool locked = params.getBool((param + "Lock").toStdString());
    toggle->setEnabled(!locked);

    // 如果需要重啟且未鎖定，附加描述文字和連線事件
    if (t_needs_restart && !locked)
    {
      toggle->setDescription(toggle->getDescription() + tr(" Changing this setting will restart openpilot if the car is powered on."));

      QObject::connect(uiState(), &UIState::engagedChanged, [toggle](bool engaged)
                       { toggle->setEnabled(!engaged); });

      QObject::connect(toggle, &ParamControl::toggleFlipped, [=](bool state)
                       { params.putBool("OnroadCycleRequested", true); });
    }

    // 加到 ListWidget
    ListToggles[param] = toggle;
    widget->addItem(toggle);
  }
  list->addItem(widget);
}