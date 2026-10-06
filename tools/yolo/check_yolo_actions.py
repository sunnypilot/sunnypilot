"""Regression checks for observational actions and grounded turn candidates."""
import numpy as np
from yolo_actions import action_preview

forward,left=np.meshgrid(np.linspace(70,0,141),np.linspace(20,-20,81),indexing='ij')
road=np.zeros((141,81),np.int8);road[np.abs(left)<2]=1
sample={'car':{'speedMps':8}}
scene={'bumper_offset':2,'cars':[],'lights':['red'],'dominant_light':'red','signs':[]}
preview=action_preview(scene,sample,road)
assert preview['primary']=='stop' and not preview['control_ready']
assert [p['direction'] for p in preview['paths']]==['straight']
assert action_preview(scene,{'car':{'speedMps':0}},road)['primary']=='hold'
scene.update(lights=['green'],dominant_light='green')
assert action_preview(scene,sample,road)['primary']=='go?'
assert action_preview(scene,sample,None)['primary']=='go?'
scene['signs']=['STOP']
assert action_preview(scene,sample,road)['primary']=='stop'
scene['signs']=['YIELD']
assert action_preview(scene,sample,road)['primary']=='brake'
scene['signs']=[]
unknown=np.full((141,81),-1,np.int8)
assert not action_preview(scene,sample,unknown)['paths']
assert [p['direction'] for p in action_preview(scene,sample,np.ones_like(road))['paths']]==['straight']
right=road.copy();right[(forward>=8)&(forward<=24)&(left<=0)]=1
paths=action_preview(scene,sample,right)['paths']
assert 'right' in [p['direction'] for p in paths] and 'left' not in [p['direction'] for p in paths]
turn=next(p for p in paths if p['direction']=='right')
assert turn['points'][-1][1]<0
left_turn=road.copy();left_turn[(forward>=8)&(forward<=24)&(left>=0)]=1
assert 'left' in [p['direction'] for p in action_preview(scene,sample,left_turn)['paths']]
scene['cars']=[{'forward':12,'left':0}]
assert action_preview(scene,sample,road)['primary']=='stop'
scene.update(cars=[],lights=[],dominant_light=None)
assert action_preview(scene,sample,road)['primary']=='go?'
print('Action preview: lights, stop/yield signs, obstacles, unknown coverage, straight road and left/right openings passed')

scene.update(signs=['NO RIGHT TURN'],dominant_light='green',lights=['green'])
assert next(p for p in action_preview(scene,sample,right)['paths'] if p['direction']=='right')['blocked']
scene['signs']=['NO STOPPING']
assert action_preview(scene,sample,road)['primary']=='go?'

scene.update(cars=[],signs=[])
first=action_preview(scene,sample,right)['paths']
second=action_preview(scene,dict(sample,model={'path':{'x':[10,20,30],'y':[100,100,100]}}),right)['paths']
assert first==second
print('Candidate paths are independent of comma model trajectories')

# A clear road alternative beats a collision, even near a yellow separator.
broad=np.ones_like(road)
scene.update(cars=[{'forward':24,'left':0}],signs=[],dominant_light='green',lights=['green'])
path=action_preview(scene,sample,broad)['paths'][0]
assert not path['blocked'] and abs(path['points'][-1][1])>2
marked=broad.copy();marked[(abs(left)>=2)&(abs(left)<=4)]=2
path=action_preview(scene,sample,marked)['paths'][0]
assert not path['blocked']
# With no obstacle, prefer remaining inside the separators.
scene['cars']=[]
path=action_preview(scene,sample,marked)['paths'][0]
assert abs(path['points'][-1][1])<2
print('Road-only candidate ranking: collision avoidance first, yellow separator preference second')

assert path['selected']
scene['cars']=[{'forward':12,'left':0}]
assert not action_preview(scene,sample,road)['paths'][0]['selected']

# A visible opening ending at unknown ground yields a truncated possible turn.
scene.update(cars=[],signs=[])
limited=road.copy();limited[(forward>=12)&(forward<=24)&(left<=0)]=1;limited[forward>17]=-1
preview=action_preview(scene,sample,limited)
turn=next(p for p in preview['paths'] if p['direction']=='right')
assert turn['partial'] and max(p[0] for p in turn['points'])<=17.25
assert abs(turn['points'][-1][1])>=2.5
assert not action_preview(scene,sample,np.full_like(road,-1))['paths']
print('Partial turn stops at visible road; unknown ground is never bridged')

# The nearby opening wins even when another, longer bend fits farther ahead.
opening=road.copy();opening[(forward>=8)&(forward<=17)&(left<=0)]=1
turn=next(p for p in action_preview(scene,sample,opening)['paths'] if p['direction']=='right')
first_bend=next(p for p in turn['points'] if abs(p[1])>.1)
assert first_bend[0]<12
assert max(p[0] for p in turn['points'])<18
print('Turn previews prefer the near segmented opening, with tighter bend candidates')


from yolo_actions import road_boundaries
labels=np.full((180,320),2,np.uint8)
labels[60:170,70:260]=0
labels[60:170,100:103]=1
labels[90:105,100:103]=0
labels[100:135,225:260]=3
edges=road_boundaries(labels,np.zeros_like(labels,bool),1)
assert len(edges)>=2
left_edge=min(edges,key=lambda e:np.median(np.asarray(e)[:,0]))
assert max(p[0] for p in left_edge)-min(p[0] for p in left_edge)<3
assert min(p[1] for p in left_edge)<=70 and max(p[1] for p in left_edge)>=160
for edge in edges:
  for x,y in edge:
    assert not (230<x<255 and 105<y<130)
assert not road_boundaries(np.full_like(labels,2),np.zeros_like(labels,bool),1)
assert not road_boundaries(labels,np.ones_like(labels,bool),1)
print('Image boundaries: continuous dashed divider, car exclusion, empty road and area masks passed')
