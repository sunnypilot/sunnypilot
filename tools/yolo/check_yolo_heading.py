"""Check ego-compensated motion, including turns and replay time scaling."""
import numpy as np
from yolo_motion import compensated_motion


def samples_for(world_velocity=(0.,0.),speed=10.,yaw=0.):
  rows=[]
  for t in np.linspace(0,1.5,20):
    theta=yaw*t
    ego=np.array([speed*t,0.]) if yaw==0 else np.array([speed*np.sin(theta)/yaw,speed*(1-np.cos(theta))/yaw])
    world=np.array([35.,4.])+np.array(world_velocity)*t
    delta=world-ego
    c,s=np.cos(theta),np.sin(theta)
    relative=np.array([c*delta[0]+s*delta[1],-s*delta[0]+c*delta[1]])
    rows.append((t,*relative,speed,yaw))
  return rows

for yaw in (0.,.2,-.2):
  points,velocity=compensated_motion(samples_for(yaw=yaw))
  assert np.linalg.norm(velocity)<1e-8,(yaw,velocity)
  assert np.allclose(points,points[-1])
  _,velocity=compensated_motion(samples_for((2.,1.),yaw=yaw))
  theta=yaw*1.5;c,s=np.cos(theta),np.sin(theta)
  assert np.allclose(velocity,[c*2+s,-s*2+c])
# Accelerating ego, stationary object; trapezoidal speed integration is exact here.
rows=[(t,35.-(5*t+t*t),4.,5+2*t,0.) for t in np.linspace(0,1.5,20)]
assert np.linalg.norm(compensated_motion(rows)[1])<1e-8
assert compensated_motion([]) is None
assert compensated_motion([(1,30,0,10,0),(1,30,0,10,0)]) is None
assert compensated_motion([(1,30,0,10,0),(0,30,0,10,0)]) is None
assert compensated_motion([(0,30,0,10,0),(1,20,0,float('nan'),0)]) is None
print('Motion: stationary/ moving objects, left/right turns, acceleration and invalid time passed')

# Exercise the viewer path: a stationary car must produce no painted trail.
import ast
from pathlib import Path
from types import SimpleNamespace
import cv2
source=ast.parse(Path(__file__).with_name('yolo_viewer.py').read_text())
helper=next(node for node in source.body if isinstance(node,ast.FunctionDef) and node.name=='draw_track_motion')
class Tensor:
  def __init__(self,value):self.value=np.asarray(value)
  def cpu(self):return self
  def numpy(self):return self.value
  def tolist(self):return self.value.tolist()
namespace={'np':np,'cv2':cv2,'compensated_motion':compensated_motion,
 'object_ground_position':lambda box,*args:np.asarray(box[:2]),
 'project_ground_points':lambda points,*args:np.asarray(points)+[0,30]}
exec(compile(ast.Module(body=[helper],type_ignores=[]),'draw-motion','exec'),namespace)
draw=namespace['draw_track_motion'];history={};image=np.zeros((100,100,3),np.uint8)
sample={'car':{'speedMps':10.,'yawRateRps':0.}}
for t in np.linspace(0,1,15):
 sample['motionTime']=float(t)
 boxes=SimpleNamespace(id=Tensor([1]),cls=Tensor([0]),xyxy=Tensor([[35-10*t,4,40,8]]))
 assert draw(image,boxes,history,100+t,True,{0:'car'},(sample,'road',None,None))=={}
assert not image.any()
count=len(history[1]);draw(image,boxes,history,101,True,{0:'car'},(sample,'road',None,None))
assert len(history[1])==count
sample['car']={}
assert draw(image,boxes,history,101,True,{0:'car'},(sample,'road',None,None))=={} and not history
print('Viewer: stationary trails suppressed, paused redraw unchanged, missing speed clears history')
