"""Run with the viewer's Python: python tools/yolo/check_object_labels.py."""
import ast
from pathlib import Path
import cv2

# Load the pure layout helper without importing models or starting a viewer.
source=ast.parse(Path(__file__).with_name('yolo_viewer.py').read_text())
helper=next(node for node in source.body if isinstance(node,ast.FunctionDef) and node.name=='layout_object_labels')
namespace={'cv2':cv2}
exec(compile(ast.Module(body=[helper],type_ignores=[]),'label-layout','exec'),namespace)
annotations=[((430+i*5,220+i*3,580+i*5,400+i*3),f'car 90% | {i} | ~18 m >') for i in range(12)]
placed=namespace['layout_object_labels']((720,1280,3),annotations)
assert len(placed)==len(annotations)
rectangles=[entry[2] for entry in placed]
for i,(x,y,x1,y1) in enumerate(rectangles):
  assert 0<=x<x1<=1280 and 0<=y<y1<=720
  for a,b,a1,b1 in rectangles[:i]:
    assert min(x1,a1)<=max(x,a) or min(y1,b1)<=max(y,b), 'Labels overlap'
assert namespace['layout_object_labels']((720,1280,3),[])==[]
long=namespace['layout_object_labels']((120,180,3),[((40,50,80,80),'very long sign text '*20)])[0]
assert long[2][2]<=180 and long[1].endswith('...')
print('Label layout: clustered objects, clipping and long text passed')
