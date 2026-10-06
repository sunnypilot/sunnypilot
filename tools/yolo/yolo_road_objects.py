"""Traffic-light crop checks and asynchronous CPU sign recognition."""
from collections import deque
import re
import threading
import time
from urllib.request import urlretrieve

import cv2
import numpy as np


def traffic_light_state(crop):
  if crop.size == 0 or min(crop.shape[:2]) < 6:
    return 'unknown'
  hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
  hue,saturation,value = cv2.split(hsv)
  bright = (saturation >= 80) & (value >= 140)
  scores = {}
  for name,condition in [('red',(hue <= 10) | (hue >= 170)),('yellow',(hue >= 15) & (hue <= 38)),('green',(hue >= 40) & (hue <= 95))]:
    mask = (bright & condition).astype(np.uint8)
    count,labels,stats,_ = cv2.connectedComponentsWithStats(mask)
    score = 0.
    for index in range(1,count):
      x,y,w,h,area = stats[index]
      # Reject broad background patches; look for compact illuminated lamps.
      if area < 2 or area > crop.shape[0]*crop.shape[1]*.25 or not .4 <= w/h <= 2.5:
        continue
      if area/(w*h) < .4:
        continue
      score = max(score,float(value[labels == index].sum()))
    scores[name] = score
  ranked = sorted(scores,key=scores.get,reverse=True)
  return ranked[0] if scores[ranked[0]] > 0 and scores[ranked[0]] > scores[ranked[1]]*1.4 else 'unknown'


def traffic_light_summary(readings,center_bounds=None):
  colors=[color for x,color in sorted(readings) if color in ('red','yellow','green')
          and (center_bounds is None or center_bounds[0]<=x<=center_bounds[1])]
  if not colors and center_bounds is not None:
    colors=[color for _,color in sorted(readings) if color in ('red','yellow','green')]
  counts={color:colors.count(color) for color in ('red','yellow','green')}
  maximum=max(counts.values())
  winners=[color for color,count in counts.items() if count==maximum]
  dominant=(winners[0] if len(winners)==1 else 'mixed') if maximum else None
  return {'lights':colors,'dominant_light':dominant,'dominant_fraction':maximum/len(colors) if colors else 0.}


def sign_class_label(name):
  if name.startswith('speedLimit') and name[10:].isdigit():
    return 'SPEED LIMIT '+name[10:]
  return re.sub(r'([a-z])([A-Z])',r'\1 \2',name).upper()


def sign_regions(labels,names,shape):
  indices = [int(key) for key,name in names.items() if str(name).lower().replace('_',' ').replace('-',' ') in ('traffic sign','traffic signs')]
  if not indices:
    return []
  mask = ((labels==indices[0]) if len(indices)==1 else np.isin(labels,indices)).astype(np.uint8)
  mask = cv2.resize(mask,(shape[1],shape[0]),interpolation=cv2.INTER_NEAREST)
  count,_,stats,_ = cv2.connectedComponentsWithStats(mask)
  return [[int(x),int(y),int(x+w),int(y+h)] for x,y,w,h,area in stats[1:] if w >= 16 and h >= 16 and area >= 100][:8]


class RoadObjectReader:
  def __init__(self,sign_weights=None):
    self.sign_weights=sign_weights
    self.condition = threading.Condition()
    self.pending = None
    self.cache = {}
    self.full_signs=([],0.)
    self.context = None
    self.last_submit = 0
    self.last_frame = None
    self.revision = 0
    self.votes = {}
    self.last_timestamp = {}
    self.vehicle_samples = {}
    self.error = ''
    self.stop = False
    threading.Thread(target=self._worker,daemon=True).start()

  def reset(self,context):
    with self.condition:
      if context != self.context:
        self.context=context;self.cache.clear();self.full_signs=([],0.);self.votes.clear();self.last_timestamp.clear();self.vehicle_samples.clear();self.pending=None;self.last_frame=None

  def light(self,key,crop,timestamp):
    state = traffic_light_state(crop)
    history = self.votes.setdefault(key,deque(maxlen=5))
    if self.last_timestamp.get(key) != timestamp:
      history.append(state);self.last_timestamp[key]=timestamp
    return state if state != 'unknown' and history.count(state) >= 2 else 'unknown'

  def vehicle(self,key,crop,timestamp):
    measurements=lamp_measurements(crop)
    if measurements is None:
      return []
    samples=self.vehicle_samples.setdefault(key,deque(maxlen=90))
    if not samples or samples[-1][0]!=timestamp:
      samples.append((timestamp,measurements))
    while samples and timestamp-samples[0][0]>3:
      samples.popleft()
    return vehicle_light_activity(list(samples))

  def read(self,key):
    with self.condition:
      text,received = self.cache.get(key,('',0))
    return text if time.monotonic()-received < 2 else ''

  def sign_label(self,key):
    return self.read(key)

  def read_boxes(self):
    with self.condition:
      boxes,received=self.full_signs
    return boxes if time.monotonic()-received<2 else []

  def submit(self,image,regions,frame=None,full_frame=False):
    now = time.monotonic()
    if (not regions and not full_frame) or now-self.last_submit < .5 or (frame is not None and frame==self.last_frame):
      return
    self.last_submit=now
    self.last_frame=frame
    crops=[('frame-signs',image.copy())] if full_frame else []
    for key,box in ([] if full_frame else regions[:6]):
      x0,y0,x1,y1=map(int,box)
      pad=max(4,int(max(x1-x0,y1-y0)*.15))
      crop=image[max(0,y0-pad):min(image.shape[0],y1+pad),max(0,x0-pad):min(image.shape[1],x1+pad)]
      if not crop.size or min(crop.shape[:2]) < 16:
        continue
      scale=min(6.,max(1.,120/min(crop.shape[:2])),640/max(crop.shape[:2]))
      crop=cv2.resize(crop,None,fx=scale,fy=scale)
      crops.append((key,crop.copy()))
    with self.condition:
      self.pending=(self.context,crops);self.condition.notify()

  def close(self):
    with self.condition:
      self.stop=True;self.condition.notify()

  def _worker(self):
    sign_model=None
    while True:
      with self.condition:
        self.condition.wait_for(lambda:self.pending is not None or self.stop)
        if self.stop:
          return
        context,crops=self.pending;self.pending=None
      try:
        if self.sign_weights is not None and sign_model is None:
          from ultralytics import YOLO
          if not self.sign_weights.exists():
            self.sign_weights.parent.mkdir(parents=True,exist_ok=True)
            partial=self.sign_weights.with_suffix('.part')
            urlretrieve('https://huggingface.co/cvtechniques/JC-Traffic-Sign-Detection/resolve/2cb01e6788b82d904a1d1e35646e171a1b622fe7/trainv26/weights/best.pt',partial)
            partial.replace(self.sign_weights)
          sign_model=YOLO(str(self.sign_weights))
        readings=[]
        full_signs=None
        for key,crop in crops:
          text=''
          if sign_model is not None:
            result=sign_model.predict(crop,imgsz=640,device='cpu',conf=.25,verbose=False)[0]
            if key=='frame-signs':
              full_signs=[(box.tolist(),sign_class_label(result.names[int(cls)])) for box,cls in zip(result.boxes.xyxy.numpy(),result.boxes.cls.tolist())]
            if len(result.boxes):
              index=int(result.boxes.conf.argmax())
              name=result.names[int(result.boxes.cls[index])]
              text=sign_class_label(name)
          readings.append((key,text))
        with self.condition:
          if context==self.context:
            if full_signs is not None:
              self.full_signs=(full_signs,time.monotonic())
            for key,text in readings:
              self.cache[key] = (text,time.monotonic())
            # Keep only current sign results rather than accumulating sign locations.
            self.cache={key:value for key,value in self.cache.items() if time.monotonic()-value[1]<2}
            self.error=''
            self.revision+=1
      except Exception as error:
        self.error=str(error)
        self.revision+=1


