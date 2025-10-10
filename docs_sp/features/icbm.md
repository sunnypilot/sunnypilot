---
title: ICBM (Intelligent Cruise Button Management)
description: Detailed documentation on the ICBM feature in sunnypilot.
---

# ICBM (Intelligent Cruise Button Management)

Intelligent Cruise Button Management (ICBM) is a system designed to manage the vehicle's speed by sending cruise control button commands to the car's computer.

This feature is particularly useful in vehicles where direct control over acceleration and braking by third-party software would disable important safety systems like Automatic Emergency Braking (AEB) and Forward Collision Warning (FCW). By simulating button presses to adjust the stock cruise control, sunnypilot's ICBM can manage the car's speed while keeping these native safety features active.

This also allows the vehicle to use the following features:

- **[Smart Cruise Control - Vision (SCC-V)]():** Adjusts the vehicle's speed for smoother and safer navigation through curves based on curvature information from camera vision.
- **[Smart Cruise Control - Map (SCC-M)]():** Adjusts the vehicle's speed for smoother and safer navigation through curves based on curvature information from OpenStreetMap.
- **[Speed Limit Assist (SLA)]():** Intelligently adjusts the vehicle's speed based on detected speed limits from various sources.
