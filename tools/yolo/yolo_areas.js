const areaSVG=document.createElementNS('http://www.w3.org/2000/svg','svg');
areaSVG.setAttribute('viewBox','0 0 1000 1000');areaSVG.setAttribute('preserveAspectRatio','none');
areaSVG.setAttribute('aria-label','Area selection editor');
areaSVG.style.cssText='position:absolute;display:none;touch-action:none;z-index:2;cursor:crosshair';
video.parentElement.append(areaSVG);video.parentElement.style.userSelect='none';
const areaControls=document.createElement('div');areaControls.className='controls';areaControls.style.marginTop='12px';
areaControls.innerHTML='<button id="edit-area" type="button">Edit areas</button><button id="add-area" type="button">Add blackout area</button><button id="finish-area" type="button" hidden>Finish area</button><button id="remove-area" type="button">Remove area</button><span id="area-help" hidden>Add an area, then drag its points to adjust it</span>';
document.querySelector('.opacity-controls').after(areaControls);
const areaStorage='sunnydrive-yolo-blackout-v1';let blackoutAreas={};
try{blackoutAreas=JSON.parse(localStorage.getItem(areaStorage)||'{}');}catch{}
let drawingArea=null,selectedArea=null,dragArea=null;
const maskLayoutStorage='sunnydrive-yolo-mask-layout-v1';let maskLayouts={},sideGeometry=null;
let maskSides=[];
try{maskSides=JSON.parse(localStorage.getItem('sunnydrive-yolo-mask-sides-v1')||'[]');}catch{}
try{maskLayouts=JSON.parse(localStorage.getItem(maskLayoutStorage)||'{}');}catch{}
function currentSideLayout(){return {rotation:{left:Number(rotationInputs[0].value),right:Number(rotationInputs[1].value)},position:{left:positionInputs.slice(0,2).map(i=>Number(i.value)/100),right:positionInputs.slice(2).map(i=>Number(i.value)/100)}};}
function sidePoint(point,side,layout,inverse=false){
 const [height,width,driverHeight,leftNative,rightNative,wideWidth]=sideGeometry;
 const nativeWidth=side==='left'?leftNative:rightNative,panelWidth=Math.round(nativeWidth*height/driverHeight);
 const base=side==='left'?0:Math.round(leftNative*height/driverHeight)+wideWidth;
 const [px,py]=layout.position[side],r=layout.rotation[side]*Math.PI/180,c=Math.cos(r),s=Math.sin(r);
 const cx=(nativeWidth-1)/2,cy=(driverHeight-1)/2,sx=panelWidth/nativeWidth,sy=height/driverHeight;
 const tx=(sx-1)/2+base+Math.round(px*width),ty=(sy-1)/2+Math.round(py*height);
 if(inverse){
  const x=(point[0]*(width-1)-tx)/sx-cx,y=(point[1]*(height-1)-ty)/sy-cy;
  return [(c*x-s*y+cx)/(nativeWidth-1),(s*x+c*y+cy)/(driverHeight-1)];
 }
 const x=point[0]*(nativeWidth-1)-cx,y=point[1]*(driverHeight-1)-cy;
 return [(sx*(c*x+s*y+cx)+tx)/(width-1),(sy*(-s*x+c*y+cy)+ty)/(height-1)];
}
function syncSideAreas(){
 if(camera.value!=='wideSides'||!sideGeometry)return;
 const next=currentSideLayout(),previous=maskLayouts.wideSides;
 if(previous&&JSON.stringify(previous)!==JSON.stringify(next)){
  const move=(poly,index)=>{
   if(!poly.length)return poly;
   const center=poly.reduce((a,p)=>[a[0]+p[0]/poly.length,a[1]+p[1]/poly.length],[0,0]);
   for(const side of (index<maskSides.length?[maskSides[index]].filter(Boolean):['right','left'])){
    const local=sidePoint(center,side,previous,true);
    if(local.every(v=>v>=0&&v<=1)){maskSides[index]=side;return poly.map(p=>sidePoint(sidePoint(p,side,previous,true),side,next));}
   }
   maskSides[index]=null;return poly;
  };
  blackoutAreas.wideSides=areas().map(move);
  if(drawingArea)drawingArea=move(drawingArea,areas().length);
 }
 for(let index=maskSides.length;index<areas().length;index++){
  const poly=areas()[index],center=poly.reduce((a,p)=>[a[0]+p[0]/poly.length,a[1]+p[1]/poly.length],[0,0]);
  maskSides[index]=['right','left'].find(side=>sidePoint(center,side,next,true).every(v=>v>=0&&v<=1))||null;
 }
 maskSides.length=areas().length;
 localStorage.setItem('sunnydrive-yolo-mask-sides-v1',JSON.stringify(maskSides));
 maskLayouts.wideSides=next;
 localStorage.setItem(maskLayoutStorage,JSON.stringify(maskLayouts));
}
function updateSideGeometry(geometry){
 if(!geometry)return;
 const first=!sideGeometry;sideGeometry=geometry;
 if(first){syncSideAreas();areaChanged();}
}

