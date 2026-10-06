"""Bring tracked ground positions into the current ego frame before estimating motion."""
import numpy as np


def compensated_motion(samples):
  # Samples: recorded time, forward, left, ego speed, ego yaw rate (rad/s).
  if len(samples)<2:
    return None
  data=np.asarray(samples,dtype=float)
  dt=np.diff(data[:,0])
  if not np.isfinite(data).all() or np.any(dt<=0) or data[-1,0]-data[0,0]<.15:
    return None
  angle_step=(data[:-1,4]+data[1:,4])*.5*dt
  heading=np.r_[0.,np.cumsum(angle_step)]
  distance=(data[:-1,3]+data[1:,3])*.5*dt
  # Integrate forward travel along the turning arc, including the straight limit.
  forward=distance*np.sinc(angle_step/np.pi)
  left=distance*angle_step*.5*np.sinc(angle_step/(2*np.pi))**2
  c,s=np.cos(heading[:-1]),np.sin(heading[:-1])
  travel=np.column_stack((c*forward-s*left,s*forward+c*left))
  ego=np.vstack((np.zeros(2),np.cumsum(travel,axis=0)))
  c,s=np.cos(heading),np.sin(heading)
  world=np.column_stack((c*data[:,1]-s*data[:,2],s*data[:,1]+c*data[:,2]))+ego
  delta=world-ego[-1]
  c,s=np.cos(heading[-1]),np.sin(heading[-1])
  points=np.column_stack((c*delta[:,0]+s*delta[:,1],-s*delta[:,0]+c*delta[:,1]))
  time=data[:,0]-data[:,0].mean()
  velocity=time @ points / (time @ time)
  return points,velocity
