from sub_fields import *
import sys
import time

subscriptions = ['carState', 'carControl', 'modelV2', 'longitudinalPlan', 'radarState']
# SubMaster subscribes to selected message types
sm = messaging.SubMaster(subscriptions)


def print_model_v2(sub):
    """
    Reads and processes ModelDataV2 messages.
    """
    print("=== ModelDataV2 ===")

    # Velocity (XYZTData struct with x, y, z, t arrays)
    if hasattr(sub, 'velocity') and False:
        vel = sub.velocity
        if hasattr(vel, 'x') and len(vel.x) > 0:
            vel_x_values = [f'{vel.x[i]:.2f}' for i in range(min(5, len(vel.x)))]
            print(f"Velocity X: [{', '.join(vel_x_values)}...] m/s (showing first {len(vel_x_values)})")
        if hasattr(vel, 'y') and len(vel.y) > 0:
            vel_y_values = [f'{vel.y[i]:.2f}' for i in range(min(5, len(vel.y)))]
            print(f"Velocity Y: [{', '.join(vel_y_values)}...] m/s (showing first {len(vel_y_values)})")
        if hasattr(vel, 'z') and len(vel.z) > 0:
            vel_z_values = [f'{vel.z[i]:.2f}' for i in range(min(5, len(vel.z)))]
            print(f"Velocity Z: [{', '.join(vel_z_values)}...] m/s (showing first {len(vel_z_values)})")
        if hasattr(vel, 't') and len(vel.t) > 0:
            vel_t_values = [f'{vel.t[i]:.2f}' for i in range(min(5, len(vel.t)))]
            print(f"Velocity T: [{', '.join(vel_t_values)}...] s (showing first {len(vel_t_values)})")

    # Position (XYZTData struct with x, y, z, t arrays)
    if hasattr(sub, 'position')and False:
        pos = sub.position
        if hasattr(pos, 'x') and len(pos.x) > 0:
            pos_x_values = [f'{pos.x[i]:.2f}' for i in range(min(5, len(pos.x)))]
            print(f"Position X: [{', '.join(pos_x_values)}...] m (showing first {len(pos_x_values)})")
        if hasattr(pos, 'y') and len(pos.y) > 0:
            pos_y_values = [f'{pos.y[i]:.2f}' for i in range(min(5, len(pos.y)))]
            print(f"Position Y: [{', '.join(pos_y_values)}...] m (showing first {len(pos_y_values)})")
        if hasattr(pos, 'z') and len(pos.z) > 0:
            pos_z_values = [f'{pos.z[i]:.2f}' for i in range(min(5, len(pos.z)))]
            print(f"Position Z: [{', '.join(pos_z_values)}...] m (showing first {len(pos_z_values)})")
        if hasattr(pos, 't') and len(pos.t) > 0:
            pos_t_values = [f'{pos.t[i]:.2f}' for i in range(min(5, len(pos.t)))]
            print(f"Position T: [{', '.join(pos_t_values)}...] s (showing first {len(pos_t_values)})")

    # Acceleration (XYZTData struct with x, y, z, t arrays)
    if hasattr(sub, 'acceleration'):
        accel = sub.acceleration
        if hasattr(accel, 'x') and len(accel.x) > 0:
            accel_x_values = [f'{accel.x[i]:.2f}' for i in range(min(11, len(accel.x)))]
            print(f"Acceleration X: [{', '.join(accel_x_values)}...] m/s² (showing first {len(accel_x_values)})")
        if hasattr(accel, 'y') and len(accel.y) > 0:
            accel_y_values = [f'{accel.y[i]:.2f}' for i in range(min(11, len(accel.y)))]
            print(f"Acceleration Y: [{', '.join(accel_y_values)}...] m/s² (showing first {len(accel_y_values)})")
        if hasattr(accel, 'z') and len(accel.z) > 0:
            accel_z_values = [f'{accel.z[i]:.2f}' for i in range(min(5, len(accel.z)))]
            print(f"Acceleration Z: [{', '.join(accel_z_values)}...] m/s² (showing first {len(accel_z_values)})")
        if hasattr(accel, 't') and len(accel.t) > 0:
            accel_t_values = [f'{accel.t[i]:.2f}' for i in range(min(11, len(accel.t)))]
            print(f"Acceleration T: [{', '.join(accel_t_values)}...] s (showing first {len(accel_t_values)})")

    # Lane Lines (4 lane lines, each with XYZTData struct containing x, y, z, t arrays)
    if hasattr(sub, 'laneLines'):
        for i, lane in enumerate(sub.laneLines):
            print(f"Lane Line {i}:")
            if hasattr(lane, 'x') and len(lane.x) > 0:
                lane_x_values = [f'{lane.x[j]:.2f}' for j in range(min(3, len(lane.x)))]
                print(f"  X: [{', '.join(lane_x_values)}...] m")
            if hasattr(lane, 'y') and len(lane.y) > 0:
                lane_y_values = [f'{lane.y[j]:.2f}' for j in range(min(3, len(lane.y)))]
                print(f"  Y: [{', '.join(lane_y_values)}...] m")
            if hasattr(lane, 'z') and len(lane.z) > 0:
                lane_z_values = [f'{lane.z[j]:.2f}' for j in range(min(3, len(lane.z)))]
                print(f"  Z: [{', '.join(lane_z_values)}...] m")
            if hasattr(lane, 't') and len(lane.t) > 0:
                lane_t_values = [f'{lane.t[j]:.2f}' for j in range(min(3, len(lane.t)))]
                print(f"  T: [{', '.join(lane_t_values)}...] s")

    # Lane Line Probabilities
    if hasattr(sub, 'laneLineProbs'):
        print(f"Lane Line Probs: [{', '.join([f'{p:.3f}' for p in sub.laneLineProbs])}]")

    # Confidence
    if hasattr(sub, 'confidence'):
        print(f"Confidence: {sub.confidence}")

    print()