function areas(){return blackoutAreas[camera.value]||[];}
let editing=false,dragPoint=null,areaTimer;
function areaLayout(){
 const w=video.parentElement.clientWidth,h=video.parentElement.clientHeight;
 const ratio=video.naturalWidth/video.naturalHeight||16/9;
 const vw=Math.min(w,h*ratio),vh=vw/ratio;
 Object.assign(areaSVG.style,{left:(w-vw)/2+'px',top:(h-vh)/2+'px',width:vw+'px',height:vh+'px'});
 areaDraw();
}
function areaDraw(){
 const all=[...areas(),...(drawingArea?[drawingArea]:[])];
 const rx=1000/Math.max(areaSVG.clientWidth,1),ry=1000/Math.max(areaSVG.clientHeight,1);
 areaSVG.innerHTML=all.map((poly,a)=>{
  const outline=`<polygon data-area="${a}" points="${poly.map(p=>p.map(v=>v*1000).join(',')).join(' ')}" fill="transparent" stroke="${selectedArea===a?'#ffdc00':'#ff9666'}" stroke-width="2" vector-effect="non-scaling-stroke"/>`;
  const handles=poly.map((p,i)=>`<g data-area="${a}" data-point="${i}" style="cursor:grab"><ellipse cx="${p[0]*1000}" cy="${p[1]*1000}" rx="${16*rx}" ry="${16*ry}" fill="transparent"/><ellipse cx="${p[0]*1000}" cy="${p[1]*1000}" rx="${7*rx}" ry="${7*ry}" fill="#ff9666" stroke="#111" stroke-width="2" vector-effect="non-scaling-stroke"/></g>`).join('');
  if(a===areas().length)return outline+handles;
  const x=Math.max(18*rx,Math.min(1000-18*rx,Math.max(...poly.map(p=>p[0]*1000))+24*rx));
  const y=Math.max(18*ry,Math.min(1000-18*ry,Math.min(...poly.map(p=>p[1]*1000))));
  return outline+handles+`<g data-delete="${a}" role="button" tabindex="0" aria-label="Delete area ${a+1}" style="cursor:pointer"><title>Delete area ${a+1}</title><ellipse cx="${x}" cy="${y}" rx="${15*rx}" ry="${15*ry}" fill="#b32929" stroke="white" stroke-width="1" vector-effect="non-scaling-stroke"/><path d="M ${x-5*rx},${y-5*ry} L ${x+5*rx},${y+5*ry} M ${x+5*rx},${y-5*ry} L ${x-5*rx},${y+5*ry}" stroke="white" stroke-width="2" vector-effect="non-scaling-stroke"/></g>`;
 }).join('');
 document.querySelector('#finish-area').disabled=!drawingArea||drawingArea.length<3;
 document.querySelector('#remove-area').textContent=drawingArea?'Cancel area':'Remove area';
}
function deleteArea(index){areas().splice(index,1);if(camera.value==='wideSides')maskSides.splice(index,1);selectedArea=null;dragArea=null;dragPoint=null;areaChanged();}
areaSVG.onkeydown=e=>{
 const button=e.target.closest('[data-delete]');
 if(button&&(e.key==='Enter'||e.key===' ')){e.preventDefault();deleteArea(Number(button.dataset.delete));}
};
async function areaSave(){
 syncSideAreas();
 localStorage.setItem(areaStorage,JSON.stringify(blackoutAreas));
 const maskResult=await fetch('/masks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({camera:camera.value,polygons:areas(),layout:camera.value==='wideSides'?maskLayouts.wideSides:null,sides:camera.value==='wideSides'&&maskSides.length===areas().length?maskSides:null})});
 if(!maskResult.ok)document.querySelector('#area-help').textContent='Could not save blackout areas; try again.';

}
function areaChanged(){areaDraw();clearTimeout(areaTimer);areaTimer=setTimeout(areaSave,80);}
function areaPosition(e){const r=areaSVG.getBoundingClientRect();return [Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))];}
areaSVG.onpointerdown=e=>{
 const remove=e.target.closest('[data-delete]');
 if(remove){deleteArea(Number(remove.dataset.delete));return;}
 const handle=e.target.closest('[data-point]');
 if(handle){
  dragArea=Number(handle.dataset.area);dragPoint=Number(handle.dataset.point);
  selectedArea=dragArea;areaSVG.setPointerCapture(e.pointerId);areaDraw();return;
 }
 if(drawingArea){if(drawingArea.length<32)drawingArea.push(areaPosition(e));areaDraw();return;}
 const polygon=e.target.closest('[data-area]');
 selectedArea=polygon?Number(polygon.dataset.area):null;areaDraw();
};
areaSVG.onpointermove=e=>{
 if(dragPoint===null||dragArea===null)return;
 const poly=dragArea===areas().length?drawingArea:areas()[dragArea];
 if(!poly)return;
 poly[dragPoint]=areaPosition(e);
 if(poly===drawingArea)areaDraw();else areaChanged();
};
areaSVG.onpointerup=areaSVG.onpointercancel=()=>{dragPoint=null;dragArea=null;};

