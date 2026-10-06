const modelSize=document.getElementById('model-size');
const featureObjects=document.getElementById('feature-objects');
const featureMasks=document.getElementById('feature-masks');
const featureScene=document.getElementById('feature-scene');
const segmentationSource=document.getElementById('segmentation-source');
let featuresBusy=false;
function updateFeatures(selection,source){
 if(featuresBusy||!selection)return;
 const [task,size]=selection.split('-');
 modelSize.value=size;
 if(source)segmentationSource.value=source;
 featureObjects.checked=['scene','sceneMask','detect','segment'].includes(task);
 featureMasks.checked=['sceneMask','segment'].includes(task);
 featureScene.checked=['scene','sceneMask','semantic'].includes(task);
 segmentationSource.disabled=!featureScene.checked;
}
async function changeFeatures(event){
 if(event.target===featureMasks&&featureMasks.checked)featureObjects.checked=true;
 if(event.target===featureObjects&&!featureObjects.checked)featureMasks.checked=false;
 featuresBusy=true;
 const controls=[modelSize,featureObjects,featureMasks,featureScene,segmentationSource];
 controls.forEach(input=>input.disabled=true);
 try{
  const response=await fetch('/features',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({size:modelSize.value,objects:featureObjects.checked,masks:featureMasks.checked,scene:featureScene.checked,segmentation_source:segmentationSource.value})});
  if(!response.ok)throw Error('Feature change failed');
 }finally{
  featuresBusy=false;controls.forEach(input=>input.disabled=false);await update();
 }
}
for(const input of [modelSize,featureObjects,featureMasks,featureScene,segmentationSource])input.onchange=changeFeatures;
