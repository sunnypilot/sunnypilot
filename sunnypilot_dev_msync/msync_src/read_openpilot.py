import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import sunnypilot_dev_msync.msync_src.short_control as short_control
import time
import cereal.messaging as messaging


subscriptions = ['carState', 'carControl', 'modelV2', 'longitudinalPlan', 'radarState']
# SubMaster subscribes to selected message types
sm = messaging.SubMaster(subscriptions)


def extract_data(sm, interesting_subs):
    """
    Extracts key data from model and car state messages.

    Returns:
        dict: Dictionary containing:
            - acceleration: ModelV2 acceleration data (XYZTData)
            - confidence: ModelV2 confidence value
            - left_blinker: Left blinker state from carState
            - right_blinker: Right blinker state from carState
    """
    result = {
        'acceleration_pred': None,
        'velocity_pred': None,
        'confidence': None,
        'left_blinker': None,
        'right_blinker': None
    }

    # Extract model data
    if 'modelV2' in interesting_subs and sm.updated['modelV2']:
        model_sub = sm['modelV2']
        if hasattr(model_sub, 'acceleration'):
            result['acceleration_pred'] = model_sub.acceleration
        if hasattr(model_sub, 'velocity'):
            result['velocity_pred'] = model_sub.velocity
        if hasattr(model_sub, 'confidence'):
            result['confidence'] = model_sub.confidence


    # Extract car state data
    if 'carState' in interesting_subs and sm.updated['carState']:
        car_sub = sm['carState']
        if hasattr(car_sub, 'leftBlinker'):
            result['left_blinker'] = car_sub.leftBlinker
        if hasattr(car_sub, 'rightBlinker'):
            result['right_blinker'] = car_sub.rightBlinker
        if hasattr(car_sub, 'vEgo'):
            result['vEgo'] = car_sub.vEgo
        if hasattr(car_sub, 'aEgo'):
            result['aEgo'] = car_sub.aEgo

    return result


def execute_control(interesting_subs=['modelV2', 'carState'], latency=0.5):
    """
    Execute control loop that listens to topics, extracts data, and calls seat_control.
    Args:
        interesting_subs: List of topics to subscribe to
        latency: Time between control updates in seconds
    Returns:
        Control response at the specified latency rate
    """

    print("Starting seat control execution...")
    sm = messaging.SubMaster(interesting_subs)
    decider = short_control.Decider(turn_thresh_1=1.0, turn_thresh_2=3.0, long_thresh=1.0)
    while True:
        sm.update()

        # Extract data from subscribed topics
        data = extract_data(sm, interesting_subs)
        # Check for None values in the data
        if not any(value is None for value in data.values()):
            decider.set_data(data)
            # Call seat control with extracted data
            response = decider.short_decision()
            yield response

        # Sleep for specified latency
        time.sleep(latency)


if __name__ == "__main__":
    latency = 0.1  # seconds, change as needed

    # Parsing options: 'modelV2', 'longitudinalPlan', 'radarState', 'carControl', 'carState'
    interesting_subs = ['modelV2', 'carState']

    # Set verbose=True to see detailed field-by-field output
    # Set verbose=False to use the original compact display format
    # parse_messages(interesting_subs, latency, verbose=True)
    for control_response in execute_control(interesting_subs, latency):
        print(f"Response: {control_response[0]} | Source: {control_response[1]}        ", end='\r')