document.querySelector('#edit-area').onclick=()=>{editing=!editing;areaSVG.style.display=editing?'block':'none';document.querySelector('#area-help').hidden=!editing;document.querySelector('#edit-area').textContent=editing?'Done editing':'Edit areas';areaLayout();};
document.querySelector('#add-area').onclick=()=>{
 if(areas().length>=16)return;
 if(!editing)document.querySelector('#edit-area').click();
 drawingArea=[];selectedArea=null;document.querySelector('#finish-area').hidden=false;
 document.querySelector('#area-help').textContent=maskModeSelect.value==='keep'?'Trace a window or area to keep, then Finish area. Add more keep areas for other windows. Everything else is masked.':'Click to outline an area, then Finish area. Drag orange points to reshape; click its X to delete it.';
 areaDraw();
};
document.querySelector('#finish-area').onclick=()=>{
 if(!drawingArea||drawingArea.length<3)return;
 blackoutAreas[camera.value]=[...areas(),drawingArea];selectedArea=areas().length-1;drawingArea=null;
 document.querySelector('#finish-area').hidden=true;areaChanged();
};
document.querySelector('#remove-area').onclick=()=>{
 if(drawingArea){drawingArea=null;document.querySelector('#finish-area').hidden=true;areaDraw();return;}
 const list=areas();if(!list.length)return;
 deleteArea(selectedArea===null?list.length-1:selectedArea);
};
camera.addEventListener('change',()=>{dragPoint=null;dragArea=null;selectedArea=null;drawingArea=null;document.querySelector('#finish-area').hidden=true;areaDraw();areaSave();});
video.addEventListener('load',areaLayout);new ResizeObserver(areaLayout).observe(video.parentElement);
fetch('/status',{cache:'no-store'}).then(r=>r.json()).then(s=>{camera.value=s.camera;areaDraw();areaSave();});
const rotationControls=document.createElement('div');rotationControls.className='opacity-controls';
rotationControls.innerHTML=['left','right'].map(side=>`<label>${side==='left'?'Left':'Right'} side rotation <input id="rotate-${side}" aria-label="${side==='left'?'Left':'Right'} side rotation" type="range" min="-180" max="180" step="1" value="0"><output id="angle-${side}">0°</output></label>`).join('');
areaControls.after(rotationControls);
const rotationInputs=['left','right'].map(side=>document.querySelector('#rotate-'+side));
const rotationStorage='sunnydrive-yolo-side-rotation-v1';let rotationTimer;
try{const saved=JSON.parse(localStorage.getItem(rotationStorage)||'{}');rotationInputs.forEach((input,i)=>{const v=saved[['left','right'][i]];if(Number.isFinite(v)&&v>=-180&&v<=180)input.value=v;});}catch{}
function rotationLabels(){rotationInputs.forEach((input,i)=>document.querySelector('#angle-'+['left','right'][i]).textContent=input.value+'°');}
async function rotationSave(){
 const angles={left:Number(rotationInputs[0].value),right:Number(rotationInputs[1].value)};
 localStorage.setItem(rotationStorage,JSON.stringify(angles));
 const r=await fetch('/rotation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(angles)});
 if(!r.ok)document.querySelector('#area-help').textContent='Could not save side rotation; try again.';
}
rotationInputs.forEach(input=>input.oninput=()=>{rotationLabels();syncSideAreas();areaChanged();clearTimeout(rotationTimer);rotationTimer=setTimeout(rotationSave,80);});
function rotationVisibility(){sideControls.style.display=camera.value==='wideSides'?'grid':'none';}
camera.addEventListener('change',rotationVisibility);
fetch('/status',{cache:'no-store'}).then(r=>r.json()).then(s=>{camera.value=s.camera;rotationVisibility();rotationLabels();rotationSave();});
const positionControls=document.createElement('div');positionControls.className='opacity-controls';
const positionKeys=['left-x','left-y','right-x','right-y'];
positionControls.innerHTML=positionKeys.map(key=>{const [side,axis]=key.split('-'),label=(side==='left'?'Left':'Right')+' side '+(axis==='x'?'horizontal':'vertical');return `<label>${label} <input id="position-${key}" aria-label="${label}" type="range" min="-50" max="50" step="1" value="0"><output id="offset-${key}">0%</output></label>`;}).join('');
rotationControls.after(positionControls);
const positionInputs=positionKeys.map(key=>document.querySelector('#position-'+key));
const positionStorage='sunnydrive-yolo-side-position-v1';let positionTimer;
try{const saved=JSON.parse(localStorage.getItem(positionStorage)||'{}');positionInputs.forEach((input,i)=>{const v=saved[positionKeys[i]];if(Number.isFinite(v)&&v>=-50&&v<=50)input.value=v;});}catch{}
function positionLabels(){positionInputs.forEach((input,i)=>document.querySelector('#offset-'+positionKeys[i]).textContent=input.value+'%');}
async function positionSave(){
 const values=positionInputs.map(input=>Number(input.value));
 localStorage.setItem(positionStorage,JSON.stringify(Object.fromEntries(positionKeys.map((k,i)=>[k,values[i]]))));
 const r=await fetch('/position',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({left:values.slice(0,2).map(v=>v/100),right:values.slice(2).map(v=>v/100)})});
 if(!r.ok)document.querySelector('#area-help').textContent='Could not save side position; try again.';
}
positionInputs.forEach(input=>input.oninput=()=>{positionLabels();syncSideAreas();areaChanged();clearTimeout(positionTimer);positionTimer=setTimeout(positionSave,80);});
function positionVisibility(){rotationVisibility();}
camera.addEventListener('change',positionVisibility);
fetch('/status',{cache:'no-store'}).then(r=>r.json()).then(s=>{camera.value=s.camera;positionVisibility();positionLabels();positionSave();});

