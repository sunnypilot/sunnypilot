"""Check that redraws reuse inference and changed input runs each selected model once."""
import ast
from pathlib import Path
from types import SimpleNamespace
import cv2
import numpy as np

source=ast.parse(Path(__file__).with_name('yolo_viewer.py').read_text())
helper=next(node for node in source.body if isinstance(node,ast.FunctionDef) and node.name=='infer')
namespace={'cv2':cv2,'np':np}
palette_nodes=[node for node in source.body if isinstance(node,ast.Assign) and ast.unparse(node).startswith(('SCENE_PALETTE =','SCENE_COLORS =','SCENE_COLORS['))]
exec(compile(ast.Module(body=palette_nodes,type_ignores=[]),'scene-colors','exec'),namespace)
labels=np.random.default_rng(0).integers(0,19,(120,160),dtype=np.int64)
assert np.array_equal(cv2.applyColorMap(labels.astype(np.uint8),namespace['SCENE_COLORS']),namespace['SCENE_PALETTE'][labels])
assert np.array_equal(np.flatnonzero(np.bincount(labels.reshape(-1),minlength=19)),np.unique(labels))
exec(compile(ast.Module(body=[helper],type_ignores=[]),'inference-cache','exec'),namespace)
class Tensor:
  def __init__(self):
    self.transfers=0
  def cpu(self):
    self.transfers+=1
    return self
class Model:
  def __init__(self,task):
    self.task=task
    self.calls=0
  def predict(self,*args,**kwargs):
    self.calls+=1
    return [SimpleNamespace(boxes=Tensor() if self.task=='detect' else None,semantic_mask=Tensor() if self.task=='semantic' else None)]
  track=predict
models=[Model('semantic'),Model('detect')]
cache={}
infer=namespace['infer']
results=infer(models,None,640,cache,(1,'layout'))
for _ in range(10):
  assert infer(models,None,640,cache,(1,'layout')) is results
assert [m.calls for m in models]==[1,1]
assert results[0][1].semantic_mask.transfers==1
assert results[1][1].boxes.transfers==1
infer(models,None,640,cache,(2,'layout'))
infer(models,None,640,cache,(2,'edited mask'))
assert [m.calls for m in models]==[3,3]
cache.clear()
assert infer([],None,640,cache,(2,'no models'))==[]
print('Inference cache: redraw reuse, tensor transfers, new frames and mask edits passed')
