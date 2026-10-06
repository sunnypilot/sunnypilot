"""Observational action hypotheses. No actuator or vehicle-control interface."""
import math
import cv2
import numpy as np


def corridor_samples(points,ground):
  """Sample a 1.8 m footprint; unknown pixels provide no road evidence."""
  if ground is None:return np.array([],np.int8)
  points=np.asarray(points,float)
  points=points[points[:,0]>=5]
  if len(points)<2:return np.array([],np.int8)
  delta=np.gradient(points,axis=0)
  normal=np.column_stack((-delta[:,1],delta[:,0]))
  normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-6)
  footprint=(points[:,None,:]+normal[:,None,:]*np.array([-.9,0,.9])[None,:,None]).reshape(-1,2)
  rows=np.rint((70-footprint[:,0])*2).astype(int);cols=np.rint((20-footprint[:,1])*2).astype(int)
  valid=(rows>=0)&(rows<141)&(cols>=0)&(cols<81)
  samples=np.full(len(rows),-1,np.int8)
  samples[valid]=ground[rows[valid],cols[valid]]
  return samples


def corridor_support(points,ground):
  samples=corridor_samples(points,ground)
  return float(np.isin(samples,[1,2]).mean()) if len(samples) else 0.


def clearance(points,objects):
  return min((float(np.linalg.norm(np.asarray(points)-[obj['forward'],obj['left']],axis=1).min())
              for obj in objects if obj['forward']>=0),default=100.)


def blocked(points,objects):
  return clearance(points,objects)<2.


def action_preview(scene,sample,ground):
  paths=[]
  forward=np.linspace(3,30,40)
  candidates=[]
  proposals=[np.column_stack((forward,shift*(forward/30)**2)) for shift in np.linspace(-6,6,13)]
  bounds=scene.get('our_edges',[])
  for first in bounds:
    for second in bounds:
      a=np.asarray(first);b=np.asarray(second)
      if len(a)<2 or len(b)<2:continue
      a=a[np.argsort(a[:,0])];b=b[np.argsort(b[:,0])]
      start=max(3.,a[0,0],b[0,0]);end=min(30.,a[-1,0],b[-1,0])
      if start>8 or end-start<10:continue
      x=np.linspace(start,end,40)
      left=np.interp(x,a[:,0],a[:,1]);right=np.interp(x,b[:,0],b[:,1])
      if not np.all((left-right>1.8)&(left-right<10)):continue
      proposals.append(np.column_stack((x,(left+right)*.5)))
  for points in proposals:
    shift=points[-1,1]
    support=corridor_support(points,ground)
    if support>=.85:
      gap=clearance(points,scene.get('cars',[]))
      separator=float((corridor_samples(points,ground)==2).mean())
      # Collision avoidance outranks separator preference; unknown ground never counts as road.
      score=(gap>=2.,gap if gap<2 else support-separator*.35+min(gap,6)*.03-abs(shift)*.005)
      candidates.append((score,points))
  if candidates:
    straight=max(candidates,key=lambda item:item[0])[1]
    paths.append(dict(direction='straight',points=straight.tolist(),blocked=blocked(straight,scene.get('cars',[]))))
  # A geometric turn is evidence of an opening, not intersection topology or permission.
  for direction,sign in (('left',1),('right',-1)):
    best=None
    for junction in range(5,31):
      for radius in (3,4,6,9,12):
        if ground is None:continue
        # Reject a uniformly wide road: require observed non-road before the opening.
        rows=np.rint((70-np.array([junction-4,junction-3,junction-2]))*2).astype(int)
        columns=np.rint((20-sign*np.linspace(3,radius+2,6))*2).astype(int)
        if not np.any((ground[rows[:,None],columns[None,:]]==0).sum(axis=0)>=2):continue
        angle=np.linspace(0,math.pi/2,25)
        turn=np.column_stack((junction+radius*np.sin(angle),sign*radius*(1-np.cos(angle))))
        approach=np.column_stack((np.linspace(3,junction,20),np.zeros(20)))
        if corridor_support(approach,ground)<.92:continue
        # Keep only the contiguous observed-road footprint, never bridge unseen ground.
        samples=corridor_samples(turn,ground).reshape(-1,3)
        unsupported=np.flatnonzero(~np.isin(samples,[1,2]).all(axis=1))
        count=int(unsupported[0]) if len(unsupported) else len(turn)
        if count<2 or angle[count-1]<math.radians(40) or abs(turn[count-1,1])<2.5:continue
        points=np.vstack((approach,turn[1:count]))
        partial=count<len(turn)
        if not partial:
          exit_points=np.column_stack((np.full(8,junction+radius),sign*np.linspace(radius,radius+3,8)))
          partial=corridor_support(exit_points,ground)<.9
        # Prefer the nearest supported opening, rather than a longer arc farther ahead.
        score=(not blocked(points,scene.get('cars',[])),-junction,not partial,angle[count-1],-radius)
        if best is None or score>best[0]:best=(score,points,partial)
    if best is not None:
      points=best[1]
      paths.append(dict(direction=direction,points=points.tolist(),partial=best[2],blocked=blocked(points,scene.get('cars',[]))))
  for path in paths:
    path['selected']=path['direction']=='straight' and not path['blocked']
  lights=scene.get('lights',[]);dominant=scene.get('dominant_light')
  signs=scene.get('signs',[])
  stop_sign=any(sign.upper() in ('STOP','STOP SIGN') for sign in signs)
  yield_sign=any(sign.upper() in ('YIELD','YIELD SIGN') for sign in signs)
  for path in paths:
    forbidden=any(sign.upper() in ('NO '+path['direction'].upper()+' TURN','NO TURN '+path['direction'].upper()) for sign in signs)
    if forbidden:path.update(blocked=True,selected=False,reason='prohibitory sign observed')
  red=dominant=='red' or (dominant=='mixed' and 'red' in lights)
  caution=dominant in ('yellow','mixed') or yield_sign
  obstacle=any(p['blocked'] for p in paths if p['direction']=='straight')
  speed=((sample or {}).get('car') or {}).get('speedMps')
  stopped=speed is not None and speed<.3
  must_stop=red or stop_sign or obstacle
  reason='red light observed' if red else 'stop sign observed' if stop_sign else 'object in corridor' if obstacle else 'yellow / mixed signal or yield sign' if caution else 'green light observed' if dominant=='green' else 'signal / right of way unknown'
  primary=('hold' if stopped else 'stop') if must_stop else 'brake' if caution else 'go?'
  go=not must_stop and not caution
  actions=[dict(name='Gas',state='candidate' if go else 'unknown'),
           dict(name='Brake',state='candidate' if not stopped and (must_stop or caution) else 'inactive'),
           dict(name='Stop',state='candidate' if must_stop else 'inactive'),
           dict(name='Go',state='candidate' if go else 'unknown')]
  return dict(primary=primary,reason=reason,actions=actions,paths=paths,
              path_status='ready' if paths else 'ground_unavailable' if ground is None else 'no_supported_corridor',
              status='unverified',right_of_way='unknown',cross_traffic='unknown',control_ready=False)


