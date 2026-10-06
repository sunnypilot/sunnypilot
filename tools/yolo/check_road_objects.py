"""Small regression check for road-signal observations and sign-model labels."""
import time

import cv2
import numpy as np

from yolo_road_objects import RoadObjectReader,traffic_light_state,vehicle_light_activity,draw_vehicle_lights,sign_class_label,traffic_light_summary


def main():
  summary=traffic_light_summary([(30,'green'),(10,'red'),(20,'red'),(0,'unknown')])
  assert summary['lights']==['red','red','green'] and summary['dominant_light']=='red'
  assert summary['dominant_fraction']==2/3
  assert traffic_light_summary([(1,'red'),(2,'green')])['dominant_light']=='mixed'
  assert traffic_light_summary([])['dominant_light'] is None
  central=traffic_light_summary([(10,'red'),(45,'green'),(55,'green'),(90,'red')],(33,67))
  assert central['lights']==['green','green'] and central['dominant_light']=='green'
  assert traffic_light_summary([(10,'red')],(33,67))['dominant_light']=='red'
  assert traffic_light_summary([(10,'red'),(45,'unknown')],(33,67))['lights']==['red']
  assert traffic_light_summary([(10,'unknown')],(33,67))['dominant_light'] is None

  assert sign_class_label('speedLimit30')=='SPEED LIMIT 30'
  assert sign_class_label('doNotEnter')=='DO NOT ENTER'

  car=np.zeros((100,160,3),np.uint8)
  cv2.rectangle(car,(15,40),(30,55),(0,0,200),-1)
  cv2.rectangle(car,(120,40),(135,55),(0,0,200),-1)
  overlay=car.copy()
  draw_vehicle_lights(overlay,car,(0,0,160,100),['brake lights?'])
  assert not np.array_equal(overlay[45,20],car[45,20])
  assert not np.array_equal(overlay[45,125],car[45,125])
  assert np.array_equal(overlay[90,80],car[90,80])
  assert np.array_equal(car[45,20],[0,0,200])
  amber=car.copy()
  amber[40:56,15:31]=(0,180,255)
  amber[40:56,120:136]=(0,180,255)
  overlay=amber.copy()
  draw_vehicle_lights(overlay,amber,(0,0,160,100),['left signal?'])
  assert not np.array_equal(overlay[45,20],amber[45,20])
  assert np.array_equal(overlay[45,125],amber[45,125])
  draw_vehicle_lights(overlay,amber,(0,0,160,100),['hazards?'])
  assert not np.array_equal(overlay[45,125],amber[45,125])

  for state,color in [('red',(0,0,255)),('yellow',(0,255,255)),('green',(0,255,0))]:
    crop=np.zeros((90,30,3),np.uint8)
    cv2.circle(crop,(15,45),6,color,-1)
    assert traffic_light_state(crop)==state
  dim=np.zeros((18,8,3),np.uint8)
  dim[7:9,3:5]=(80,80,150)
  assert traffic_light_state(dim)=='red'
  assert traffic_light_state(np.zeros((90,30,3),np.uint8))=='unknown'
  ambiguous=np.zeros((90,30,3),np.uint8)
  cv2.circle(ambiguous,(15,20),6,(0,0,255),-1)
  cv2.circle(ambiguous,(15,65),6,(0,255,0),-1)
  assert traffic_light_state(ambiguous)=='unknown'
  flashing=[(t,[(3,.03 if on else 0),(3,0)]) for t,on in ((0,False),(.3,True),(.6,False),(.9,True))]
  assert vehicle_light_activity(flashing)==['left signal?']
  assert vehicle_light_activity([(t,[(12,0),(12,0)]) for t in (0,.3,.6,.9)])==[]
  assert vehicle_light_activity([(0,[(3,0),(3,0)]),(.3,[(3,0),(3,0)]),(.6,[(3,0),(3,0)]),(.9,[(12,0),(12,0)])])==['brake lights?']
  reader=RoadObjectReader()
  try:
    reader.reset('regression')
    reader.full_signs=([([1,2,20,30],'SPEED LIMIT 30')],time.monotonic())
    assert reader.read_boxes()[0][1]=='SPEED LIMIT 30'
    reader.reset('new camera')
    assert reader.read_boxes()==[]
    assert reader.sign_label('absent')==''
    reader.cache['empty']=('',time.monotonic())
    assert reader.sign_label('empty')==''
    assert reader.light('dim',dim,0)=='unknown'
    assert reader.light('dim',dim,0)=='unknown'  # Paused redraw adds no vote.
    assert reader.light('dim',dim,.1)=='red'
    assert reader.light('dim',np.zeros_like(dim),.2)=='unknown'
    reader.cache['recognized']=('SPEED LIMIT 30',time.monotonic())
    assert reader.sign_label('recognized')=='SPEED LIMIT 30'
  finally:
    reader.close()
  print('Traffic-light states, amber flashing, brake brightening, and sign-model labels passed')


if __name__=='__main__':
  main()
