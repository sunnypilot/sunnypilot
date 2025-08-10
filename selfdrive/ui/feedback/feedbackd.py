#!/usr/bin/env python3
import cereal.messaging as messaging
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from cereal import car, custom
from openpilot.system.micd import SAMPLE_RATE, SAMPLE_BUFFER

FEEDBACK_MAX_DURATION = 10.0
ButtonType = car.CarState.ButtonEvent.Type
ButtonTypeSP = custom.CarStateSP.ButtonEvent.Type

CUSTOM_MAPPING_BOOKMARK = 1  # Custom button mapping value for bookmark action


def main():
  params = Params()
  pm = messaging.PubMaster(['userBookmark', 'audioFeedback'])
  sm = messaging.SubMaster(['rawAudioData', 'bookmarkButton', 'carState', 'selfdriveStateSP', 'carStateSP'])
  should_record_audio = False
  block_num = 0
  waiting_for_release = False
  early_stop_triggered = False
  custom_button_mapping = params.get("SteeringCustomButtonMapping")

  while True:
    sm.update()

    if sm.frame % 60 == 0:  # update params once every 60 frames
      custom_button_mapping = params.get("SteeringCustomButtonMapping")

    custom_mapped = custom_button_mapping == CUSTOM_MAPPING_BOOKMARK
    should_send_bookmark = False
    btn_pressed = False

    # use custom button mapping if available
    use_custom = custom_mapped and sm.updated['carStateSP']
    # only allow the LKAS button to record feedback when MADS is disabled & custom button mapping is not set
    use_lkas = sm.updated['carState'] and sm['carState'].canValid and not sm['selfdriveStateSP'].mads.available and not custom_mapped

    if use_custom:
      for be in sm['carStateSP'].buttonEvents:
        if be.type == ButtonTypeSP.customButton:
          btn_pressed =  be.pressed
    elif use_lkas:
      for be in sm['carState'].buttonEvents:
        if be.type == ButtonType.lkas:
          btn_pressed =  be.pressed
    
    if btn_pressed:
      if not should_record_audio:
        if params.get_bool("RecordAudioFeedback"):  # Start recording on first press if toggle set
          should_record_audio = True
          block_num = 0
          waiting_for_release = False
          early_stop_triggered = False
          cloudlog.info(f"{'LKAS' if use_lkas else 'CUSTOM'} button pressed - starting 10-second audio feedback")
        else:
          should_send_bookmark = True  # immediately send bookmark if toggle false
          cloudlog.info(f"{'LKAS' if use_lkas else 'CUSTOM'} button pressed - bookmarking")
      elif should_record_audio and not waiting_for_release:  # Wait for release of second press to stop recording early
        waiting_for_release = True
    elif waiting_for_release:  # Second press released
      waiting_for_release = False
      early_stop_triggered = True
      cloudlog.info(f"{'LKAS' if use_lkas else 'CUSTOM'} button released - ending recording early")

    if should_record_audio and sm.updated['rawAudioData']:
      raw_audio = sm['rawAudioData']
      msg = messaging.new_message('audioFeedback', valid=True)
      msg.audioFeedback.audio.data = raw_audio.data
      msg.audioFeedback.audio.sampleRate = raw_audio.sampleRate
      msg.audioFeedback.blockNum = block_num
      block_num += 1
      if (block_num * SAMPLE_BUFFER / SAMPLE_RATE) >= FEEDBACK_MAX_DURATION or early_stop_triggered:  # Check for timeout or early stop
        should_send_bookmark = True  # send bookmark at end of audio segment
        should_record_audio = False
        early_stop_triggered = False
        cloudlog.info("10-second recording completed or second button press - stopping audio feedback")
      pm.send('audioFeedback', msg)

    if sm.updated['bookmarkButton']:
      cloudlog.info("Bookmark button pressed!")
      should_send_bookmark = True

    if should_send_bookmark:
      msg = messaging.new_message('userBookmark', valid=True)
      pm.send('userBookmark', msg)


if __name__ == '__main__':
  main()
