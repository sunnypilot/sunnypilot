# /// script
# requires-python = ">=3.12"
# dependencies = ["ultralytics>=8.4.172", "torch", "opencv-python", "av", "lap>=0.5.12", "pycapnp", "zstandard", "pyzmq", "segmentation-models-pytorch"]
# ///
"""Observational YOLO26 viewer. Camera, radar and optional comma10k segmentation overlays.

python tools/yolo/yolo_viewer.py --demo
python tools/yolo/yolo_viewer.py --replay
python tools/yolo/yolo_viewer.py --comma http://10.83.106.109:8766 --token-file /tmp/roadseg-tokens.json
Replay input requires openpilot/tools/replay/replay --demo --wide-road in the same OPENPILOT_PREFIX.
"""
import argparse
import base64
import gc
import json
import io
import os
import fcntl
import pty
import select
import socket
import termios
import tty
from pathlib import Path
import re
import struct
import subprocess
import sys
import threading
import time
from urllib.request import Request, urlopen

import av
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from ultralytics.engine.results import Results
import yolo_web as road
from yolo_radar import decode_tracks,radar_snapshot,scene_snapshot,RadarAssociator
from yolo_motion import compensated_motion
from yolo_actions import action_preview, road_boundaries
from yolo_road_objects import RoadObjectReader,sign_regions,draw_vehicle_lights,traffic_light_summary

DEMO_ROUTE = 'd59ca223dca8da93/00000498--3190be1e8b/6'

TASKS = {'detect': ('Detection', ''), 'segment': ('Instance masks', '-seg'),
         'semantic': ('Scene segmentation', '-sem')}
SIZES = dict(n='Nano', s='Small', m='Medium', l='Large', x='Extra large')
MODELS = {f'{task}-{size}': label for task in ('scene','sceneMask','detect','segment','semantic','raw') for size,label in SIZES.items()}


SCENE_PALETTE = np.array([[60,200,60],[180,80,180],[130,130,130],[100,100,140],[80,100,140],
                          [160,160,160],[0,180,255],[0,240,255],[40,100,40],[70,150,120],
                          [235,170,75],[50,50,240],[60,120,240],[20,170,240],[30,110,220],
                          [60,130,210],[100,80,180],[140,80,240],[160,60,240]], np.uint8)
SCENE_COLORS=np.zeros((256,1,3),np.uint8)
SCENE_COLORS[:len(SCENE_PALETTE),0]=SCENE_PALETTE


def selected_features(selection):
  task,size=selection.split('-')
  return {'size':size,'objects':task in ('scene','sceneMask','detect','segment'),
          'masks':task in ('sceneMask','segment'),'scene':task in ('scene','sceneMask','semantic')}


def feature_selection(size,objects,masks,scene):
  if masks:
    objects=True
  task=('sceneMask' if masks else 'scene') if scene and objects else 'semantic' if scene else 'segment' if masks else 'detect' if objects else 'raw'
  return task+'-'+size


def restore_selection(args):
  try:
    saved = json.loads(args.settings_file.read_text())
    if not isinstance(saved, dict):
      saved = {}
  except (OSError, ValueError):
    saved = {}
  if args.camera is None:
    args.camera = saved.get('camera') if saved.get('camera') in ('road','wideRoad','driver','wideSides','qcam') else 'road'
  if getattr(args,'segmentation_source',None) is None:
    args.segmentation_source=saved.get('segmentation_source') if saved.get('segmentation_source') in ('yolo','comma10k') else 'yolo'
  if args.camera=='qcam' and not (args.replay or args.demo or args.route):
    args.camera='road'
  if args.model is None:
    model = saved.get('model')
    args.model = model if isinstance(model,str) and model in MODELS else 'scene-n'


def save_selection(args):
  args.settings_file.parent.mkdir(parents=True,exist_ok=True)
  temporary = args.settings_file.with_suffix('.tmp')
  temporary.write_text(json.dumps({'camera':args.camera,'model':args.model,'segmentation_source':args.segmentation_source})+'\n')
  temporary.replace(args.settings_file)


def update_replay_pause_state(state, output):
  text=re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]','',output)
  statuses=list(re.finditer(r'\b(paused\.\.\.|playing|resuming)',text))
  if statuses:
    state['paused']=statuses[-1].group(1).startswith('paused')


def replay_console(command, root, env):
  """Share one replay console between Terminal input and browser shortcuts."""
  master, slave = pty.openpty()
  stdin = sys.stdin.fileno()
  terminal = termios.tcgetattr(stdin) if os.isatty(stdin) else None
  if terminal:
    fcntl.ioctl(slave,termios.TIOCSWINSZ,fcntl.ioctl(stdin,termios.TIOCGWINSZ,b'\0'*8))
    tty.setcbreak(stdin)
  else:
    fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',32,120,0,0))
  try:
    process = subprocess.Popen(command,cwd=root,env=env,stdin=slave,stdout=slave,stderr=slave,start_new_session=True)
  except BaseException:
    os.close(master)
    if terminal:
      termios.tcsetattr(stdin,termios.TCSADRAIN,terminal)
    raise
  finally:
    os.close(slave)
  done = threading.Event()
  process.viewer_replay_state={"paused":False}

  def relay():
    output_tail=""
    try:
      while not done.is_set():
        ready,_,_ = select.select([master]+([stdin] if terminal else []),[],[],.2)
        for fd in ready:
          data = os.read(fd,65536 if fd == master else 64)
          if not data:
            return
          if fd == master:
            output_tail=(output_tail+data.decode('utf-8',errors='ignore'))[-4096:]
            update_replay_pause_state(process.viewer_replay_state,output_tail)
          os.write(sys.stdout.fileno() if fd == master else master,data)
    except OSError:
      pass

  threading.Thread(target=relay,daemon=True).start()

  def send(key):
    if process.poll() is not None:
      raise RuntimeError('Replay exited')
    os.write(master,key.encode())

  def close():
    done.set()
    os.close(master)
    if terminal:
      termios.tcsetattr(stdin,termios.TCSADRAIN,terminal)

  return process,send,close


class CommaSegmenter:
  task='comma10k'
  def __init__(self):
    import segmentation_models_pytorch as smp
    self.model=smp.from_pretrained('commaai/comma10k-segnet').eval().to('mps')
  def predict(self,image,**kwargs):
    rgb=cv2.cvtColor(cv2.resize(image,(512,384)),cv2.COLOR_BGR2RGB)
    pixels=torch.from_numpy(rgb.astype(np.float32).transpose(2,0,1).copy()).unsqueeze(0).to('mps')
    with torch.inference_mode():
      labels=self.model(pixels).argmax(1)[0].cpu().numpy().astype(np.uint8)
    labels=cv2.resize(labels,(image.shape[1],image.shape[0]),interpolation=cv2.INTER_NEAREST)
    return [Results(image,path='',names={0:'road',1:'lane markings',2:'background',3:'vehicles / people',4:'your car'},semantic_mask=torch.from_numpy(labels))]


def load(selection, cache, segmentation_source='yolo'):
  task, size = selection.split('-')
  tasks = ['semantic','segment'] if task=='sceneMask' else ['semantic', 'detect'] if task == 'scene' else [] if task=='raw' else [task]
  return [CommaSegmenter() if t=='semantic' and segmentation_source=='comma10k' else YOLO(str(cache / f'yolo26{size}{TASKS[t][1]}.pt')).to('mps') for t in tasks]


def project_ground_points(points,shape,sample,camera,geometry=None):
  if camera=='qcam':camera='road'
  height,width=shape[:2]
  offset=0
  if camera=='wideSides':
    offset=round(geometry[3]*geometry[0]/geometry[2]);width=geometry[5];camera='wideRoad'
  calibration=(sample or {}).get('wideRoadCamera' if camera=='wideRoad' else 'roadCamera')
  if camera not in ('road','wideRoad') or not calibration:
    return None
  pixel=np.column_stack((points,np.ones(len(points)))) @ np.asarray(calibration['ground']).reshape(3,3).T
  if np.any(pixel[:,2]<=1e-6):
    return None
  pixel=pixel[:,:2]/pixel[:,2:]
  pixel*=np.array([width/calibration['width'],height/calibration['height']])
  pixel[:,0]+=offset
  return pixel if np.isfinite(pixel).all() else None


