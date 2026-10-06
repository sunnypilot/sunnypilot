"""Check feature combinations without loading weights or starting the viewer."""
import ast
from pathlib import Path

source=ast.parse(Path(__file__).with_name('yolo_viewer.py').read_text())
functions=[node for node in source.body if isinstance(node,ast.FunctionDef) and node.name in ('selected_features','feature_selection','load')]
class Model:
  def __init__(self,path):
    self.path=path
  def to(self,device):
    return self
namespace={'CommaSegmenter':lambda:Model('comma10k'),'YOLO':Model,'TASKS':{'detect':('Detection',''),'segment':('Masks','-seg'),'semantic':('Scene','-sem')}}
exec(compile(ast.Module(body=functions,type_ignores=[]),'features','exec'),namespace)
for size in 'nsmlx':
  for objects in (False,True):
    for masks in (False,True):
      for scene in (False,True):
        selection=namespace['feature_selection'](size,objects,masks,scene)
        assert namespace['selected_features'](selection)==dict(size=size,objects=objects or masks,masks=masks,scene=scene)
        models=namespace['load'](selection,Path('/tmp'))
        assert len(models)==int(scene)+int(objects or masks)
        assert any('-seg.pt' in model.path for model in models)==masks
        comma_models=namespace['load'](selection,Path('/tmp'),'comma10k')
        assert sum(model.path=='comma10k' for model in comma_models)==int(scene)
        assert len(comma_models)==len(models)
        assert not any('-sem.pt' in model.path for model in comma_models)
print('All 40 model-size and feature combinations passed')