const sideControls=document.createElement('div');sideControls.className='side-controls';
areaControls.after(sideControls);
['left','right'].forEach((side,i)=>{
 const column=document.createElement('section');column.className='side-column';
 const title=document.createElement('strong');title.textContent=(side==='left'?'Left':'Right')+' side';column.append(title);
 const inputs=[rotationInputs[i],positionInputs[i*2],positionInputs[i*2+1]];
 inputs.forEach((input,index)=>{const label=input.closest('label');label.firstChild.textContent=['Rotation ','Horizontal ','Vertical '][index];column.append(label);});
 sideControls.append(column);
});
rotationControls.remove();positionControls.remove();rotationVisibility();
const resetSides=document.createElement('button');resetSides.type='button';resetSides.textContent='Reset sides';
resetSides.onclick=()=>{
 rotationInputs.forEach(input=>input.value=0);
 positionInputs.forEach(input=>input.value=0);
 rotationLabels();positionLabels();syncSideAreas();areaChanged();
 clearTimeout(rotationTimer);clearTimeout(positionTimer);
 rotationSave();positionSave();
};
sideControls.append(resetSides);

const maskModeLabel=document.createElement('label');maskModeLabel.style.cssText='display:flex;gap:10px;align-items:center';
maskModeLabel.innerHTML='Area selection <select id="mask-mode" aria-label="Area selection"><option value="exclude">Black out selected areas</option><option value="keep">Keep selected areas</option></select>';
areaControls.append(maskModeLabel);
const maskModeSelect=document.querySelector('#mask-mode');
const maskModesStorage='sunnydrive-yolo-mask-modes-v1';let maskModes={};
try{maskModes=JSON.parse(localStorage.getItem(maskModesStorage)||'{}');}catch{}
const legacyMaskMode=localStorage.getItem('sunnydrive-yolo-mask-mode')==='keep'?'keep':'exclude';
async function saveMaskMode(){
 const view=camera.value,mode=maskModeSelect.value;
 maskModes[view]=mode;
 localStorage.setItem(maskModesStorage,JSON.stringify(maskModes));
 document.querySelector('#add-area').textContent=mode==='keep'?'Add keep area':'Add blackout area';
 areaDraw();
 const r=await fetch('/mask-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({camera:view,mode})});
 if(!r.ok)document.querySelector('#area-help').textContent='Could not save selection mode; try again.';
}
function restoreMaskMode(){
 maskModeSelect.value=maskModes[camera.value]||legacyMaskMode;
 saveMaskMode();
}
maskModeSelect.onchange=saveMaskMode;
camera.addEventListener('change',restoreMaskMode);
fetch('/status',{cache:'no-store'}).then(r=>r.json()).then(s=>{camera.value=s.camera;restoreMaskMode();});
restoreMaskMode();

// Drag a side panel in the preview; area editing keeps its point-drag behavior.
let sideDrag=null;
const preview=video.parentElement;
function previewPoint(e){
 const rect=video.getBoundingClientRect(),ratio=video.naturalWidth/video.naturalHeight||16/9;
 const width=Math.min(rect.width,rect.height*ratio),height=width/ratio;
 return [(e.clientX-rect.left-(rect.width-width)/2)/width,(e.clientY-rect.top-(rect.height-height)/2)/height];
}
preview.addEventListener('pointerdown',e=>{
 if(editing||camera.value!=='wideSides'||!sideGeometry||e.button!==0)return;
 const point=previewPoint(e),layout=currentSideLayout();
 const side=['right','left'].find(side=>sidePoint(point,side,layout,true).every(v=>v>=0&&v<=1));
 if(!side)return;
 const offset=side==='left'?0:2;
 sideDrag={point,offset,x:Number(positionInputs[offset].value),y:Number(positionInputs[offset+1].value)};
 preview.setPointerCapture(e.pointerId);preview.style.cursor='grabbing';e.preventDefault();
});
preview.addEventListener('pointermove',e=>{
 if(!sideDrag)return;
 const point=previewPoint(e),{offset,x,y}=sideDrag;
 positionInputs[offset].value=Math.max(-50,Math.min(50,Math.round(x+(point[0]-sideDrag.point[0])*100)));
 positionInputs[offset+1].value=Math.max(-50,Math.min(50,Math.round(y+(point[1]-sideDrag.point[1])*100)));
 positionInputs[offset].oninput();
});
preview.addEventListener('pointerup',()=>{sideDrag=null;preview.style.cursor='';});
preview.addEventListener('pointercancel',()=>{sideDrag=null;preview.style.cursor='';});
const dragHint=document.createElement('span');dragHint.textContent='Drag side panels on the image to move them. Finish area editing first.';
sideControls.append(dragHint);preview.style.touchAction='none';

const laneStyleControls=document.createElement('div');laneStyleControls.className='opacity-controls';
laneStyleControls.innerHTML='<label>Lane UI width <input id="lane-ui-width" aria-label="Lane UI width" type="range" min="1" max="16" step="1" value="3"><output id="lane-ui-width-value">3 px</output></label><label>Lane UI opacity <input id="lane-ui-opacity" aria-label="Lane UI opacity" type="range" min="0" max="100" step="1" value="100"><output id="lane-ui-opacity-value">100%</output></label>';
document.querySelector('.opacity-controls').after(laneStyleControls);
const laneWidthInput=document.querySelector('#lane-ui-width'),laneAlphaInput=document.querySelector('#lane-ui-opacity');
const laneStyleStorage='sunnydrive-yolo-lane-style-v1';let laneStyleTimer;
try{
 const saved=JSON.parse(localStorage.getItem(laneStyleStorage)||'{}');
 if(Number.isInteger(saved.width)&&saved.width>=1&&saved.width<=16)laneWidthInput.value=saved.width;
 if(Number.isFinite(saved.opacity)&&saved.opacity>=0&&saved.opacity<=1)laneAlphaInput.value=Math.round(saved.opacity*100);
}catch{}
function laneStyleLabels(){
 document.querySelector('#lane-ui-width-value').textContent=laneWidthInput.value+' px';
 document.querySelector('#lane-ui-opacity-value').textContent=laneAlphaInput.value+'%';
}
async function saveLaneStyle(){
 const style={width:Number(laneWidthInput.value),opacity:Number(laneAlphaInput.value)/100};
 localStorage.setItem(laneStyleStorage,JSON.stringify(style));
 const result=await fetch('/lane-style',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(style)});
 if(!result.ok)document.querySelector('#area-help').textContent='Could not save lane style; try again.';
}
laneWidthInput.oninput=laneAlphaInput.oninput=()=>{laneStyleLabels();clearTimeout(laneStyleTimer);laneStyleTimer=setTimeout(saveLaneStyle,80);};
laneStyleLabels();saveLaneStyle();