def print_model(sub, prev_conf=None):
    """
    Reads and processes perception-prediction model messages.
    """
    conf_dict = {"red": "Low   ", "yellow": "Medium", "green": "High  "}
    conf_str = conf_dict.get(sub.confidence, str(sub.confidence))
    if prev_conf is None:
        print("Model Confidence: ", end="", flush=True)
    if conf_str != prev_conf:
        sys.stdout.write("\rModel Confidence: {}".format(conf_str))
        sys.stdout.flush()
    return conf_str


def print_longitudinal_plan(sub):
    """
    Reads and processes LongitudinalPlan messages.
    """
    print("=== LongitudinalPlan ===")

    # Longitudinal Plan Source
    if hasattr(sub, 'longitudinalPlanSource'):
        print(f"Longitudinal Plan Source: {sub.longitudinalPlanSource}")

    # Accelerations
    if hasattr(sub, 'accels') and len(sub.accels) > 0:
        print(f"Accelerations: [{', '.join([f'{a:.2f}' for a in sub.accels])}] m/s²")

    # Speeds
    if hasattr(sub, 'speeds') and len(sub.speeds) > 0:
        print(f"Speeds: [{', '.join([f'{s:.2f}' for s in sub.speeds])}] m/s")

    # Jerks
    if hasattr(sub, 'jerks') and len(sub.jerks) > 0:
        print(f"Jerks: [{', '.join([f'{j:.2f}' for j in sub.jerks])}] m/s³")

    # Has Lead
    if hasattr(sub, 'hasLead'):
        print(f"Has Lead: {sub.hasLead}")

    print()