def lamp_measurements(crop):
  """Compare outer rear-lamp regions; this is observation, not brake intent."""
  if crop.size == 0 or crop.shape[0]<24 or crop.shape[1]<32:
    return None
  height,width=crop.shape[:2]
  hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
  hue,saturation,value=cv2.split(hsv)
  red=((hue<10)|(hue>170)) & (saturation>100) & (value>100)
  amber=(hue>=10)&(hue<=38)&(saturation>110)&(value>170)
  values=[]
  for left,right in ((.04,.42),(.58,.96)):
    region=np.s_[int(height*.2):int(height*.85),int(width*left):int(width*right)]
    pixels=value[region]
    values.append((float((pixels*red[region]).sum()/max(pixels.size,1)),float(amber[region].mean())))
  return values


def vehicle_light_activity(samples):
  if len(samples)<4 or samples[-1][0]-samples[0][0]<.6:
    return []
  readings=[]
  for index,side in ((0,'left'),(1,'right')):
    flashing=[sample[1][index][1]>.01 for sample in samples]
    transitions=sum(a!=b for a,b in zip(flashing,flashing[1:]))
    if transitions>=2 and any(flashing):
      readings.append(side+' signal?')
  if len(readings)==2:
    readings=['hazards?']
  # Both red lamp regions must brighten relative to observed earlier values.
  previous=samples[:-1]
  brightened=[]
  for index in (0,1):
    baseline=float(np.percentile([sample[1][index][0] for sample in previous],20))
    current=samples[-1][1][index][0]
    brightened.append(baseline>1 and current>max(baseline*1.6,baseline+5))
  if all(brightened):
    readings.append('brake lights?')
  return readings


def draw_vehicle_lights(overlay, image, box, activity):
  """Highlight currently lit pixels in the regions used by the activity heuristic."""
  height,width=image.shape[:2]
  x0,y0,x1,y1=map(int,box)
  x0,y0,x1,y1=max(0,x0),max(0,y0),min(width,x1),min(height,y1)
  crop=image[y0:y1,x0:x1]
  if crop.size==0:
    return
  hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
  hue,saturation,value=cv2.split(hsv)
  red=((hue<10)|(hue>170)) & (saturation>100) & (value>100)
  amber=(hue>=10)&(hue<=38)&(saturation>110)&(value>170)
  target=overlay[y0:y1,x0:x1]
  h,w=red.shape
  for pixels,color,enabled in ((red,(0,40,255),['brake lights?' in activity]*2),
                               (amber,(0,190,255),[side+' signal?' in activity or 'hazards?' in activity for side in ('left','right')])):
    mask=np.zeros(red.shape,np.uint8)
    for active,(left,right) in zip(enabled,((.04,.42),(.58,.96))):
      if active:
        region=np.s_[int(h*.2):int(h*.85),int(w*left):int(w*right)]
        mask[region]=pixels[region]
    radius=max(2,min(10,round(w*.025)))
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius*2+1,radius*2+1))
    glow=cv2.dilate(mask,kernel).astype(bool)
    target[glow]=(target[glow]*.2+np.array(color)*.8).astype(np.uint8)
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(target,contours,-1,(0,0,0),8,cv2.LINE_AA)
    cv2.drawContours(target,contours,-1,(255,255,255),6,cv2.LINE_AA)
    cv2.drawContours(target,contours,-1,color,3,cv2.LINE_AA)
    target[mask.astype(bool)]=color
