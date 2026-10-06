"""Read-only sensor-track provenance and a scene snapshot; never issue control commands."""
import math
from pathlib import Path

_schema=None


def decode_tracks(message):
  global _schema
  if _schema is None:
    import capnp
    _schema=capnp.load(str(Path(__file__).with_name('yolo_radar.capnp')))
  # Cap'n Proto preserves unknown fields; re-read the extended branch layout.
  with _schema.RadarData.from_bytes(message.as_builder().to_bytes()) as reader:
    return reader.to_dict()


def source_kind(address,bus,sources):
  source=next((s for s in sources if s['startAddress']<=address<=s['endAddress'] and s['bus']==bus),None)
  if source is None:
    return 'unknown','unclassified'
  first,last=source['startAddress'],source['endAddress']
  label=f'{first:03X}–{last:03X} / bus {bus}'
  if first==0x235 and last==0x248:
    return 'camera',label
  if first in (0x240,0x278):
    return 'candidate_radar',label
  if first in (0x500,0x602,0x210,0x3a5):
    return 'radar',label
  return 'unknown',label


def radar_snapshot(raw,timestamp,reference):
  if raw is None:
    return dict(status='unavailable',timestamp=None,age_ms=None,tracks=[],errors={})
  age=abs(reference-timestamp)
  errors=raw.get('errors',{})
  status='stale' if age>.2 else 'invalid' if any(errors.values()) else 'ready'
  tracks=[]
  if status=='ready':
    sources=raw.get('trackSources',[])
    for p in raw.get('points',[]):
      values=[p.get(key) for key in ('dRel','yRel','vRel')]
      if any(v is None or not math.isfinite(v) for v in values):
        continue
      forward,left,relative_speed=values
      if not -50<=forward<=250 or abs(left)>100:
        continue
      address,bus=int(p.get('sourceAddress',0)),int(p.get('sourceBus',0))
      kind,label=source_kind(address,bus,sources)
      tracks.append(dict(id=int(p['trackId']),forward=float(forward),left=float(left),relative_speed=float(relative_speed),
                         source=kind,source_label=label,address=address,bus=bus,motion_state=int(p.get('motionState',0)),
                         track_age=int(p.get('trackAge',0)),uncertainty=None))
  return dict(status=status,timestamp=timestamp,age_ms=round(age*1000,1),tracks=tracks,errors=errors)


def scene_snapshot(sample,top_down,timestamp):
  radar=(sample or {}).get('radar') or radar_snapshot(None,0,timestamp)
  objects=[dict(source=c.get('source','vision'),vision_forward=c.get('vision_forward',c['forward']),vision_left=c.get('vision_left',c['left']),relative_speed=c.get('relative_speed'),id=c['id'],type=c['type'],forward=c['forward'],left=c['left'],
                lane=c['lane'],heading=c.get('heading'),uncertainty=None) for c in top_down.get('cars',[])]
  return dict(timestamp=timestamp,frame='vehicle',distance_origin='front_bumper',ego=(sample or {}).get('car'),
              vision=objects,sensor_tracks=radar['tracks'],radar_status=radar['status'],radar_age_ms=radar.get('age_ms'),
              lanes=top_down.get('lanes',[]),lane_probabilities=top_down.get('probabilities',[]),
              traffic_lights=top_down.get('lights',[]),signal_lane_association=None,
              occupancy='unknown',control_ready=False)