def print_radar_state(sub):
    """
    Reads and processes RadarState messages.
    """
    print("=== RadarState ===")

    # Lead One
    if hasattr(sub, 'leadOne'):
        lead = sub.leadOne
        print("Lead One:")
        if hasattr(lead, 'dRel'):
            print(f"  dRel: {lead.dRel:.2f} m")
        if hasattr(lead, 'yRel'):
            print(f"  yRel: {lead.yRel:.2f} m")
        if hasattr(lead, 'vRel'):
            print(f"  vRel: {lead.vRel:.2f} m/s")
        if hasattr(lead, 'aRel'):
            print(f"  aRel: {lead.aRel:.2f} m/s²")
        if hasattr(lead, 'dPath'):
            print(f"  dPath: {lead.dPath:.2f} m")
        if hasattr(lead, 'modelProb'):
            print(f"  modelProb: {lead.modelProb:.3f}")
        if hasattr(lead, 'fcw'):
            print(f"  fcw: {lead.fcw}")
        if hasattr(lead, 'radarTrackId'):
            print(f"  radarTrackId: {lead.radarTrackId}")

    # Lead Two
    if hasattr(sub, 'leadTwo'):
        lead = sub.leadTwo
        print("Lead Two:")
        if hasattr(lead, 'dRel'):
            print(f"  dRel: {lead.dRel:.2f} m")
        if hasattr(lead, 'yRel'):
            print(f"  yRel: {lead.yRel:.2f} m")
        if hasattr(lead, 'vRel'):
            print(f"  vRel: {lead.vRel:.2f} m/s")
        if hasattr(lead, 'aRel'):
            print(f"  aRel: {lead.aRel:.2f} m/s²")
        if hasattr(lead, 'dPath'):
            print(f"  dPath: {lead.dPath:.2f} m")
        if hasattr(lead, 'modelProb'):
            print(f"  modelProb: {lead.modelProb:.3f}")
        if hasattr(lead, 'fcw'):
            print(f"  fcw: {lead.fcw}")
        if hasattr(lead, 'radarTrackId'):
            print(f"  radarTrackId: {lead.radarTrackId}")

    print()

def print_car_control(sub):
    """
    Reads and processes CarControl messages.
    """
    print("=== CarControl ===")

    # Main control flags
    if hasattr(sub, 'enabled'):
        print(f"Enabled: {sub.enabled}")
    if hasattr(sub, 'latActive'):
        print(f"Lateral Active: {sub.latActive}")
    if hasattr(sub, 'longActive'):
        print(f"Longitudinal Active: {sub.longActive}")

    # Blinkers
    if hasattr(sub, 'leftBlinker'):
        print(f"Left Blinker: {sub.leftBlinker}")
    if hasattr(sub, 'rightBlinker'):
        print(f"Right Blinker: {sub.rightBlinker}")

    # Current curvature
    if hasattr(sub, 'currentCurvature'):
        print(f"Current Curvature: {sub.currentCurvature:.4f} 1/m")

    # Actuators
    if hasattr(sub, 'actuators'):
        act = sub.actuators
        print("Actuators:")
        if hasattr(act, 'steeringAngleDeg'):
            print(f"  Steering Angle: {act.steeringAngleDeg:.2f} deg")
        if hasattr(act, 'curvature'):
            print(f"  Curvature: {act.curvature:.4f} 1/m")
        if hasattr(act, 'accel'):
            print(f"  Accel: {act.accel:.2f} m/s²")
        if hasattr(act, 'gas'):
            print(f"  Gas: {act.gas:.3f}")
        if hasattr(act, 'brake'):
            print(f"  Brake: {act.brake:.3f}")
        if hasattr(act, 'torqueOutputCan'):
            print(f"  Torque Output CAN: {act.torqueOutputCan:.2f}")
        if hasattr(act, 'speed'):
            print(f"  Speed: {act.speed:.2f} m/s")

    print()

def print_car_state(sub):
    """
    Reads and processes CarState messages.
    """
    print("=== CarState ===")

    # Vehicle dynamics
    if hasattr(sub, 'vEgo'):
        print(f"vEgo: {sub.vEgo:.2f} m/s")
    if hasattr(sub, 'aEgo'):
        print(f"aEgo: {sub.aEgo:.2f} m/s²")
    if hasattr(sub, 'yawRate'):
        print(f"Yaw Rate: {sub.yawRate:.3f} rad/s")

    # Gas pedal
    if hasattr(sub, 'gas'):
        print(f"Gas: {sub.gas:.3f}")
    if hasattr(sub, 'gasPressed'):
        print(f"Gas Pressed: {sub.gasPressed}")

    # Brake pedal
    if hasattr(sub, 'brake'):
        print(f"Brake: {sub.brake:.3f}")
    if hasattr(sub, 'brakePressed'):
        print(f"Brake Pressed: {sub.brakePressed}")

    # Steering
    if hasattr(sub, 'steeringAngleDeg'):
        print(f"Steering Angle: {sub.steeringAngleDeg:.2f} deg")
    if hasattr(sub, 'steeringRateDeg'):
        print(f"Steering Rate: {sub.steeringRateDeg:.2f} deg/s")

    # Sensor validity
    if hasattr(sub, 'vehicleSensorsInvalid'):
        print(f"Vehicle Sensors Invalid: {sub.vehicleSensorsInvalid}")

    # Blinkers
    if hasattr(sub, 'leftBlinker'):
        print(f"Left Blinker: {sub.leftBlinker}")
    if hasattr(sub, 'rightBlinker'):
        print(f"Right Blinker: {sub.rightBlinker}")

    print()

