# Seat Control Integration System

This system integrates the seat control decision-making logic with the sunnypilot UI by using the cereal messaging system.

## Overview

The seat control system consists of:

1. **Decision Logic** (`short_control.py`) - Makes seat control decisions based on vehicle state
2. **Messaging Integration** (`seat_control_integration.py`) - Publishes commands to cereal messaging
3. **UI Display** (`hud_renderer.py`) - Shows seat control commands on the UI
4. **Service Runner** (`seat_control_service.py`) - Background service to run the system

## Architecture

```
Vehicle State (modelV2, carState)
        ↓
Decision Logic (short_control.py)
        ↓
Seat Control Commands
        ↓
Message Publisher (seat_control_integration.py)
        ↓
Cereal Messaging System (seatControl)
        ↓
UI Display (hud_renderer.py)
```

## Message Structure

The system uses a custom cereal message type `seatControl` with the following structure:

```capnp
struct SeatControl {
  command @0 :SeatControlCommand;
  source @1 :SeatControlSource;
  timestamp @2 :UInt64;

  enum SeatControlCommand {
    neutral @0;
    forward @1;
    back @2;
    mildLeft @3;
    mildRight @4;
    hardLeft @5;
    hardRight @6;
  }

  enum SeatControlSource {
    none @0;
    stop @1;
    accelerate @2;
    curve @3;
    turn @4;
  }
}
```

## Files Modified

### Cereal Schema Files
- `cereal/custom.capnp` - Added SeatControl message structure
- `cereal/log.capnp` - Added seatControl event to Event union

### UI Files
- `selfdrive/ui/ui_state.py` - Added seatControl subscription
- `selfdrive/ui/onroad/hud_renderer.py` - Added seat control display

### New Files
- `sunnypilot_dev_msync/seat_control_integration.py` - Message publisher
- `sunnypilot_dev_msync/seat_control_service.py` - Background service
- `sunnypilot_dev_msync/test_seat_control.py` - Test utilities

## Usage

### Running the Seat Control Service

```bash
# Start the service with default 10Hz update rate
python sunnypilot_dev_msync/seat_control_service.py

# Start with custom frequency
python sunnypilot_dev_msync/seat_control_service.py --frequency 20
```

### Testing the System

```bash
# Test the publisher
python sunnypilot_dev_msync/test_seat_control.py publisher

# Test manual message publishing
python sunnypilot_dev_msync/test_seat_control.py manual

# Test message receiving
python sunnypilot_dev_msync/test_seat_control.py subscriber
```

### UI Display

The seat control command is displayed on the UI in the HUD area:
- Position: Right side of screen, below the experimental button
- Shows current command with color coding:
  - NEUTRAL: Gray
  - MILD_LEFT/MILD_RIGHT: Green (engaged color)
  - HARD_LEFT/HARD_RIGHT: Orange
  - FORWARD: Green
  - BACK: Red
- Shows source of command (STOP, ACCELERATE, CURVE, TURN)

## Integration Points

### With Existing Systems

1. **Vehicle State**: Uses existing `modelV2` and `carState` messages
2. **UI System**: Integrates with existing HUD renderer
3. **Messaging**: Uses standard cereal messaging infrastructure

### Customization

To modify the decision logic:
1. Edit `sunnypilot_dev_msync/msync_src/short_control.py`
2. Restart the seat control service

To modify the UI display:
1. Edit `selfdrive/ui/onroad/hud_renderer.py`
2. Restart the UI

## Development Notes

- The system uses a background thread to avoid blocking the main UI
- Message publishing rate is configurable (default 10Hz)
- Error handling ensures the system fails gracefully
- The UI falls back to "NEUTRAL" if no messages are received

## Future Enhancements

- Add seat control command history/logging
- Implement seat control command filtering/smoothing
- Add configuration options for display position/styling
- Integrate with seat actuator hardware (when available)