const bumperLabel=document.createElement('label');bumperLabel.style.cssText='display:flex;gap:10px;align-items:center';
bumperLabel.innerHTML='Camera → front bumper (m) <input id="bumper-offset" aria-label="Camera to front bumper meters" type="number" min="0" max="5" step="0.01" placeholder="Measured offset" style="width:150px">';
laneStyleControls.after(bumperLabel);
const bumperInput=document.querySelector('#bumper-offset'),bumperStorage='sunnydrive-yolo-bumper-offset-v1';
const savedBumper=localStorage.getItem(bumperStorage);
if(savedBumper!==null&&savedBumper!==''&&Number.isFinite(Number(savedBumper))&&Number(savedBumper)>=0&&Number(savedBumper)<=5)bumperInput.value=savedBumper;
async function saveBumperOffset(){
 if(!bumperInput.checkValidity())return;
 const meters=bumperInput.value===''?null:Number(bumperInput.value);
 if(meters===null)localStorage.removeItem(bumperStorage);else localStorage.setItem(bumperStorage,String(meters));
 const response=await fetch('/bumper-offset',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({meters})});
 if(!response.ok)document.querySelector('#area-help').textContent='Could not save bumper offset; try again.';
}
bumperInput.onchange=saveBumperOffset;saveBumperOffset();