def print_plan(sub_long, prev_value=None):
    """
    Reads and processes longitudinal plan messages.
    """
    if prev_value is None:
        print("Planned Long Acceleration: ")
        print("Seat Signal: ")
    value = sub_long.accels
    jerks = sub_long.jerks
    display_value = []
    for a in value:
        val_str = f"{a:+.2f}"
        if len(val_str) > 5:
            val_str = val_str[:5]
        else:
            val_str = val_str.ljust(5, '0')
        display_value.append(val_str)
    # Determine seat signal using average jerk
    avg_jerk = sum(jerks) / len(jerks) if len(jerks) > 0 else 0.0
    if avg_jerk > 0.5:
        seat_signal = "Lean Forward"
    elif avg_jerk < -0.5:
        seat_signal = "Lean Back"
    else:
        seat_signal = "Neutral"
    # Only update if changed
    if display_value != prev_value:
        # Move cursor up 2 lines, clear both lines, print both lines (no extra newlines)
        sys.stdout.write("\033[2F")  # Move up 2 lines
        sys.stdout.write(f"\033[2KPlanned Long Acceleration: [{', '.join(display_value)}]\n")
        sys.stdout.write(f"\033[2KSeat Signal: {seat_signal}\n")
        sys.stdout.flush()
    return display_value

def print_controls(sub):
    """
    Reads and processes controls state messages.
    """
    print("Processing controls state...")
    print(f"Steering Angle: {sub.steeringAngle:.2f} rad")
    print(f"Throttle: {sub.throttle:.2f}")
    print(f"Brake: {sub.brake:.2f}")
    print(f"Gear: {sub.gear}")


def parse_messages(interesting_subs, latency, verbose=False):
    print("Starting MSync parsing...\n")
    prev_accel = None
    prev_conf = None
    while True:
        sm.update()

        # Print detailed messages for each topic
        if sm.updated['modelV2'] and 'modelV2' in interesting_subs:
            model_sub = sm['modelV2']
            if verbose:
                print_model_v2(model_sub)
            else:
                prev_conf = print_model(model_sub, prev_conf)

        if sm.updated['longitudinalPlan'] and 'longitudinalPlan' in interesting_subs:
            long_sub = sm['longitudinalPlan']
            if verbose:
                print_longitudinal_plan(long_sub)
            else:
                prev_accel = print_plan(long_sub, prev_accel)

        if sm.updated['radarState'] and 'radarState' in interesting_subs:
            radar_sub = sm['radarState']
            if verbose:
                print_radar_state(radar_sub)

        if sm.updated['carControl'] and 'carControl' in interesting_subs:
            control_sub = sm['carControl']
            if verbose:
                print_car_control(control_sub)

        if sm.updated['carState'] and 'carState' in interesting_subs:
            state_sub = sm['carState']
            if verbose:
                print_car_state(state_sub)

        if not verbose:
            print_plan(sm['longitudinalPlan'])
        time.sleep(latency)




if __name__ == "__main__":
    latency = 0.1  # seconds, change as needed

    # Parsing options: 'modelV2', 'longitudinalPlan', 'radarState', 'carControl', 'carState'
    interesting_subs = ['modelV2', 'carState']

    # Set verbose=True to see detailed field-by-field output
    # Set verbose=False to use the original compact display format
    parse_messages(interesting_subs, latency, verbose=True)