def draw_track_motion(overlay, boxes, history, timestamp, visible=True, names=None, distance_context=None):
  motions={}
  if boxes is None or boxes.id is None or distance_context is None:
    return motions
  sample,camera,geometry,layout,*_=distance_context
  car=(sample or {}).get('car') or {}
  speed=car.get('speedMps')
  yaw=car.get('yawRateRps',0.)
  if speed is None or not np.isfinite(speed) or yaw is None or not np.isfinite(yaw):
    history.clear()
    return motions
  timestamp=(sample or {}).get('motionTime',timestamp)
  for box,cls,identity in zip(boxes.xyxy.cpu().numpy(),boxes.cls.cpu().tolist(),boxes.id.cpu().tolist()):
    # Sign/light boxes are above the road and cannot use a ground-contact motion model.
    if names is None or names[int(cls)] not in ('car','truck','bus','person','bicycle','motorcycle'):
      continue
    point=object_ground_position(box,overlay.shape,sample,camera,geometry,layout)
    if point is None:
      continue
    identity=int(identity)
    samples=history.setdefault(identity,[])
    if samples and timestamp<samples[-1][0]:
      samples.clear()
    if not samples or timestamp>samples[-1][0]:
      samples.append((timestamp,*point,float(speed),float(yaw)))
    samples[:]=[entry for entry in samples if timestamp-entry[0]<=1.5][-30:]
    motion=compensated_motion(samples)
    if motion is None:
      continue
    points,velocity=motion
    # Suppress low-speed residuals from ground-contact and bounding-box jitter.
    if np.linalg.norm(velocity)<max(.8,float(point[0])*.015):
      continue
    motions[identity]=velocity
    if not visible:
      continue
    pixels=project_ground_points(points,overlay.shape,sample,camera,geometry)
    arrow=project_ground_points(np.array([point,point+velocity]),overlay.shape,sample,camera,geometry)
    if pixels is not None:
      pixels=np.rint(np.clip(pixels,[0,0],[overlay.shape[1]-1,overlay.shape[0]-1])).astype(np.int32)
      cv2.polylines(overlay,[pixels],False,(255,220,0),2)
    if arrow is not None:
      arrow=np.rint(np.clip(arrow,[0,0],[overlay.shape[1]-1,overlay.shape[0]-1])).astype(np.int32)
      cv2.arrowedLine(overlay,tuple(arrow[0]),tuple(arrow[1]),(0,220,255),2,tipLength=.2)
  for identity in list(history):
    if history[identity] and timestamp-history[identity][-1][0]>2:
      del history[identity]
  return motions


def draw_radar_overlay(image,sample,camera,geometry,bumper_offset,tracks,matches=None):
  if bumper_offset is None:
    return  # Radar ranges start at the bumper; don't invent a camera offset.
  colors={'radar':(255,80,255),'camera':(255,220,0),'candidate_radar':(0,160,255),'unknown':(170,170,170)}
  for track in tracks:
    if track['forward']<=0:
      continue
    pixel=project_ground_points(np.array([[track['forward']+bumper_offset,track['left']]]),image.shape,sample,camera,geometry)
    if pixel is None:
      continue
    x,y=map(int,np.rint(pixel[0]))
    if not 0<=x<image.shape[1] or not 0<=y<image.shape[0]:
      continue
    color=colors[track['source']]
    match=next((m for m in (matches or {}).values() if RadarAssociator.key(m['track'])==RadarAssociator.key(track)),None)
    if match is not None:
      box=match['box'];end=(round((box[0]+box[2])/2),round(box[3]))
      cv2.line(image,(x,y),end,(0,0,0),4,cv2.LINE_AA)
      cv2.line(image,(x,y),end,color,2,cv2.LINE_AA)
    cv2.drawMarker(image,(x,y),(0,0,0),cv2.MARKER_DIAMOND,19,5,cv2.LINE_AA)
    cv2.drawMarker(image,(x,y),color,cv2.MARKER_DIAMOND,17,2,cv2.LINE_AA)
    text=f"{track['relative_speed']:+.1f} | {track['forward']:.0f}"
    (text_width,text_height),baseline=cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,.5,1)
    label_x=max(4,min(x+12,image.shape[1]-text_width-4))
    label_y=max(text_height+4,min(y-6,image.shape[0]-baseline-4))
    cv2.putText(image,text,(label_x,label_y),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,0),3,cv2.LINE_AA)
    cv2.putText(image,text,(label_x,label_y),cv2.FONT_HERSHEY_SIMPLEX,.5,color,1,cv2.LINE_AA)