class HyundaiReplayRadar:
  """Decode the confirmed 3A5–3C4 family using the radar branch's DBC."""
  def __init__(self):
    import tempfile
    from opendbc.can import CANParser
    from yolo_radar_dbc import generate
    with tempfile.NamedTemporaryFile(suffix='.dbc',mode='w') as dbc:
      dbc.write(next(iter(generate().values())))
      dbc.flush()
      self.parsers=[CANParser(dbc.name,[(addr,20) for addr in range(0x3a5,0x3c5)],bus) for bus in range(3)]
    self.seen=[set() for _ in self.parsers]
    self.times=[0.0]*3

  def update(self,events,reference):
    for event in events:
      timestamp=event.logMonoTime
      frames=[(p.address,bytes(p.dat),p.src) for p in event.can if 0x3a5<=p.address<=0x3c4 and len(p.dat)==24 and p.src<3]
      for bus,parser in enumerate(self.parsers):
        own=[p for p in frames if p[2]==bus]
        if own:
          if timestamp/1e9<self.times[bus]:
            self.seen[bus].clear()
          self.seen[bus].update(p[0] for p in own)
          parser.update([(timestamp,own)])
          self.times[bus]=timestamp/1e9
    candidates=[bus for bus in range(3) if len(self.seen[bus])==32 and abs(reference-self.times[bus])<=.2]
    if not candidates:
      return radar_snapshot(None,0,reference)
    bus=max(candidates,key=lambda b:self.times[b]); parser=self.parsers[bus]
    points=[]
    for addr in range(0x3a5,0x3c5):
      msg=parser.vl[addr]
      ts=parser.ts_nanos[addr].get('LONG_DIST',0)/1e9
      if int(msg['STATE']) not in (3,4) or abs(reference-ts)>.2:
        continue
      points.append(dict(trackId=bus*2048+addr,dRel=msg['LONG_DIST'],yRel=msg['LAT_DIST'],vRel=msg['REL_SPEED'],
                         sourceAddress=addr,sourceBus=bus,motionState=int(msg['MOTION_STATE']),trackAge=int(msg['AGE'])))
    raw=dict(points=points,trackSources=[dict(startAddress=0x3a5,endAddress=0x3c4,bus=bus)],errors={})
    return radar_snapshot(raw,self.times[bus],reference)

class RadarAssociator:
  """Conservative one-to-one association; ambiguous returns stay unmatched."""
  def __init__(self):
    self.reset()

  def reset(self):
    self.previous={};self.pending={};self.matches={};self.timestamp=None

  @staticmethod
  def key(track):
    return (track['bus'],track['address'],track['id'])

  def update(self,objects,tracks,timestamp):
    objects={o['id']:o for o in objects if o.get('id') is not None}
    tracks={self.key(t):t for t in tracks if t['source']=='radar' and t['forward']>0}
    if self.timestamp is not None and timestamp<self.timestamp:
      self.reset()
    if timestamp==self.timestamp:
      return {identity:match for identity,match in self.matches.items() if identity in objects and self.key(match['track']) in tracks}
    old=self.previous;dt=timestamp-self.timestamp if self.timestamp is not None else None
    edges=[]
    for identity,obj in objects.items():
      for key,track in tracks.items():
        longitudinal=abs(obj['forward']-track['forward']);lateral=abs(obj['left']-track['left'])
        range_gate=max(5.,track['forward']*.20);side_gate=min(3.,1.5+track['forward']*.015)
        if longitudinal>range_gate or lateral>side_gate:continue
        score=(longitudinal/range_gate)**2+(lateral/side_gate)**2
        if dt is not None and .15<=dt<=1.0 and identity in old:
          speed=(obj['forward']-old[identity]['forward'])/dt
          difference=abs(speed-track['relative_speed'])
          if difference>8.:continue
          score+=(difference/8.)**2*.5
        if score<1.:edges.append((score,identity,key))
    edges.sort();pending={};matches={}
    for score,identity,key in edges:
      alternatives=[s for s,i,k in edges if (i==identity or k==key) and (i,k)!=(identity,key)]
      # Require a clear winner for both the visual object and radar return.
      if alternatives and min(alternatives)-score<.2:continue
      track=tracks[key];prior=self.pending.get(identity)
      continuous=prior is not None and prior['key']==key and 0<timestamp-prior['time']<=1.0 and track['track_age']>=prior['age']
      count=prior['count']+1 if continuous else 1
      start=prior['start'] if continuous else timestamp
      pending[identity]=dict(key=key,count=count,start=start,time=timestamp,age=track['track_age'])
      if count>=3 and timestamp-start>=.15:
        matches[identity]=dict(track=track,box=objects[identity]['box'],cost=round(score,3))
    self.previous=objects;self.pending=pending;self.matches=matches;self.timestamp=timestamp
    return matches
