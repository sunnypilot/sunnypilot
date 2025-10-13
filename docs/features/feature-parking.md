# Parking Mode - Intelligent Dashcam

Parking Mode transforms your C3X into an **intelligent dashcam** when your vehicle is parked. It continuously records and **automatically preserves** important moments (impacts) by learning the vehicle's normal vibrations and detecting statistical anomalies.

---

## 🎯 How It Works

### 1️⃣ **Automatic Parking Detection**

```
Engine ON → Engine OFF + Vehicle Stopped → Parking Mode Activated
```

**Detection mechanism:**

- Monitors the `ignitionLine` signal from `pandaStates`
- Monitors vehicle speed from `carState.vEgo`
- When `ignitionLine = False` AND `vEgo < 0.5 m/s` (< 1.8 km/h) = parked
- If `EnableParkingMode = 1` → Activates parking mode

**Responsible code:**

```python
def is_parked(self) -> bool:
    # Check ignition is off
    ignition_off = all(not ps.ignitionLine for ps in self.sm['pandaStates'])

    # Check vehicle is not moving (speed < 0.5 m/s ~= 1.8 km/h)
    standstill = True
    if self.sm.valid['carState']:
        standstill = self.sm['carState'].vEgo < 0.5

    return ignition_off and standstill
```

### 2️⃣ **Continuous Loop Recording**

```
Segment 1 (60s) → Segment 2 (60s) → Segment 3 (60s) → ...
     ↓                ↓                ↓
   Deleted          Deleted         Kept (most recent)
```

- Every **60 seconds**, a new video file is created.
- **Old segments are automatically deleted** (unless preserved).
- **Infinite recording** as long as the battery is OK.

### 3️⃣ **Intelligent Shock Detection (Statistical Method)**

Instead of a fixed G-force threshold, the system now uses a more intelligent, adaptive method to detect impacts.

#### **Phase 1: Calibration (First 10 seconds)**
When parking mode starts, it enters a **10-second calibration phase**.
- It records 100 accelerometer samples to learn the car's **normal baseline vibrations**.
- From this data, it calculates a **mean vector** (average orientation) and a **covariance matrix** (the shape and size of normal vibrations).

```python
# parking_monitor.py
def calibrate(self):
    data = np.array(self.calibration_data)
    self.mean_accel = np.mean(data, axis=0)
    self.cov_inv_accel = np.linalg.inv(np.cov(data, rowvar=False))
    cloudlog.info("Parking mode calibrated.")
```

#### **Phase 2: Anomaly Detection (Mahalanobis Distance)**
After calibration, for each new accelerometer reading, the system calculates its **Mahalanobis distance**.
- This is a statistical measure of how much a point deviates from a distribution.
- A low distance means the vibration is "normal" and fits the learned model.
- A **high distance** means the vibration is a statistical **anomaly**—an outlier that is very unlikely to be part of the normal vibrations. This is considered a **shock**.

```python
# parking_monitor.py
def detect_shock_mahalanobis(self) -> tuple[bool, float]:
    diff = current_accel - self.mean_accel
    # D² = (x - μ)ᵀ Σ⁻¹ (x - μ)
    mahal_dist_sq = diff.T @ self.cov_inv_accel @ diff
    
    is_shock = mahal_dist_sq > self.MAHALANOBIS_THRESHOLD
    return is_shock, math.sqrt(mahal_dist_sq)
```

#### **Why this method is better:**
- **Adaptive:** It automatically adapts to the specific vehicle. A truck and a sports car have different vibration profiles, and the system learns them.
- **Robust:** It's less likely to be fooled by non-shock events like strong winds or nearby heavy traffic, as it looks for deviations from the *learned normal pattern*.
- **Sensitive:** It can detect unusual impacts even if their raw G-force isn't extremely high, because they don't fit the statistical model.

#### **The New Threshold:**
- The old `2.0g` threshold is replaced by `self.MAHALANOBIS_THRESHOLD = 15.0`.
- This is a threshold on the unitless Mahalanobis distance. Like the old value, it's a starting point that may require fine-tuning, but it's based on statistical significance rather than a fixed physical unit.

### 4️⃣ **Automatic Evidence Preservation**

When a shock is detected, the system preserves **7 segments** around the event:

```
Timeline of segments (60s each):

N-2    N-1     N      N+1    N+2    N+3    N+4
│      │       │       │      │      │      │
│      │    🚨SHOCK    │      │      │      │
│      │       │       │      │      │      │
▼      ▼       ▼       ▼      ▼      ▼      ▼
60s    60s    60s     60s    60s    60s    60s

= 7 minutes of evidence around the incident
  (2 min before + 1 min shock + 4 min after)
```

**Technical mechanism:**
- The `deleter.py` process is instructed to keep segments `N-2` through `N+4` by marking them with a `user.preserve` file attribute.

### 5️⃣ **Intelligent Battery Protection**

The system continuously monitors:

```
Voltage < 11.8V  OR  Duration > 12h  →  Automatic SHUTDOWN
```