def road_boundaries(labels,excluded,lane_class=None):
  """Open image-space sides of the ego road, excluding segmented obstacles."""
  height,width=labels.shape
  # Work at native segmentation resolution; preserve masks and painted dividers.
  free=(labels==0)&~excluded
  if lane_class is not None:
    paint=(labels==lane_class).astype(np.uint8)
    paint=cv2.morphologyEx(paint,cv2.MORPH_CLOSE,np.ones((9,3),np.uint8))
    free &= ~paint.astype(bool)
  free=cv2.morphologyEx(free.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8)).astype(bool)
  traces=[[],[]];paint_trace=[];center=width*.5
  for row in range(height-2,height//3,-1):
    columns=np.flatnonzero(free[row])
    if not len(columns):continue
    runs=np.split(columns,np.flatnonzero(np.diff(columns)>1)+1)
    runs=[run for run in runs if len(run)>=max(3,width//100)]
    if not runs:continue
    run=min(runs,key=lambda r:abs(np.clip(center,r[0],r[-1])-center))
    if abs(np.clip(center,run[0],run[-1])-center)>width*.12:continue
    center=.8*center+.2*(run[0]+run[-1])/2
    if lane_class is not None:
      lane_cols=np.flatnonzero((labels[row]==lane_class)&(np.arange(width)<center))
      if len(lane_cols) and (labels[row]==lane_class).sum()<width*.15:
        paint_trace.append((float(lane_cols[-1]+1),float(row)))
    for side,col in enumerate((run[0],run[-1])):
      if 1<col<width-2 and not excluded[row,col]:traces[side].append((float(col),float(row)))
  if len(paint_trace)>=12:traces[0]=paint_trace
  edges=[]
  for side,trace in enumerate(traces):
    if len(trace)<8:continue
    points=np.asarray(trace);x,y=points.T
    # Remove paint-gap excursions; preserve genuine intersection discontinuities.
    median=np.median(np.lib.stride_tricks.sliding_window_view(np.pad(x,(7,7),mode='edge'),15),axis=1)
    good=abs(x-median)<width*.035
    discontinuity=(abs(np.diff(median))>width*.04)
    if not (side==0 and len(paint_trace)>=12):discontinuity |= abs(np.diff(y))>3
    splits=np.flatnonzero(discontinuity)+1
    for ids in np.split(np.arange(len(points)),splits):
      ids=ids[good[ids]]
      if len(ids)<8:continue
      p=points[ids].copy();v=median[ids]
      dense_y=np.arange(p[-1,1],p[0,1]+1)[::-1]
      dense_x=np.interp(dense_y,p[::-1,1],v[::-1])
      p=np.column_stack((dense_x,dense_y));v=dense_x
      p[:,0]=np.convolve(np.pad(v,(2,2),mode='edge'),np.ones(5)/5,mode='valid')
      # Each segment is open; never wrap around a marking or a parked car.
      edges.append(p.tolist())
  return edges
