# CarController Debug Replay Guide

This guide outlines the steps needed to replay a drive and debug `carcontroller.py` using breakpoints in the `card.py` process.

---

## ✅ Step 1: Set Environment Variables

`card.py` requires environment variables to simulate the target vehicle. Set them before launching the process.

Example for KIA EV9:

```sh
export FINGERPRINT=KIA_EV9
export SKIP_FW_QUERY=1
```

You can add these to your shell session or prefix the command launching `card.py`.

---

## 🚀 Step 2: Launch `card.py` Manually

Start `card.py` as a standalone process so you can attach a debugger or use breakpoints.

```sh
cd selfdrive/car
python card.py
```

> 🔑 Make sure your breakpoints are set **in this process**, not in the replay one.

---

## 🔁 Step 3: Run the Replay

Use the `replay` tool to play back a segment, blocking certain publishers to avoid conflicts with the live `card.py`.

### Example:

```sh
./tools/replay/replay "cb6aec3054a67f94/00000273--dae50621b9" \
  --block "sendcan,carState,carParams,carOutput,liveTracks,carParamsSP,carStateSP"
```

This prevents `replay` from publishing messages that `card.py` is responsible for generating.

---


## 🔧 Common Issues

| Symptom                                  | Likely Cause                                                                        |
| ---------------------------------------- | ----------------------------------------------------------------------------------- |
| No breakpoints hit in `carcontroller.py` | Replay is blocking too much or not enough. Confirm `card.py` is running standalone. |
| No CAN output                            | `sendcan` not blocked in replay; conflict with replay publisher.                    |
| No data in replay                        | Incorrect segment path or segment not downloaded properly.                          |

---

## 📝 Segment Path Format

The path used in `replay` follows this format:

```
<route_prefix>/<segment_name>
```

Example:

```sh
cb6aec3054a67f94/00000273--dae50621b9
```