- **11.8V** = ~20% remaining charge for a typical 12V car battery.
- **12h max** = Hard limit to protect against slow battery drain.

---

## ⚙️ Technical Architecture

### 🧠 **parking_monitor.py** - The Brain

```python
class ParkingMonitor:
    def step(self):  # Runs at 10Hz
        # 1. Check if parked
        if self.is_parked() and not self.parking_mode_active:
            self.is_calibrating = True
            ...

        # 2. If calibrating, collect data
        if self.is_calibrating:
            self.calibration_data.append(...)
            if len(self.calibration_data) >= self.CALIBRATION_SAMPLES:
                self.calibrate()
        
        # 3. If calibrated, detect shocks
        else:
            shock, magnitude = self.detect_shock_mahalanobis()
            if shock:
                self.mark_current_segment_for_preservation()
                self.send_parking_event(magnitude)
```

### 📹 **Recording & Storage** (largely unchanged)
- **camerad, loggerd, encoderd, sensord**: Standard openpilot processes, now configured to run during parking mode.
- **deleter.py**: Modified to preserve a 7-segment window around a shock event.

### 📡 **Internal Communication** (cereal)
- A `ParkingEvent` message is used to notify other processes (like the UI) of a shock.

```capnp
# cereal/custom.capnp
struct ParkingEvent @0xcb9fd56c7057593a {
    shockDetected @0 :Bool;
    magnitude @1 :Float32;     # Mahalanobis distance (unitless)
    timestamp @2 :UInt64;
}
```

---

## 🎮 Practical Usage

### **Activation**
1.  Navigate to **Settings → Device**.
2.  Toggle **"Parking Mode"** to ON.
3.  The system will now automatically activate every time you park.

### **User Interface Features**

#### **1. Visual Alert on Impact Detection**
When an impact is detected, a visual notification appears on screen:

```
┌─────────────────────────────────────┐
│  Parking Mode: Impact Detected      │
│  Impact magnitude: 22.5 - Recording preserved │
└─────────────────────────────────────┘
```
- The magnitude is now a unitless statistical value. A higher number indicates a more severe anomaly.

**Implementation:**
```cpp
// selfdrive/ui/sunnypilot/qt/onroad/alerts.cc
if (uiStateSP()->scene.parkingShockDetected) {
    parking_alert.text1 = "Parking Mode: Impact Detected";
    parking_alert.text2 = QString("Impact magnitude: %1 - Recording preserved").arg(magnitude, 0, 'f', 2);
}
```

#### **2. Last Impact Indicator in Settings**
The Device Settings panel shows the most recent impact:

```
Settings → Device → Last Impact Detected
┌─────────────────────────────────────────┐
│ Last Impact Detected                    │
│ 2025-01-15 14:32:18 (Magnitude: 22.5) →   │
└─────────────────────────────────────────┘
```
- This provides a persistent record of the last event, showing the time and the statistical magnitude of the shock.

**Implementation:**
```cpp
// selfdrive/ui/sunnypilot/qt/offroad/settings/device_panel.cc
void DevicePanelSP::updateParkingShockIndicator() {
    ...
    QString display_text = QString("%1 (Magnitude: %2)")
                             .arg(formatted_time)
                             .arg(magnitude, 0, 'f', 2);
}
```

### **Video Retrieval & Monitoring**
(This process remains the same as before, using SSH or comma connect to find and retrieve preserved segments.)

---

## 🔧 Configuration and Customization

### **Adjust sensitivity**
Edit `sunnypilot/selfdrive/parking_monitor.py`:

```python
# Line 22: Mahalanobis distance threshold
self.MAHALANOBIS_THRESHOLD = 10.0  # More sensitive
self.MAHALANOBIS_THRESHOLD = 20.0  # Less sensitive
```

### **Modify calibration duration**
```python
# Line 23: Number of samples for calibration
self.CALIBRATION_SAMPLES = 50   # Faster 5-second calibration
self.CALIBRATION_SAMPLES = 200  # More robust 20-second calibration
```

After editing, restart the `comma-manager` process.

---

## 🚨 Real Use Cases & Limitations
(The use cases and limitations remain broadly the same, but the detection mechanism is now more robust.)

- **Protects against**: Parking lot collisions, vandalism, hit-and-runs.
- **Limitations**: Still dependent on battery life (12h max) and C3X storage. Detection is based on accelerometer data, not visual analysis.

---

## 📊 Technical Specifications

| Parameter | Value | Description |
|-----------|-------|-------------|
| Segment length | 60s | Duration of each video file. |
| Shock threshold | 15.0 | **Mahalanobis distance** to trigger preservation. |
| Calibration Samples | 100 | Samples taken over **10 seconds** to learn baseline vibration. |
| Preserved segments | 7 | N-2, N-1, N, N+1, N+2, N+3, N+4. |
| Preserved duration | ~7 min | 7 × 60s around shock event. |
| Voltage threshold | 11.8V | Auto-shutdown if battery drops below this. |
| Max parking duration | 12h | Maximum continuous recording time. |
| Monitoring frequency | 10Hz | Shock and battery checking rate. |

---