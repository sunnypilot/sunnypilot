---
title: NNLC (Neural Network Lateral Control)
description: Detailed documentation on the NNLC feature in sunnypilot.
---

# NNLC (Neural Network Lateral Control)

sunnypilot's Neural Network Lateral Control (NNLC) is a feature that enhances the system's ability to steer a vehicle. It enhances the standard lateral controller with one based on a neural network trained on the vehicle's torque data, aiming for smoother and more precise steering adjustments.

## Key Aspects of NNLC

- **Improved Accuracy:** The neural network is trained using driving data specific to each vehicle, which allows for more accurate control.
- **Smoother Turns:** NNLC inputs past curvature data into its driving model to achieve smoother and more precise lateral control, especially noticeable when taking curves on a highway. Users report that it reduces the oversteering and understeering corrections.

Formerly known as "NNFF" (Neural Network Feedforward), NNLC aims to make the driving experience feel more natural and less "jittery" in turns.
