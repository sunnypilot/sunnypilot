"""Ensure comma trajectory is not drawn as an independently detected path."""
import numpy as np
from yolo_web import draw_comma_overlay
sample={'roadCamera':{'ground':[0,100,320,-10,0,450,0,0,1],'width':640,'height':480},'model':{'path':{'x':[5,10,20],'y':[0,0,0],'z':[0,0,0]}}}
image=np.zeros((480,640,3),np.uint8)
draw_comma_overlay(image,sample,'road')
assert not image.any()
print('Comma model path is omitted from the camera overlay')
