---
title: ICBM (Intelligent Cruise Button Management)
description: Detailed documentation on the ICBM feature in sunnypilot.
---

# ICBM (Intelligent Cruise Button Management)

Intelligent Cruise Button Management (ICBM) is a system designed to manage the vehicle's cruise control set speed by sending cruise control button commands via CAN bus to the car.

ICBM is particularly useful in vehicles openpilot Longitudinal Control is not available or not desirable to use. By simulating button presses to adjust the stock cruise control set speed, sunnypilot's ICBM can manage the car's speed while keeping native safety features active, such as Forward Collision Warning (FCA) and Automatic Emergency Braking (AEB).

ICBM also allows the vehicle to use the following features:

- **[Smart Cruise Control - Vision (SCC-V)]()**
- **[Smart Cruise Control - Map (SCC-M)]()**
- **[Speed Limit Assist (SLA)]()**
- **[Custom ACC Increments]()**
