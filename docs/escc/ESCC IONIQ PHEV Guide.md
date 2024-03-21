# This document is still a WIP and I used ChatGPT to help me put things down in writing as there's a lot to cover. Feel free to help improve it.

## Introduction
Welcome to the ESCC (Enhanced Smart Cruise Control) IONIQ PHEV Guide. This document provides detailed instructions for connecting and configuring the ESCC Interceptor board with your Hyundai IONIQ Plug-in Hybrid Electric Vehicle (PHEV). Our goal is to simplify the wiring process, enhance vehicle functionality, and ensure a seamless integration with aftermarket components like the Panda device.

## Terminology and Abbreviations
- **ESCC**: Enhanced Smart Cruise Control
- **PANDA**: A universal car interface
- **C-CAN**: Chassis Controller Area Network
- **L-CAN**: Local Controller Area Network
- **IGPM**: Ignition Power Module

## Components

### Harness Female Connector
This connector originates from the car's harness and plugs directly into the radar's male connector.

![](attachment/a4ae5e59abc1483c766af0e9377441ce.png)

### Radar's Male Connector
Located on the radar, this is where the car's harness plugs in. The image shows the connector from the front, with securing guides facing upwards.

![](attachment/caab30983673f68f7ae8f702c856ac44.png)

### ESCC Interceptor Board
Our custom-designed ESCC board simplifies the required wiring for the project.

![](attachment/d129bd73bafecc8d21472d0e981c163b.png)

## Connection Instructions

1. **Connect the Radar's Male Connector**: Solder the radar's male connector to the `HKG-MANDO-HHANRESS` spot on the ESCC board. Ensure all other connectors are also correctly soldered in place. We use double connectors for redundancy or future modifications.

    ![](attachment/a21845b6f9830c1e4b28091d653d2e77.png)

## Understanding the Board Sections
![](attachment/319716f93d3ddc35b46563f11587c030.png)

### I/O from / to PANDA (Left Side)
- Start with the `JST XH-2` connector at the bottom, which receives the C-CAN from the car's radar.
- Follow the traces to the `CSTHRCN` connector for C-CAN input/output.
- The `COUT` connector at the top includes an extra pin for a relay switch, which can be ignored for this guide.

### I/O from / to CAR Harness (Middle Up)
- The `FINAL C-CAN` connector taps directly into the car's C-CAN network, connecting to whatever output the Panda device generates.

### L-CAN I/O Unused, Passthrough
- The L-CAN connection is not intercepted and is passed through from the radar's connector to the car's harness.

### Power Outputs
- Two types of power outputs are available: 5V (unused) and 12V. Only the 12V output is used in this setup.

**WARNING:** The `BAT` connector is always live. Exercise caution during handling.

## Wire Configuration from the Radar Connector and Connections

- White wires are used for both L-CAN HIGH and C-CAN HIGH, blue for C-CAN LOW, and green for L-CAN LOW.
- Yellow indicates the BAT line, red for IGN, and black for GND.

### Viewing the Car's Harness from Different Angles

#### From the Back
![](attachment/967edbc70d3a2481639ec347fc0cf33d.png)

#### Upside Down
![](attachment/c058dd352308ab61cdb1e86ff47c6fe9.png)

#### Tracing Cables and Pins Through the Board
![](attachment/f62476c3c75255cd39558ea40ffa4428.png)

### Wires Going to the Panda
Ensure a 120-ohm resistor is in place for both C-CAN Up to Panda and Down from Panda connections.

![](attachment/e4b242ec00c3fa73314b0ad191afc199.png)

## Disclaimer

Remember, this guide is for educational purposes, and modifications to your vehicle are performed at your own risk. Always ensure safety and compliance with local automotive regulations.
