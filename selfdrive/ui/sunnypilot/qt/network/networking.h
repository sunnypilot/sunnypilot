/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once
#include "selfdrive/ui/qt/network/networking.h"


class NetworkingSP : public Networking {
    Q_OBJECT

public:
    explicit NetworkingSP(QWidget *parent = nullptr);
};

class AdvancedNetworkingSP : public AdvancedNetworking {
    Q_OBJECT

public:
    explicit AdvancedNetworkingSP(QWidget *parent = nullptr, WifiManager *wifi = nullptr);

private:
    Params params;

public slots:
    void toggleTethering(bool enabled) override;
};