def top_down_segmentation(results,shape,sample,camera,geometry,layout,bumper_offset,excluded,return_ground=False,image=None):
  if camera=='qcam':camera='road'
  """Project ground classes only; elevated objects and sky have no ground footprint."""
  selected=next(((task,result) for task,result in results if task in ('semantic','comma10k')),None)
  if selected is None or bumper_offset is None or camera=='driver':
    return (None,None) if return_ground else None
  calibration=(sample or {}).get('wideRoadCamera' if camera in ('wideRoad','wideSides') else 'roadCamera')
  if not calibration:
    return (None,None) if return_ground else None
  task,result=selected
  labels=result.semantic_mask.data.cpu().numpy().astype(np.uint8)
  height,width=shape[:2]; offset=0
  if camera=='wideSides':
    offset=round(geometry[3]*geometry[0]/geometry[2]);width=geometry[5]
  left,forward=np.meshgrid(np.linspace(20,-20,81),np.linspace(70,0,141))
  points=np.stack((forward.ravel()+bumper_offset,left.ravel(),np.ones(left.size)),axis=1)
  projected=points @ np.asarray(calibration['ground']).reshape(3,3).T
  valid=projected[:,2]>1e-6
  pixels=projected[:,:2]/np.maximum(projected[:,2:],1e-6)
  pixels*=np.array([width/calibration['width'],height/calibration['height']]);pixels[:,0]+=offset
  valid &= np.isfinite(pixels).all(axis=1)&(pixels[:,0]>=offset)&(pixels[:,0]<offset+width)&(pixels[:,1]>=0)&(pixels[:,1]<height)
  if camera=='wideSides':
    normalized=np.column_stack((pixels[:,0]/(shape[1]-1),pixels[:,1]/(height-1),np.ones(len(pixels))))
    for side in ('left','right'):
      local=normalized @ np.linalg.inv(side_matrix(geometry,side,layout)).T
      valid &= ~((local[:,0]>=0)&(local[:,0]<=1)&(local[:,1]>=0)&(local[:,1]<=1))
  x=np.clip(pixels[:,0],0,shape[1]-1).astype(int);y=np.clip(pixels[:,1],0,height-1).astype(int)
  valid &= ~excluded[y,x]
  classes=labels[np.minimum(y*labels.shape[0]//height,labels.shape[0]-1),np.minimum(x*labels.shape[1]//shape[1],labels.shape[1]-1)]
  palette={0:(60,200,60),1:(0,220,255)} if task=='comma10k' else {0:tuple(SCENE_PALETTE[0]),1:tuple(SCENE_PALETTE[1]),9:tuple(SCENE_PALETTE[9])}
  rgba=np.zeros((len(classes),4),np.uint8)
  for cls,color in palette.items():
    mask=valid&(classes==cls);rgba[mask,:3]=color;rgba[mask,3]=150
  ok,png=cv2.imencode('.png',rgba.reshape(141,81,4))
  url='data:image/png;base64,'+base64.b64encode(png).decode() if ok else None
  ground=np.full(len(classes),-1,np.int8)
  ground[valid]=0
  ground[valid&(classes==0)]=1
  if task=='comma10k':ground[valid&(classes==1)]=2
  if image is not None:
    hsv=cv2.cvtColor(image[y,x].reshape(-1,1,3),cv2.COLOR_BGR2HSV).reshape(-1,3)
    yellow=(hsv[:,0]>=15)&(hsv[:,0]<=40)&(hsv[:,1]>=90)&(hsv[:,2]>=100)
    ground[(ground==1)&yellow]=2
  return (url,ground.reshape(141,81)) if return_ground else url


def object_ground_position(box, shape, sample, camera, geometry=None, layout=None):
  if camera=='qcam':camera='road'
  height,width = shape[:2]
  x0,y0,x1,y1 = map(float,box)
  # A composite box must belong wholly to the center view, without a visible
  # side panel at its ground-contact point, to use road calibration.
  if camera == 'wideSides':
    left = round(geometry[3]*geometry[0]/geometry[2])
    contact = [(x0+x1)/2/(width-1),y1/(height-1),1]
    for side in ('right','left'):
      local = np.linalg.inv(side_matrix(geometry,side,layout)) @ contact
      if 0<=local[0]<=1 and 0<=local[1]<=1:
        return None
    if x0<left or x1>left+geometry[5]:
      return None
    x0-=left;x1-=left;width=geometry[5];camera='wideRoad'
  if camera not in ('road','wideRoad') or y1>=height-2 or x0<=1 or x1>=width-2:
    return None
  calibration = (sample or {}).get('wideRoadCamera' if camera=='wideRoad' else 'roadCamera')
  if not calibration:
    return None
  pixel = [(x0+x1)/2*calibration['width']/width,y1*calibration['height']/height,1]
  try:
    point=np.linalg.solve(np.asarray(calibration['ground']).reshape(3,3),pixel)
    point=point[:2]/point[2]
  except (ValueError,np.linalg.LinAlgError):
    return None
  distance=float(np.linalg.norm(point))
  return point if np.isfinite(distance) and point[0]>0 and 1<=distance<=150 else None


def object_distance(box, shape, sample, camera, geometry=None, layout=None):
  point=object_ground_position(box,shape,sample,camera,geometry,layout)
  return float(np.linalg.norm(point)) if point is not None else None


def object_lane(box, shape, sample, camera, geometry=None, layout=None):
  # Use the same pixel projection as the drawn lane lines, sampled at the box bottom.
  if object_ground_position(box,shape,sample,camera,geometry,layout) is None:
    return 'lane unknown'
  height,width=shape[:2]
  x=(float(box[0])+float(box[2]))/2
  bottom=float(box[3])
  if camera=='wideSides':
    x-=round(geometry[3]*geometry[0]/geometry[2]);width=geometry[5];camera='wideRoad'
  calibration=sample.get('wideRoadCamera' if camera=='wideRoad' else 'roadCamera')
  model=sample.get('model',{})
  lines,probabilities=model.get('laneLines',[]),model.get('laneLineProbs',[])
  boundaries=[]
  for index in range(4):
    confidence=probabilities[index] if index<len(probabilities) else 0
    if index>=len(lines) or confidence is None or confidence<(.3 if index in (1,2) else .15):
      boundaries.append(None);continue
    points=road.project_comma_line((height,width),calibration,lines[index])
    intersections=[]
    for first,second in zip(points,points[1:]):
      if min(first[1],second[1])<=bottom<=max(first[1],second[1]) and first[1]!=second[1]:
        intersections.append(float(first[0]+(bottom-first[1])*(second[0]-first[0])/(second[1]-first[1])))
    boundaries.append(float(np.mean(intersections)) if intersections and np.ptp(intersections)<5 else None)
  left,right=boundaries[1:3]
  if left is None or right is None or right-left<10:
    return 'lane unknown'
  if min(abs(x-left),abs(x-right))<6:
    return 'on lane line'
  if left<x<right:
    return 'ego lane'
  width_at_bottom=right-left
  outer_left,outer_right=boundaries[0],boundaries[3]
  if x<left:
    if outer_left is not None and outer_left<left:
      if outer_left<x:
        return 'left lane'
      if outer_left-(left-outer_left)<x:
        return 'left left lane'
    elif outer_left is None:
      if left-width_at_bottom<x:
        return 'left lane'
      if left-2*width_at_bottom<x:
        return 'left left lane'
  if x>right:
    if outer_right is not None and outer_right>right:
      if x<outer_right:
        return 'right lane'
      if x<outer_right+(outer_right-right):
        return 'right right lane'
    elif outer_right is None:
      if x<right+width_at_bottom:
        return 'right lane'
      if x<right+2*width_at_bottom:
        return 'right right lane'
  return 'lane unknown'


def bumper_clearance(point, camera_to_bumper):
  if point is None or camera_to_bumper is None:
    return None
  return max(0.,float(point[0])-camera_to_bumper)


def layout_object_labels(shape, annotations):
  """Place readable, single-line callouts near their objects without stacking text."""
  height,width=shape[:2]
  occupied=[(0,0,min(width,600),40)]  # Reserve the viewer's FPS heading.
  placed=[]
  for box,text in annotations:
    while cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,.55,2)[0][0]+12>width and len(text)>4:
      text=text[:-4]+'...'
    (tw,th),baseline=cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,.55,2)
    w,h=tw+12,th+baseline+10
    x0,y0,x1,y1=map(int,box)
    cx,cy=(x0+x1)//2,(y0+y1)//2
    candidates=[(cx-w//2,y0-h-12),(cx-w//2,y1+12),(x1+12,cy-h//2),(x0-w-12,cy-h//2)]
    # ponytail: greedy placement; dense scenes fall back to the least occupied slot.
    candidates.extend((x,y) for y in range(42,max(43,height-h),h+6) for x in (cx-w//2,8,width-w-8))
    best=None
    for x,y in candidates:
      x,y=max(0,min(width-w,x)),max(0,min(height-h,y))
      rect=(x,y,x+w,y+h)
      overlap=sum(max(0,min(rect[2]+3,r[2])-max(x-3,r[0]))*max(0,min(rect[3]+3,r[3])-max(y-3,r[1])) for r in occupied)
      object_overlap=max(0,min(rect[2],x1)-max(x,x0))*max(0,min(rect[3],y1)-max(y,y0))
      score=(overlap,object_overlap,(x+w/2-cx)**2+(y+h/2-cy)**2)
      if best is None or score<best[0]:
        best=(score,rect)
    rect=best[1]
    occupied.append(rect)
    placed.append((box,text,rect,th))
  return placed


def draw_label_callouts(image, annotations):
  placed=layout_object_labels(image.shape,annotations)
  for box,text,(x,y,x1,y1),th in placed:
    cx,cy=(x+x1)//2,(y+y1)//2
    target=(int(np.clip(cx,box[0],box[2])),int(np.clip(cy,box[1],box[3])))
    anchor=(int(np.clip(target[0],x,x1)),int(np.clip(target[1],y,y1)))
    cv2.line(image,anchor,target,(10,14,20),3,cv2.LINE_AA)
    cv2.line(image,anchor,target,(240,240,240),1,cv2.LINE_AA)
    cv2.circle(image,target,3,(255,255,255),-1,cv2.LINE_AA)
  for box,text,(x,y,x1,y1),th in placed:
    cv2.rectangle(image,(x,y),(x1,y1),(10,14,20),-1)
    cv2.putText(image,text,(x+6,y+th+4),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),2,cv2.LINE_AA)


def draw_object_labels(image, boxes, names, sample, camera, geometry, layout, bumper_offset=None, details=None, extra_labels=None, radar_matches=None):
  annotations=list(extra_labels or [])
  if boxes is None:
    draw_label_callouts(image,annotations)
    return
  ids=boxes.id.cpu().tolist() if boxes.id is not None else [None]*len(boxes)
  for index,(box,cls,confidence,identity) in enumerate(zip(boxes.xyxy.cpu().numpy(),boxes.cls.cpu().tolist(),boxes.conf.cpu().tolist(),ids)):
    name=names[int(cls)]
    type_label=(details or {}).get(index,name)
    if not type_label or (name=='traffic light' and type_label=='UNKNOWN'):
      continue
    confidence_label=f'{confidence:.0%}'
    id_label=str(int(identity)) if identity is not None and 'sign' not in name.lower() else ''
    distance_label=''
    if name in ('car','truck','bus','person','bicycle','motorcycle'):
      point=object_ground_position(box,image.shape,sample,camera,geometry,layout)
      distance=bumper_clearance(point,bumper_offset)
      radar_match=(radar_matches or {}).get(int(identity)) if identity is not None else None
      distance_label=(f"R {radar_match['track']['forward']:.0f} m {radar_match['track']['relative_speed']:+.1f} m/s" if radar_match else f'~{distance:.0f} m' if distance is not None else '?')
      if name in ('car','truck','bus','motorcycle'):
        lane=object_lane(box,image.shape,sample,camera,geometry,layout)
        lane_label={'left left lane':'<<','left lane':'<','ego lane':'=','right lane':'>','right right lane':'>>','on lane line':'|'}.get(lane,'')
        if lane_label:
          distance_label+=' '+lane_label
    x0,y0=max(0,int(box[0])),max(0,int(box[1]))
    x1,y1=min(image.shape[1]-1,int(box[2])),min(image.shape[0]-1,int(box[3]))
    if x1-x0<12 or y1-y0<12:
      continue
    text=f'{type_label} {confidence_label}'
    if id_label:
      text+=' | '+id_label
    if distance_label:
      text+=' | '+distance_label
    annotations.append(((x0,y0,x1,y1),text))
  draw_label_callouts(image,annotations)


def infer(models,image,size,cache=None,key=None):
  if cache is not None and cache.get('key')==key and 'results' in cache:
    return cache['results']
  results=[]
  for model in models:
    if model.task in ('detect','segment'):
      result=model.track(image,persist=True,tracker='bytetrack.yaml',device='mps',imgsz=size,conf=.1,verbose=False)[0]
    else:
      result=model.predict(image,device='mps',imgsz=size,conf=.25,verbose=False)[0]
    # Transfer each annotation tensor once, rather than synchronizing per object.
    if result.boxes is not None:
      result.boxes=result.boxes.cpu()
    if result.semantic_mask is not None:
      result.semantic_mask=result.semantic_mask.cpu()
    results.append((model.task,result))
  if cache is not None:
    cache.update(key=key,results=results)
  return results


def render(models, image, size, opacity, history=None, timestamp=None, distance_context=None, top_down=None, object_mode="full", show_labels=True, show_boxes=True, show_motion=True, road_reader=None, lamp_overlays=None, results=None, radar_matches=None):
  overlay = image.copy()
  descriptions = []
  tracked_boxes = None
  object_boxes,object_names = None,None
  semantic_signs=[]
  if results is None:
    results=infer(models,image,size)
  for task,result in results:
    if object_mode!="full" and result.boxes is not None:
      keep=np.zeros(image.shape[:2],np.uint8)
      if result.masks is not None:
        for polygon in result.masks.xy:
          cv2.fillPoly(keep,[np.rint(polygon).astype(np.int32)],1)
      overlay=np.zeros_like(image)
      overlay[keep.astype(bool)]=image[keep.astype(bool)]
    if task in ('semantic','comma10k'):
      labels = result.semantic_mask.data.cpu().numpy()
      # Cityscapes class colors: roads green, sky blue, vegetation dark green, signs yellow.
      if task=='comma10k':
        palette=np.zeros((256,1,3),np.uint8)
        palette[:5,0]=[(60,200,60),(0,220,255),(0,0,0),(20,170,240),(200,80,180)]
        colors=cv2.applyColorMap(labels.astype(np.uint8),palette)
        background=labels==2
        colors[background]=overlay[background]
      else:
        colors=cv2.applyColorMap(labels.astype(np.uint8),SCENE_COLORS)
      overlay = cv2.addWeighted(overlay, 1-opacity, colors, opacity, 0)
      semantic_signs=sign_regions(labels,result.names,image.shape) if task=='semantic' else []
      descriptions.append('Scene: '+', '.join(result.names[int(i)] for i in np.flatnonzero(np.bincount(labels.reshape(-1),minlength=len(SCENE_PALETTE)))))
    else:
      overlay = result.plot(img=overlay, line_width=2, font_size=14, labels=show_labels and result.boxes is None, conf=False, boxes=show_boxes, masks=object_mode!="original").copy()
      if result.boxes is not None:
        object_boxes,object_names = result.boxes,result.names
        counts = {}
        for i in result.boxes.cls.cpu().tolist():
          name = result.names[int(i)]
          counts[name] = counts.get(name, 0)+1
        descriptions.append('Objects: '+(', '.join(f'{v} {k}' for k,v in counts.items()) or 'none'))
        if result.boxes.id is not None:
          descriptions.append(f'Tracking: {len(result.boxes.id)} objects')
          tracked_boxes = result.boxes
      else:
        descriptions.append(TASKS[task][0])
  comma_scene=any(task=='comma10k' for task,_ in (results or []))
  sensed_lights=[]
  center_left,center_width=0,image.shape[1]
  if distance_context is not None:
    _,view,view_geometry,*_=distance_context
    if view=='wideSides' and view_geometry:
      center_left=round(view_geometry[3]*view_geometry[0]/view_geometry[2])
      center_width=view_geometry[5]
  light_bounds=(center_left+center_width/3,center_left+center_width*2/3)
  vehicle_lamps=[]
  object_details={}
  sign_labels=[]
  if road_reader is not None:
    crops=[]
    if object_boxes is not None:
      identities=object_boxes.id.cpu().tolist() if object_boxes.id is not None else [None]*len(object_boxes)
      for index,(box,cls,identity) in enumerate(zip(object_boxes.xyxy.cpu().numpy(),object_boxes.cls.cpu().tolist(),identities)):
        name=object_names[int(cls)]
        x0,y0,x1,y1=map(int,box)
        crop=image[max(0,y0):min(image.shape[0],y1),max(0,x0):min(image.shape[1],x1)]
        key=f'{name}:{int(identity)}' if identity is not None else f'{name}:{index}'
        if name=='traffic light':
          state=road_reader.light(key,crop,timestamp)
          object_details[index]=state.upper()
          sensed_lights.append(((x0+x1)/2,state))
        elif name=='stop sign':
          crops.append((key,box));text=road_reader.read(key)
          object_details[index]=text
        elif name in ('car','truck','bus') and identity is not None:
          activity=road_reader.vehicle(key,crop,timestamp)
          if activity:
            vehicle_lamps.append((box,activity))
            object_details[index]=name+' '+', '.join(activity)
    for box in semantic_signs:
      key=f'sign:{round((box[0]+box[2])/64)}:{round((box[1]+box[3])/64)}'
      crops.append((key,box));text=road_reader.read(key)
      if show_boxes:
        cv2.rectangle(overlay,tuple(box[:2]),tuple(box[2:]),(0,220,255),2)
      if show_labels and text:
        sign_labels.append((box,text))
    if comma_scene:
      for box,text in road_reader.read_boxes():
        if show_boxes:
          cv2.rectangle(overlay,tuple(map(int,box[:2])),tuple(map(int,box[2:])),(0,220,255),2)
        if show_labels:
          sign_labels.append((box,text))
    road_reader.submit(image,crops,timestamp,full_frame=comma_scene)
  motions={}
  if history is not None and timestamp is not None:
    motions=draw_track_motion(overlay,tracked_boxes,history,timestamp,show_motion,object_names,distance_context)
  if distance_context is not None:
    if show_labels:
      draw_object_labels(overlay,object_boxes,object_names,*distance_context,details=object_details,extra_labels=sign_labels,radar_matches=radar_matches)
    if top_down is not None:
      sample,camera,geometry,layout,*extra=distance_context
      bumper_offset=extra[0] if extra else None
      top_down.update(bumper_offset=bumper_offset,lanes=(sample or {}).get('model',{}).get('laneLines',[]),
                      probabilities=(sample or {}).get('model',{}).get('laneLineProbs',[]),cars=[])
      if object_boxes is not None:
        ids=object_boxes.id.cpu().tolist() if object_boxes.id is not None else [None]*len(object_boxes)
        for box,cls,identity in zip(object_boxes.xyxy.cpu().numpy(),object_boxes.cls.cpu().tolist(),ids):
          name=object_names[int(cls)]
          if name not in ('car','truck','bus','motorcycle'):
            continue
          point=object_ground_position(box,image.shape,sample,camera,geometry,layout)
          if point is not None:
            top_down['cars'].append({'forward':float(point[0])-(bumper_offset or 0),'left':float(point[1]),'id':int(identity) if identity is not None else None,
                                     'type':name,'lane':object_lane(box,image.shape,sample,camera,geometry,layout),
                                     'heading':float(np.arctan2(-motions[int(identity)][1],motions[int(identity)][0])) if identity is not None and int(identity) in motions else None})
  if top_down is not None:
    top_down.update(traffic_light_summary(sensed_lights,light_bounds))
    top_down['signs']=[text for _,text in sign_labels]
    top_down['signs'] += [text for text in object_details.values() if 'STOP' in text.upper() or 'YIELD' in text.upper()]
  if lamp_overlays is not None:
    lamp_overlays.extend(vehicle_lamps)
  else:
    for box,activity in vehicle_lamps:
      draw_vehicle_lights(overlay,image,box,activity)
  return overlay, ' · '.join(descriptions)


def compose_sides(wide, driver, left_angle=0, right_angle=0, left_position=(0,0), right_position=(0,0), masks=None, return_exclusion=False):
  """Composite camera layers, revealing lower layers through side masks."""
  height = wide.shape[0]
  middle = driver.shape[1]//2
  panels,coverage = [],[]
  for panel,angle in ((driver[:,middle:],left_angle),(driver[:,:middle],right_angle)):
    h,w = panel.shape[:2]
    matrix = cv2.getRotationMatrix2D(((w-1)/2,(h-1)/2),angle,1)
    size = (round(w*height/h),height)
    panels.append(cv2.resize(cv2.warpAffine(panel,matrix,(w,h)),size))
    coverage.append(cv2.resize(cv2.warpAffine(np.ones((h,w),np.uint8),matrix,(w,h),flags=cv2.INTER_NEAREST),size,interpolation=cv2.INTER_NEAREST).astype(bool))
  left_width = panels[0].shape[1]
  canvas_width = left_width+wide.shape[1]+panels[1].shape[1]
  canvas = np.zeros((height,canvas_width,3),np.uint8)
  visible = np.zeros((height,canvas_width),bool)
  masks = masks or {}
  center = slice(left_width,left_width+wide.shape[1])
  canvas[:,center] = wide
  visible[:,center] = ~masks.get('center',np.zeros((height,canvas_width),bool))[:,center]
  for side,panel,coverage,base,position in zip(('left','right'),panels,coverage,(0,left_width+wide.shape[1]),(left_position,right_position)):
    x,y = base+round(position[0]*canvas_width),round(position[1]*height)
    x0,y0,x1,y1 = max(0,x),max(0,y),min(canvas_width,x+panel.shape[1]),min(height,y+height)
    if x1<=x0 or y1<=y0:
      continue
    target = canvas[y0:y1,x0:x1]
    underneath = visible[y0:y1,x0:x1]
    pixels = panel[y0-y:y1-y,x0-x:x1-x]
    covered = coverage[y0-y:y1-y,x0-x:x1-x]
    excluded = masks.get(side)
    valid = covered if excluded is None else covered & ~excluded[y0:y1,x0:x1]
    # Keep raw masked pixels only where there is no valid lower camera layer,
    # allowing Area opacity to reveal them without obscuring the center view.
    paint = valid | (covered & ~underneath)
    target[paint] = pixels[paint]
    underneath[valid] = True
  return (canvas,~visible) if return_exclusion else canvas


def side_matrix(geometry, side, layout):
  height,width,driver_height,left_native,right_native,wide_width = geometry
  native_width = left_native if side == 'left' else right_native
  panel_width = round(native_width*height/driver_height)
  base = 0 if side == 'left' else round(left_native*height/driver_height)+wide_width
  angle = layout.get('rotation', {}).get(side,0)
  position = layout.get('position', {}).get(side,[0,0])
  matrix = np.eye(3)
  matrix[:2] = cv2.getRotationMatrix2D(((native_width-1)/2,(driver_height-1)/2),angle,1)
  # Pixel-center resize mapping matches the camera compositor.
  resize = np.array([[panel_width/native_width,0,(panel_width/native_width-1)/2+base+round(position[0]*width)],
                     [0,height/driver_height,(height/driver_height-1)/2+round(position[1]*height)],[0,0,1]])
  return np.diag([1/(width-1),1/(height-1),1]) @ resize @ matrix @ np.diag([native_width-1,driver_height-1,1])


def move_side_areas(polygons, geometry, previous, current, sides=None):
  result = []
  for index,polygon in enumerate(polygons):
    points = np.column_stack((polygon,np.ones(len(polygon))))
    center = points.mean(axis=0)
    moved = points
    # Right panel is painted last, so it wins where panels overlap.
    for side in ([sides[index]] if sides is not None and sides[index] else [] if sides is not None else ('right','left')):
      inverse = np.linalg.inv(side_matrix(geometry,side,previous))
      local = inverse @ center
      if 0 <= local[0] <= 1 and 0 <= local[1] <= 1:
        moved = (side_matrix(geometry,side,current) @ inverse @ points.T).T
        break
    result.append(moved[:,:2].tolist())
  return result


def area_exclusion(height, width, polygons, keep_selected=False):
  mask = np.zeros((height,width),np.uint8)
  for polygon in polygons:
    vertices = np.rint(np.asarray(polygon)*[width-1,height-1]).astype(np.int32)
    cv2.fillPoly(mask,[vertices],1)
  return ~mask.astype(bool) if keep_selected else mask.astype(bool)


def match_replay_sample(samples, frame_id, camera):
  key='frameIdExtra' if camera in ('wideRoad','wideSides') else 'frameId'
  candidates=[s for s in samples if key in s.get('model',{})]
  if not candidates:
    return None
  sample=min(candidates,key=lambda s:abs(s['model'][key]-frame_id))
  return sample if abs(sample['model'][key]-frame_id)<=3 else None


def run(args):
  if not args.idle and not torch.backends.mps.is_available():
    raise RuntimeError('Apple Metal GPU unavailable')
  # Measured fastest on this Mac for both the GPU pipeline and CPU sign worker.
  torch.set_num_threads(1)
  args.command = 'web'
  args.custom_masks = True
  args.feature_selection = feature_selection
  args.camera_choices = ('road', 'wideRoad', 'driver', 'wideSides', 'qcam') if args.replay else ('road', 'wideRoad', 'driver', 'wideSides')
  road.MODELS = MODELS
  page = road.WEB_PAGE.replace('sunnydrive road segmentation', 'sunnydrive YOLO26').replace('Road segmentation', 'YOLO26').replace('Live road segmentation overlay', 'YOLO26 scene view')
  page = re.sub(r'(<select id="model" aria-label="Model">).*?(</select>)', lambda m: m[1]+''.join(f'<option value="{k}">{v}</option>' for k,v in MODELS.items())+m[2], page)
  page = page.replace('<select id="model" aria-label="Model">','<select id="model" aria-label="Model" hidden>')
  page = page.replace('</select><select id="camera"', '</select><select id="model-size" aria-label="Model size">'+''.join(f'<option value="{key}">{label}</option>' for key,label in SIZES.items())+'</select><label><input id="feature-objects" type="checkbox"> Objects</label><label><input id="feature-masks" type="checkbox"> Object masks</label><label><input id="feature-scene" type="checkbox"> Scene segmentation</label><select id="camera"',1)
  page = page.replace('<select id="camera"','<select id="segmentation-source" aria-label="Segmentation source"><option value="yolo">YOLO segmentation</option><option value="comma10k">comma10k segmentation</option></select><select id="camera"',1)
  page = page.replace('Segmentation opacity', 'Scene opacity')
  page = page.replace('Lane UI opacity', 'Area opacity')
  page = page.replace('const s=await r.json();', 'const s=await r.json();updateSideGeometry(s.side_geometry);updateObjectMode(s.object_mode);updateFeatures(s.requested_model||s.model,s.segmentation_source);')
  page = page.replace('<option value="wideRoad">Wide road camera</option>',
                      '<option value="wideRoad">Wide road camera</option><option value="driver">Driver camera</option><option value="wideSides">Wide + driver sides</option>')
  if args.replay:
    page=page.replace('<option value="road">Road camera</option>','<option value="road">Road camera</option><option value="qcam">Qcam · low resolution</option>')
  page = re.sub(r'const colors=s.model===.*?;\nif\(s.comma_overlay\)', "const colors=/^(scene|sceneMask|semantic)-/.test(s.model)?(s.segmentation_source==='comma10k'?[['Road','#3cc83c'],['Lane markings','#ffdc00'],['Vehicles / people','#f0aa14'],['Your car','#b450c8']]:[['Road','#3cc83c'],['Sky','#4baaea'],['Traffic signs','#fff000'],['Objects','#f0aa14']]):[];\nif(s.comma_overlay)", page)
  page = page.replace('> Comma overlay</label>','> Lane lines / edges</label>')
  page = page.replace('</style>', 'main{max-width:none;width:100%;padding:20px}.video{width:100%;min-height:0;max-height:none}</style>')
  page = page.replace('</style>', '.side-controls{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px;max-width:850px;margin-top:16px}.side-column{display:grid;gap:12px}.side-column label{display:grid;grid-template-columns:90px minmax(90px,1fr)48px;align-items:center;gap:10px}.side-column input{width:100%;padding:0;accent-color:#66e1a1}.side-column output{font-variant-numeric:tabular-nums}@media(max-width:600px){.side-controls{grid-template-columns:1fr}}</style>')
  page = page.replace('commaOverlay.checked=s.comma_overlay;',
                      'if(!laneToggleBusy)commaOverlay.checked=s.comma_overlay;if(s.video_width&&s.video_height)video.parentElement.style.aspectRatio=s.video_width+"/"+s.video_height;')
  page = page.replace('Loading segmentation model', 'Loading YOLO26 model')
  page = page.replace('</script>', Path(__file__).with_name('yolo_areas.js').read_text()+'\n'+Path(__file__).with_name('yolo_features.js').read_text()+'\n'+Path(__file__).with_name('yolo_top_down.js').read_text()+'\n</script>')
  if getattr(args, 'send_replay_key', None):
    page = page.replace('</script>', Path(__file__).with_name('yolo_replay.js').read_text()+'\n</script>')
  if args.replay:
    page = page.replace('Live comma camera · processing on your Mac', 'Comma replay · processing on your Mac')

  road.WEB_PAGE = page
  state, frames, changed, enabled, server = road.start_web(args)
  # Reuse the second slider's transport field for display-only area opacity.
  with changed:
    state['comma_opacity'] = 1.
    state['comma_overlay'] = True
    state['segmentation_source']=args.segmentation_source
  stop = threading.Event()
  condition = threading.Condition()
  latest = [None, 0]

  driver_latest = [None, 0, None]
  telemetry = [None,0,None]
  telemetry_history = []
  qcam_index=[None]

  def connection_status(message):
    with changed:
      state['connection_message']=message

  def receive_telemetry():
    while not stop.is_set():
      if args.idle:
        stop.wait(.2);continue
      source=args.comma
      try:
        if args.replay:
          root=Path(__file__).resolve().parents[2]
          sys.path[:0]=[str(root),str(root/'msgq_repo'),str(root/'opendbc_repo')]
          from openpilot.cereal import messaging
          from openpilot.sunnypilot.sunnydrive.sunnydrived import road_camera
          from yolo_radar import HyundaiReplayRadar
          can_socket=messaging.sub_sock('can')
          can_radar=HyundaiReplayRadar()
          sm=messaging.SubMaster(['modelV2','extrinsicsCalibration','deviceState','carState','radarTracks','qNarrowRoadEncodeIdx'])
          while not stop.is_set():
            sm.update(100)
            if sm.updated['qNarrowRoadEncodeIdx']:
              idx=sm['qNarrowRoadEncodeIdx']
              with condition:
                qcam_index[0]=(idx.segmentNum,idx.segmentId,idx.frameId)
                condition.notify_all()
            can_events=messaging.drain_sock(can_socket,wait_for_one=False)
            can_time=sm.logMonoTime['modelV2']/1e9
            decoded_can_radar=can_radar.update(can_events,can_time)
            if not all(sm.seen[key] for key in ('modelV2','extrinsicsCalibration','deviceState')) or not sm.updated['modelV2']:
              continue
            model,calib=sm['modelV2'],sm['extrinsicsCalibration']
            motion_time=sm.logMonoTime['modelV2']/1e9
            car=sm['carState']
            car_fresh=sm.seen['carState'] and abs(sm.logMonoTime['modelV2']-sm.logMonoTime['carState'])<300_000_000
            sample={'motionTime':motion_time,'car':{'speedMps':float(car.vEgo),'yawRateRps':float(car.yawRate)} if car_fresh else None,'model':{'frameId':model.frameId,'frameIdExtra':model.frameIdExtra,'laneLines':[{'x':list(p.x),'y':list(p.y),'z':list(p.z)} for p in model.laneLines],
                             'laneLineProbs':list(model.laneLineProbs),'roadEdges':[{'x':list(p.x),'y':list(p.y),'z':list(p.z)} for p in model.roadEdges],
                             'roadEdgeStds':list(model.roadEdgeStds),'path':{'x':list(model.position.x),'y':list(model.position.y),'z':list(model.position.z)}}}
            raw_tracks=decode_tracks(sm['radarTracks']) if sm.seen['radarTracks'] else None
            sample['radar']=radar_snapshot(raw_tracks,sm.logMonoTime['radarTracks']/1e9,motion_time)
            if not sample['radar']['tracks'] and decoded_can_radar['status']=='ready':
              sample['radar']=decoded_can_radar
            if len(calib.rpyCalib)==3 and len(calib.height):
              device=str(sm['deviceState'].deviceType)
              sample['roadCamera']=road_camera(device,tuple(calib.rpyCalib),calib.height[0])
              if len(calib.wideFromDeviceEuler)==3:
                sample['wideRoadCamera']=road_camera(device,tuple(calib.rpyCalib),calib.height[0],tuple(calib.wideFromDeviceEuler))
            with changed:
              state.pop('telemetry_error',None)
            with condition:
              telemetry[:]=[sample,time.monotonic(),source]
              telemetry_history.append(sample)
              del telemetry_history[:-100]
        else:
          token=road.token_for(source,args.token_file,connection_status)
          request=Request(source+'/telemetry/stream',headers={'Authorization':'Bearer '+token})
          with urlopen(request,timeout=15) as stream:
            for line in stream:
              if stop.is_set() or source!=args.comma:
                break
              if line.startswith(b'data: '):
                with condition:
                  telemetry[:]=[json.loads(line[6:]),time.monotonic(),source]
      except Exception as e:
        with changed:
          state['telemetry_error']=str(e)
        stop.wait(1)


  def camera_frames(source, feed, selection):
    if feed=='qcam':
      if not args.replay or not (args.route or args.demo):
        raise RuntimeError('Qcam requires a route launched by this viewer')
      from openpilot.tools.lib.route import RouteName
      from openpilot.tools.lib.api import CommaApi
      from urllib.parse import urlsplit
      route_name='/'.join(args.route.split('/')[:2]) if args.route else '/'.join(DEMO_ROUTE.split('/')[:2])
      # Replay's IPC namespace must not change the account used to fetch videos.
      try:
        token=json.loads(args.auth_file.read_text()).get('access_token')
      except (OSError,ValueError):
        token=None
      files=CommaApi(token).get('v1/route/'+RouteName(route_name).canonical_name+'/files')
      paths={}
      for urls in files.values():
        for url in urls:
          parts=urlsplit(url).path.rsplit('/',2)
          if parts[-1]=='qcamera.ts':paths[int(parts[-2])]=url
      container=None;segment=None;previous=None;decoder=None;decoded_pts=None
      try:
        while not stop.is_set() and selection==args.camera:
          with condition:
            index=qcam_index[0]
            if index is None or index==previous:
              condition.wait(.1);continue
          number,frame_index,frame_id=index
          if number!=segment:
            if container is not None:container.close()
            if number not in paths:
              raise RuntimeError(f'No Qcam recording for segment {number}')
            with changed:state.update(message='Loading Qcam recording…')
            with urlopen(paths[number],timeout=30) as response:
              container=av.open(io.BytesIO(response.read()))
            segment=number;decoder=None;decoded_pts=None
          stream=container.streams.video[0]
          target=(stream.start_time or 0)+round(frame_index/float(stream.average_rate)/float(stream.time_base))
          if decoder is None or decoded_pts is None or target<decoded_pts or target-decoded_pts>round(.5/float(stream.time_base)):
            container.seek(target,stream=stream,backward=True)
            decoder=container.decode(stream)
          for frame in decoder:
            if frame.pts is not None and frame.pts>=target:
              decoded_pts=frame.pts
              yield frame.to_ndarray(format='bgr24'),frame_id
              break
          previous=index
      finally:
        if container is not None:container.close()
      return
    if args.replay:
      sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'msgq_repo'))
      from msgq.visionipc import VisionIpcClient
      client = VisionIpcClient('camerad', {'road':0,'wideRoad':2,'driver':1}[feed], True)
      if not client.connect(False):
        raise RuntimeError('Start comma replay with --demo --wide-road --cabin in the same IPC namespace')
      last_frame = time.monotonic()
      while not stop.is_set() and selection == args.camera:
        buf = client.recv(1000)
        if buf is None:
          if time.monotonic()-last_frame>5:
            raise RuntimeError(f'No {feed} frames from replay. This segment may lack that camera video, or replay is paused. Select Road camera or resume replay.')
          continue
        last_frame = time.monotonic()
        data = np.frombuffer(buf.data, np.uint8)
        y = data[:buf.stride*buf.height].reshape(buf.height,buf.stride)[:,:buf.width]
        uv = data[buf.uv_offset:buf.uv_offset+buf.stride*(buf.height//2)].reshape(buf.height//2,buf.stride)[:,:buf.width]
        yield cv2.cvtColor(np.vstack((y,uv)),cv2.COLOR_YUV2BGR_NV12),client.frame_id
    else:
      token = road.token_for(source,args.token_file,connection_status)
      decoder = av.CodecContext.create('h264','r')
      request = Request(source+'/connect/live?cam='+feed,headers={'Authorization':'Bearer '+token})
      with urlopen(request,timeout=15) as stream:
        while not stop.is_set() and selection == args.camera and source == args.comma:
          length,_ = struct.unpack('>IB',road.read_exact(stream,5))
          if length > 16*1024*1024:
            raise ValueError('Invalid packet size')
          for packet in decoder.parse(road.read_exact(stream,length)):
            for frame in decoder.decode(packet):
              yield frame.to_ndarray(format='bgr24'),None

  def receive_driver():
    while not stop.is_set():
      if args.idle:
        stop.wait(.2);continue
      if args.camera != 'wideSides':
        stop.wait(.1)
        continue
      source = args.comma
      try:
        for image,_ in camera_frames(source,'driver','wideSides'):
          with condition:
            driver_latest[:] = [image,time.monotonic(),source]
      except Exception as e:
        with changed:
          state.update(ready=False,message=f'Waiting for driver side panels: {e}')
        stop.wait(1)

  def receive():
    while not stop.is_set():
      if args.idle:
        stop.wait(.2);continue
      camera, source = args.camera, args.comma
      try:
        for image,frame_id in camera_frames(source,'wideRoad' if camera == 'wideSides' else camera,camera):
          received = time.monotonic()
          if camera == 'wideSides':
            with condition:
              driver,driver_time,driver_source = driver_latest
            if driver is None or received-driver_time > 1 or driver_source != source:
              with changed:
                state.update(ready=False,message='Waiting for driver camera to build side panels…')
              continue
            with changed:
              rotation = state.get('side_rotation', {'left':0,'right':0})
              position = state.get('side_position', {'left':[0,0],'right':[0,0]})
            native_left,native_right = driver.shape[1]-driver.shape[1]//2,driver.shape[1]//2
            geometry = [image.shape[0],image.shape[1]+round(native_left*image.shape[0]/driver.shape[0])+round(native_right*image.shape[0]/driver.shape[0]),driver.shape[0],native_left,native_right,image.shape[1]]
            layout = {'rotation':rotation,'position':position}
            with changed:
              state['side_geometry'] = geometry

          with condition:
            if camera != args.camera or source != args.comma:
              continue
            latest[:] = [(image,received,camera,geometry if camera == 'wideSides' else None,driver if camera == 'wideSides' else None,frame_id),latest[1]+1]
            condition.notify()
      except Exception as e:
        with changed:
          if args.replay and str(e).startswith('No ') and 'frames from replay' in str(e):
            if latest[0] is None or latest[0][2]!=args.camera:
              state.update(ready=False,message='Waiting for camera frames…')
          else:
            state.update(ready=False,message=f'Waiting for input: {e}')
        stop.wait(1)

  threading.Thread(target=receive_telemetry,daemon=True).start()
  threading.Thread(target=receive,daemon=True).start()
  threading.Thread(target=receive_driver,daemon=True).start()
  models, active, version = [], None, 0
  active_source=None
  frozen, rendered_settings = None, None
  frozen_sample = None
  tracking_context = None
  radar_associator=RadarAssociator()
  inference_cache={}
  processing_fps=0.
  track_history = {}
  road_reader=RoadObjectReader(args.cache/'us-traffic-signs-yolo26s.pt')
  args.tracking_epoch = 0
  if getattr(args,'send_replay_key',None):
    replay_key = args.send_replay_key
    def tracked_replay_key(key):
      replay_key(key)
      if key in ('s','S','m','M'):
        args.tracking_epoch += 1
    args.send_replay_key = tracked_replay_key
  try:
    while True:
      if args.idle:
        stop.wait(.2);continue
      replay = getattr(args, 'replay_process', None)
      if replay is not None and replay.poll() is not None and not getattr(args,'switching_input',False):
        break
      if args.model != active or args.segmentation_source!=active_source:
        inference_cache.clear()
        results=None
        models.clear()
        gc.collect()
        torch.mps.synchronize()
        torch.mps.empty_cache()
        selected = args.model
        selected_source=args.segmentation_source
        with changed:
          state.update(ready=False,connection_message='',model='',message=f'Loading {MODELS[selected]}…')
        try:
          models = load(selected,args.cache,selected_source)
          active = selected
          active_source=selected_source
          with changed:
            state.update(message='Waiting for camera frames…')
        except Exception as e:
          with changed:
            state.update(message=f'Load failed: {e}. Choose another model.')
          # Wait for a new selection, keeping the picker usable.
          while args.model == selected and args.segmentation_source==selected_source and not stop.wait(.2):
            pass
          continue
      with condition:
        if args.replay and frozen is not None and frozen_sample is None:
          frozen_sample=match_replay_sample(telemetry_history,frozen[-1],args.camera)
      with changed:
        opacity, area_opacity = state['segmentation_opacity'], state['comma_opacity']
        polygons = state.get('blackout_areas', {}).get(args.camera, [])
        keep_selected = state.get('mask_modes', {}).get(args.camera, 'exclude') == 'keep'
        reference = state.get('mask_layouts', {}).get(args.camera)
        sides = state.get('mask_sides', {}).get(args.camera)
        layout = {'rotation':state.get('side_rotation', {'left':0,'right':0}),
                  'position':state.get('side_position', {'left':[0,0],'right':[0,0]})}
        lanes_enabled=state['comma_overlay']
        object_mode=state.get('object_mode','full')
        show_labels,show_boxes=state.get('show_labels',True),state.get('show_boxes',True)
        show_motion=state.get('show_motion',True)
        road_signals=state.get('road_signals',True)
        show_radar=state.get('show_radar',True)
        hide_stationary=state.get('hide_stationary',False)
        show_top_seg=state.get('show_top_seg',False)
        show_actions=state.get('show_actions',True)
        show_our_edges=state.get('show_our_edges',False)
        bumper_offset=state.get('bumper_offset')
        lane_width,lane_opacity=state.get('lane_width',3),state.get('lane_opacity',1.)
        settings = json.dumps([road_reader.revision,frozen_sample is not None,telemetry[0] is not None,lanes_enabled,lane_width,lane_opacity,bumper_offset,object_mode,show_labels,show_boxes,show_motion,road_signals,show_radar,hide_stationary,show_top_seg,show_actions,show_our_edges,args.tracking_epoch,active,active_source,args.camera,opacity,area_opacity,polygons,keep_selected,reference,sides,layout],sort_keys=True)
      with condition:
        if enabled.is_set() and latest[0] is not None and latest[1]!=version:
          frozen,version = latest
          frozen_sample = match_replay_sample(telemetry_history,frozen[-1],args.camera) if args.replay else telemetry[0] if telemetry[2]==args.comma and time.monotonic()-telemetry[1]<2 else None
        elif frozen is None or settings == rendered_settings:
          condition.wait(timeout=.1)
          continue
      image,received,camera,geometry,driver,frame_id = frozen
      with condition:
        if frozen_sample is None and args.replay:
          frozen_sample=match_replay_sample(telemetry_history,frame_id,camera)
        sample=frozen_sample
      if camera != args.camera:
        stop.wait(.1)
        continue
      context = json.dumps([active,active_source,camera,args.comma,args.tracking_epoch,layout,polygons,reference,sides,keep_selected],sort_keys=True)
      if context != tracking_context:
        track_history.clear()
        radar_associator.reset()
        road_reader.reset(context)
        for model in models:
          for tracker in getattr(getattr(model,'predictor',None),'trackers',[]):
            tracker.reset()
        if models:
          del model
        inference_cache.clear()
        tracking_context = context
      start = time.perf_counter()
      try:
        if camera == 'wideSides':
          if reference and geometry:
            polygons = move_side_areas(polygons,geometry,reference,layout,sides)
          # Masks belong to their camera layer, rather than covering the final composite.
          owners = sides
          if owners is None:
            owners = []
            for polygon in polygons:
              center = np.mean(polygon,axis=0)
              owner = None
              for side in ('right','left'):
                local = np.linalg.inv(side_matrix(geometry,side,layout)) @ [*center,1]
                if 0 <= local[0] <= 1 and 0 <= local[1] <= 1:
                  owner = side
                  break
              owners.append(owner)
          masks = {side:area_exclusion(geometry[0],geometry[1],[p for p,owner in zip(polygons,owners) if owner == name],keep_selected)
                   for side,name in (('left','left'),('right','right'),('center',None))}
          image,excluded = compose_sides(image,driver,layout['rotation']['left'],layout['rotation']['right'],layout['position']['left'],layout['position']['right'],masks,True)
        else:
          excluded = area_exclusion(*image.shape[:2],polygons,keep_selected)
        height,width = image.shape[:2]
        model_image = image.copy()
        model_image[excluded] = 0
        top_down={}
        lamp_overlays=[]
        inference_key=(version,context)
        reused=inference_cache.get('key')==inference_key
        inference_start=time.perf_counter()
        results=infer(models,model_image,args.imgsz,inference_cache,inference_key)
        inference_ms=(time.perf_counter()-inference_start)*1000
        render_start=time.perf_counter()
        raw_radar=(sample or {}).get('radar') or {}
        sensor_tracks=raw_radar.get('tracks',[]) if raw_radar.get('status')=='ready' else []
        objects=[]
        detection=next((result for task,result in results if task in ('detect','segment') and result.boxes is not None),None)
        if detection is not None and detection.boxes.id is not None and bumper_offset is not None:
          for box,cls,identity in zip(detection.boxes.xyxy.numpy(),detection.boxes.cls.tolist(),detection.boxes.id.tolist()):
            if detection.names[int(cls)] not in ('car','truck','bus','motorcycle','bicycle','person'):continue
            point=object_ground_position(box,image.shape,sample,camera,geometry,layout)
            if point is not None:
              objects.append(dict(id=int(identity),forward=float(point[0])-bumper_offset,left=float(point[1]),box=box.tolist()))
        radar_matches=radar_associator.update(objects,sensor_tracks,(sample or {}).get('motionTime',received))
        overlay,description = render(models,model_image,args.imgsz,opacity,track_history,received,(sample,camera,geometry,layout,bumper_offset),top_down,object_mode,show_labels,show_boxes,show_motion,road_reader if road_signals else None,lamp_overlays,results,radar_matches)
        lane_drawn=False
        if lanes_enabled and sample and camera in ('road','wideRoad','wideSides','qcam'):
          if camera=='wideSides':
            left=round(geometry[3]*geometry[0]/geometry[2])
            layer=overlay[:,left:left+geometry[5]].copy()
            lane_drawn=road.draw_comma_overlay(layer,sample,'wideRoad',lane_opacity,lane_width)
            # Only the center-owned pixels receive the projected road overlay.
            valid=np.ones(layer.shape[:2],bool)
            yy,xx=np.mgrid[:geometry[0],left:left+geometry[5]]
            points=np.stack((xx/(geometry[1]-1),yy/(geometry[0]-1),np.ones_like(xx)),axis=-1)
            for side in ('left','right'):
              local=points @ np.linalg.inv(side_matrix(geometry,side,layout)).T
              valid &= ~((local[:,:,0]>=0)&(local[:,:,0]<=1)&(local[:,:,1]>=0)&(local[:,:,1]<=1))
            center=overlay[:,left:left+geometry[5]];center[valid]=layer[valid]
          else:
            lane_drawn=road.draw_comma_overlay(overlay,sample,'road' if camera=='qcam' else camera,lane_opacity,lane_width)
        ground=None
        if show_top_seg or show_actions or show_our_edges:
          segmentation,ground=top_down_segmentation(results,image.shape,sample,camera,geometry,layout,bumper_offset,excluded,True,image)
          if show_top_seg:top_down['segmentation']=segmentation
        for car in top_down.get('cars',[]):
          match=radar_matches.get(car['id'])
          if match:
            track=match['track']
            car.update(vision_forward=car['forward'],vision_left=car['left'],forward=track['forward'],left=track['left'],relative_speed=track['relative_speed'],source='vision+radar')
        if show_our_edges:
          top_down['our_edges']=[]
          selected=next(((task,result) for task,result in results if task in ('semantic','comma10k')),None)
          if selected:
            task,result=selected
            labels=result.semantic_mask.data.cpu().numpy().astype(np.uint8)
            small_excluded=cv2.resize(excluded.astype(np.uint8),labels.shape[::-1],interpolation=cv2.INTER_NEAREST).astype(bool)
            edges=road_boundaries(labels,small_excluded,1 if task=='comma10k' else None)
            scale=np.array([width/labels.shape[1],height/labels.shape[0]])
            calibration=(sample or {}).get('wideRoadCamera' if camera in ('wideRoad','wideSides') else 'roadCamera')
            for edge in edges:
              pixels=np.asarray(edge)*scale
              cv2.polylines(overlay,[np.rint(pixels).astype(np.int32)],False,(220,220,0),2,cv2.LINE_AA)
              if calibration and camera in ('road','wideRoad','qcam') and bumper_offset is not None:
                native=pixels*np.array([calibration['width']/width,calibration['height']/height])
                projected=np.column_stack((native,np.ones(len(native)))) @ np.linalg.inv(np.asarray(calibration['ground']).reshape(3,3)).T
                valid=abs(projected[:,2])>1e-6
                points=projected[:,:2]/np.where(valid,projected[:,2],1)[:,None]
                points[:,0]-=bumper_offset
                valid &= (points[:,0]>=0)&(points[:,0]<=70)&(abs(points[:,1])<=20)&np.isfinite(points).all(axis=1)
                ids=np.flatnonzero(valid)
                for group in np.split(ids,np.flatnonzero(np.diff(ids)>1)+1):
                  if len(group)>=2:top_down['our_edges'].append(points[group].tolist())
        if show_actions:
          top_down['action_preview']=action_preview(top_down,sample,ground)
          if ground is None:
            if not any(task in ('semantic','comma10k') for task,_ in results):
              top_down['action_preview']['path_status']='segmentation_off'
            elif bumper_offset is None:
              top_down['action_preview']['path_status']='bumper_offset_missing'
            elif not (sample or {}).get('wideRoadCamera' if camera in ('wideRoad','wideSides') else 'roadCamera'):
              top_down['action_preview']['path_status']='calibration_missing'
          top_down['action_preview']['show_paths']=show_our_edges
          for path in top_down['action_preview']['paths'] if show_our_edges else []:
            points=np.array(path['points'])
            pixels=project_ground_points(points+np.array([bumper_offset or 0,0]),image.shape,sample,camera,geometry)
            if pixels is None:continue
            pixels=np.rint(np.clip(pixels,[-width,-height],[width*2,height*2])).astype(np.int32)
            color=(0,130,255) if path['blocked'] else (255,200,60)
            if path.get('selected'):
              # A 1.8 m preview footprint: green nearby, cyan farther ahead.
              normals=np.column_stack((-np.gradient(points[:,1]),np.gradient(points[:,0])))
              normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-6)
              edges=[project_ground_points(points+normals*side+np.array([bumper_offset or 0,0]),image.shape,sample,camera,geometry) for side in (-.9,.9)]
              if all(edge is not None for edge in edges):
                layer=overlay.copy()
                for i in range(len(points)-1):
                  t=i/max(1,len(points)-2)
                  shade=(int(80+175*t),int(225-35*t),int(65+10*t))
                  polygon=np.array([edges[0][i],edges[0][i+1],edges[1][i+1],edges[1][i]])
                  polygon=np.rint(np.clip(polygon,[-width,-height],[width*2,height*2])).astype(np.int32)
                  cv2.fillConvexPoly(layer,polygon,shade,cv2.LINE_AA)
                  cv2.line(overlay,tuple(pixels[i]),tuple(pixels[i+1]),shade,4,cv2.LINE_AA)
                cv2.addWeighted(layer,.3,overlay,.7,0,overlay)
                cv2.circle(overlay,tuple(pixels[0]),7,(80,225,65),-1,cv2.LINE_AA)
            else:
              for i in range(0,len(pixels)-1,3):cv2.polylines(overlay,[pixels[i:i+2]],False,color,3,cv2.LINE_AA)
        scene=scene_snapshot(sample,top_down,(sample or {}).get('motionTime',received))
        scene['action_preview']=top_down.get('action_preview')
        scene['radar_associations']=[dict(object_id=i,radar_id=m['track']['id'],source_bus=m['track']['bus'],source_address=m['track']['address'],cost=m['cost']) for i,m in radar_matches.items()]
        visible_tracks=[track for track in scene['sensor_tracks'] if not (hide_stationary and track['motion_state']==1)]
        top_down['radar']=visible_tracks if show_radar else []
        top_down['radar_status']=scene['radar_status']
        if show_radar:
          draw_radar_overlay(overlay,sample,camera,geometry,bumper_offset,visible_tracks,radar_matches)
        for box,activity in lamp_overlays:
          draw_vehicle_lights(overlay,model_image,box,activity)
        overlay[excluded] = 0 if object_mode!="full" else (image[excluded]*(1-area_opacity)).astype(np.uint8)
      except Exception as e:
        with changed:
          state.update(ready=False,message=f'Inference failed: {e}. Choose another model.')
        while args.model == active and args.segmentation_source==active_source and not stop.wait(.2):
          pass
        continue
      if args.model != active or args.segmentation_source!=active_source or camera != args.camera:
        continue
      rendered_settings = settings
      render_ms=(time.perf_counter()-render_start)*1000
      cv2.putText(overlay,f'{MODELS[active]} | {processing_fps:.1f} FPS',(15,32),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,255,255),2)
      encode_start=time.perf_counter()
      ok,jpeg = cv2.imencode('.jpg',overlay,[cv2.IMWRITE_JPEG_QUALITY,85])
      encode_ms=(time.perf_counter()-encode_start)*1000
      elapsed=time.perf_counter()-start
      if not reused:
        processing_fps=1/elapsed
      if not ok:
        raise RuntimeError('JPEG encode failed')
      with changed:
        frames[:] = [jpeg.tobytes(),frames[1]+1]
        state.update(connection_message='',scene=scene,segmentation_source=active_source,sign_model_error=road_reader.error,top_down=top_down,lane_projection="calibrated 3D" if sample and "modelProjection" in (sample.get("roadCamera") or {}) else "ground fallback",camera_frame_id=frame_id,model_frame_id=sample["model"].get("frameId") if sample else None,comma_overlay_ready=lane_drawn,model=active,ready=True,video_width=width,video_height=height,fps=round(processing_fps,1),inference_ms=round(inference_ms,1),render_ms=round(render_ms,1),encode_ms=round(encode_ms,1),processing_ms=round(elapsed*1000,1),inference_reused=reused,age_ms=round((time.monotonic()-received)*1000),message=('Paused · ' if not enabled.is_set() else 'Replay · ' if args.replay else 'Live · ')+('Driver left | Wide | Driver right · Unaligned camera views · ' if camera == 'wideSides' else '')+description)
        changed.notify_all()
  finally:
    stop.set()
    road_reader.close()
    server.shutdown()
    server.server_close()


def replay_command(root, route=None, start=None):
  command=[str(root/'openpilot/tools/replay/replay')]
  command += [route or DEMO_ROUTE]
  command += ['--start',str(start if start is not None else 0),'--wide-road','--cabin',
              '--allow','can,qNarrowRoadEncodeIdx,narrowRoadCameraState,wideRoadCameraState,narrowRoadEncodeIdx,wideRoadEncodeIdx,cabinCameraState,cabinEncodeIdx,modelV2,extrinsicsCalibration,deviceState,carState,radarTracks']
  return command


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  source = parser.add_mutually_exclusive_group()
  source.add_argument('route',nargs='?',help='Replay route or segment, e.g. dongle/route/6')
  source.add_argument('--replay',action='store_true',help='Attach to an existing local replay')
  source.add_argument('--demo',action='store_true',help='Launch the public comma demo replay locally')
  parser.add_argument('--replay-route',help=argparse.SUPPRESS)
  parser.add_argument('--comma',help='Connect to a live sunnydrive server')
  parser.add_argument('--start',type=int,help='Start offset in seconds (demo defaults to 120; routes to 0)')
  parser.add_argument('--camera',choices=['road','wideRoad','driver','wideSides','qcam'])
  parser.add_argument('--model',choices=list(MODELS))
  parser.add_argument('--segmentation-source',choices=['yolo','comma10k'])
  parser.add_argument('--settings-file',type=Path,default=Path.home()/'.config/sunnydrive/yolo-viewer.json')
  parser.add_argument('--imgsz',type=int,default=640)
  parser.add_argument('--port',type=int,default=8768)
  parser.add_argument('--token-file',type=Path,default=Path.home()/'.config/sunnydrive/roadseg-tokens.json')
  parser.add_argument('--cache',type=Path,default=Path.home()/'.cache/sunnydrive/yolo26')
  parser.add_argument('--no-open',action='store_true')
  args=parser.parse_args()
  args.idle=not any((args.route,args.replay,args.comma,args.demo))
  args.comma=args.comma or 'http://10.83.106.109:8766'
  if args.start is not None and args.start<0:
    parser.error('start must be nonnegative')
  if args.imgsz<=0:
    parser.error('imgsz must be positive')
  args.viewer_lock = road.acquire_viewer_lock()
  restore_selection(args)
  save_selection(args)
  args.save_selection = lambda: save_selection(args)
  args.cache.mkdir(parents=True,exist_ok=True)
  original_prefix=os.environ.get('OPENPILOT_PREFIX')
  args.auth_file=Path.home()/('.comma'+os.environ.get('OPENPILOT_PREFIX',''))/'auth.json'
  replay = None
  close_console = None
  if args.demo or args.route:
    root = Path(__file__).resolve().parents[2]
    os.environ['OPENPILOT_PREFIX'] = f'yolo-demo-{os.getpid()}'
    Path('/tmp/msgq_'+os.environ['OPENPILOT_PREFIX']).mkdir(exist_ok=True)
    env = dict(os.environ, PATH=str(root/'.venv/bin')+os.pathsep+os.environ['PATH'])
    replay,args.send_replay_key,close_console = replay_console(replay_command(root,args.route,args.start),root,env)
    args.replay_process = replay
    args.get_replay_paused=lambda: replay.viewer_replay_state["paused"]
    args.replay = True
  def switch_input(mode):
    # Suppress the replay-exit handler until this process is replaced.
    args.switching_input=True
    if replay is not None:
      replay.terminate()
      try:replay.wait(timeout=3)
      except subprocess.TimeoutExpired:
        replay.kill();replay.wait()
    if close_console is not None:close_console()
    route=args.route or args.replay_route
    command=[sys.executable,str(Path(__file__).resolve()),'--cache',str(args.cache),
             '--port',str(args.port),'--settings-file',str(args.settings_file),
             '--token-file',str(args.token_file),'--imgsz',str(args.imgsz),'--no-open']
    if route:command += ['--replay-route',route]
    if mode=='live':
      if args.comma=='http://10.83.106.109:8766':
        try:
          with socket.create_connection(('10.83.106.109',8766),timeout=.7):pass
        except OSError:
          args.comma='http://100.100.139.123:8766'
      command += ['--comma',args.comma]
      if args.camera=='qcam':command += ['--camera','road']
    else:
      command += [route or DEMO_ROUTE]
      command += ['--comma',args.comma]
    if original_prefix is None:os.environ.pop('OPENPILOT_PREFIX',None)
    else:os.environ['OPENPILOT_PREFIX']=original_prefix
    os.execv(sys.executable,command)
  args.switch_input=switch_input
  try:
    run(args)
  except KeyboardInterrupt:
    pass
  finally:
    if replay is not None:
      replay.terminate()
      try:
        replay.wait(timeout=5)
      except subprocess.TimeoutExpired:
        replay.kill()
        replay.wait()
    if close_console is not None:
      close_console()


if __name__=='__main__':
  main()
