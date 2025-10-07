---
title: Speed Limit Assist
description: Detailed documentation on the Speed Limit Assist feature in sunnypilot.
---

# Speed Limit Assist (SLA)

Speed Limit Assist (SLA) is a comprehensive framework in sunnypilot that adjusts the vehicle's set cruise speed according to detected speed limits. It reconciles data from multiple sources to determine the current speed limit.

## Core Functionality

SLA utilizes various data sources to determine the speed limit for the current road:

- **OpenStreetMap (OSM):** Utilizes map data to fetch speed limits. sunnypilot has a refactored OSM implementation for lower resource usage and provides weekly updates.
- **Car's Stock System:** On some compatible vehicles, it can pull speed limit data directly from the car's native system.

## Key Features and Customization

sunnypilot offers extensive customization for its speed control features:

- **Selectable Speed Limit Source:** Users can define the priority of data sources (e.g., OSM, Navigation, Vision) for determining the speed limit.
- **Configurable Offsets:** You can set an offset above the detected speed limit, either as a fixed value (e.g., +5 mph) or a percentage.
- **Engagement Modes:**
    - **Auto:** Automatically adjusts the cruise speed when a new speed limit is detected.
    - **User Confirm:** Informs the driver of the new speed limit and waits for them to confirm the change before adjusting the speed.
- **Alerts and Warnings:** The system provides alerts to inform the driver before a speed adjustment occurs.