const objectModeLabel=document.createElement('label');objectModeLabel.style.cssText='display:flex;gap:8px;align-items:center';
objectModeLabel.innerHTML='Display <select id="object-mode" aria-label="Object display"><option value="full">Full view</option><option value="masked">Objects only — masked</option><option value="original">Objects only — original</option></select>';
document.querySelector('header .controls').append(objectModeLabel);
const objectModeInput=document.querySelector('#object-mode'),objectModeStorage='sunnydrive-yolo-object-mode-v1';
function updateObjectMode(mode){
 if(objectModeInput.disabled)return;
 objectModeInput.value=['full','masked','original'].includes(mode)?mode:'full';
 localStorage.setItem(objectModeStorage,objectModeInput.value);
}
async function saveObjectMode(){
 objectModeInput.disabled=true;
 try{
  const r=await fetch('/object-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:objectModeInput.value})});
  if(!r.ok)document.querySelector('#area-help').textContent='Could not change object display; try again.';
 }finally{objectModeInput.disabled=false;await update();}
}
objectModeInput.onchange=saveObjectMode;
const savedObjectMode=localStorage.getItem(objectModeStorage)||(localStorage.getItem('sunnydrive-yolo-cars-only')==='true'?'original':'full');
objectModeInput.value=['full','masked','original'].includes(savedObjectMode)?savedObjectMode:'full';
if(objectModeInput.value!=='full')saveObjectMode();

const annotationControls=document.createElement('span');annotationControls.style.cssText='display:flex;gap:12px';
annotationControls.innerHTML='<label class="overlay-toggle"><input type="checkbox" id="show-labels" checked> Labels</label><label class="overlay-toggle"><input type="checkbox" id="show-boxes" checked> Bounding boxes</label><label class="overlay-toggle"><input type="checkbox" id="show-motion" checked> Arrows and trails</label><label class="overlay-toggle"><input type="checkbox" id="road-signals" checked> Lights / sign text</label><label class="overlay-toggle"><input type="checkbox" id="show-radar" checked> Radar / sensor tracks</label><label class="overlay-toggle"><input type="checkbox" id="hide-stationary"> Hide stationary</label><label class="overlay-toggle"><input type="checkbox" id="top-seg"> Top-down segmentation</label><label class="overlay-toggle"><input type="checkbox" id="show-actions" checked> Actions / paths</label><label class="overlay-toggle"><input type="checkbox" id="our-edges"> Our lanes / edges</label>';
document.querySelector('header .controls').append(annotationControls);
const showLabelsInput=document.querySelector('#show-labels'),showBoxesInput=document.querySelector('#show-boxes'),showMotionInput=document.querySelector('#show-motion'),roadSignalsInput=document.querySelector('#road-signals');
const showRadarInput=document.querySelector('#show-radar');
const showActionsInput=document.querySelector('#show-actions');
const topSegInput=document.querySelector('#top-seg');
const hideStationaryInput=document.querySelector('#hide-stationary');
const ourEdgesInput=document.querySelector('#our-edges');
const annotationStorage='sunnydrive-yolo-annotations-v1';
try{const saved=JSON.parse(localStorage.getItem(annotationStorage)||'{}');if(typeof saved.our_edges==='boolean')ourEdgesInput.checked=saved.our_edges;if(typeof saved.actions==='boolean')showActionsInput.checked=saved.actions;if(typeof saved.top_seg==='boolean')topSegInput.checked=saved.top_seg;if(typeof saved.labels==='boolean')showLabelsInput.checked=saved.labels;if(typeof saved.boxes==='boolean')showBoxesInput.checked=saved.boxes;if(typeof saved.motion==='boolean')showMotionInput.checked=saved.motion;if(typeof saved.hide_stationary==='boolean')hideStationaryInput.checked=saved.hide_stationary;if(typeof saved.radar==='boolean')showRadarInput.checked=saved.radar;if(typeof saved.signals==='boolean')roadSignalsInput.checked=saved.signals;}catch{}
async function saveAnnotations(){
 const values={labels:showLabelsInput.checked,boxes:showBoxesInput.checked,motion:showMotionInput.checked,signals:roadSignalsInput.checked,radar:showRadarInput.checked,hide_stationary:hideStationaryInput.checked,top_seg:topSegInput.checked,actions:showActionsInput.checked,our_edges:ourEdgesInput.checked};
 localStorage.setItem(annotationStorage,JSON.stringify(values));
 const response=await fetch('/annotations',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(values)});
 if(!response.ok)document.querySelector('#area-help').textContent='Could not save annotation visibility; try again.';
}
showLabelsInput.onchange=showBoxesInput.onchange=showMotionInput.onchange=roadSignalsInput.onchange=showRadarInput.onchange=hideStationaryInput.onchange=topSegInput.onchange=showActionsInput.onchange=ourEdgesInput.onchange=saveAnnotations;saveAnnotations();

// Feature checkboxes are saved in the server model selection; overlays live in this browser.
const laneToggleStorage='sunnydrive-yolo-lane-toggle-v1';
let laneToggleBusy=false;
const changeLaneOverlay=commaOverlay.onchange;
commaOverlay.onchange=async()=>{
 localStorage.setItem(laneToggleStorage,JSON.stringify(commaOverlay.checked));
 laneToggleBusy=true;
 try{await changeLaneOverlay();}finally{laneToggleBusy=false;}
};
try{
 const saved=JSON.parse(localStorage.getItem(laneToggleStorage)||'null');
 if(typeof saved==='boolean'){
  commaOverlay.checked=saved;
  commaOverlay.onchange();
 }
}catch{}
