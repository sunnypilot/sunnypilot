const topDownPanel=document.createElement('section');
topDownPanel.style.cssText='padding:0;border:1px solid #334155;border-radius:12px;background:#101722;min-width:0;box-sizing:border-box;overflow:hidden';
topDownPanel.innerHTML='<canvas width="420" height="520" aria-label="Top-down lane lines and detected cars" style="width:100%;height:100%;display:block"></canvas>';
const sceneLayout=document.createElement('div');sceneLayout.className='scene-layout';
const cameraPanel=video.parentElement;cameraPanel.before(sceneLayout);sceneLayout.append(cameraPanel,topDownPanel);
const trafficLightRow=document.createElement('div');
trafficLightRow.className='traffic-light-row';trafficLightRow.setAttribute('aria-live','polite');
trafficLightRow.style.cssText='position:absolute;top:10px;right:10px;z-index:3;pointer-events:none;display:flex;align-items:center;flex-wrap:wrap;gap:8px;padding:7px 10px;background:rgba(8,13,20,.8);border:1px solid rgba(148,163,184,.25);border-radius:8px;box-sizing:border-box;width:auto;max-width:calc(100% - 20px);font-size:12px';
cameraPanel.append(trafficLightRow);
const actionPanel=document.createElement('div');
actionPanel.style.cssText='position:absolute;bottom:12px;left:12px;z-index:3;pointer-events:none;max-width:calc(100% - 24px);padding:9px 12px;border-radius:8px;background:rgba(8,13,20,.86);border:1px solid #334155;font-size:12px;display:none';
cameraPanel.append(actionPanel);
function updateActions(scene){
 const preview=scene?.action_preview;
 actionPanel.style.display=preview?'block':'none';actionPanel.replaceChildren();
 if(!preview)return;
 const heading=document.createElement('div');heading.style.cssText='display:flex;gap:16px;align-items:center;justify-content:space-between';
 const title=document.createElement('strong');title.textContent=preview.primary.replaceAll('?','').toUpperCase();
 title.style.cssText='font-size:20px;letter-spacing:.04em;color:'+(['stop','hold','brake'].includes(preview.primary)?'#ffb36b':'#66e1a1');
 const tag=document.createElement('span');tag.textContent='PREVIEW';tag.style.cssText='font-size:10px;letter-spacing:.1em;color:#8291a4';
 heading.append(title,tag);
 const reason=document.createElement('div');reason.textContent=preview.reason;reason.style.cssText='margin-top:4px;color:#cbd5e1';
 const paths=document.createElement('div');paths.style.cssText='margin-top:8px;padding-top:7px;border-top:1px solid #334155;color:#9bd2ff';
 paths.textContent=preview.paths.length?preview.paths.map(p=>({straight:'↑ Straight',left:'← Left',right:'→ Right'})[p.direction]+(p.blocked?' · blocked':p.partial?' · possible':'')).join('   '):({segmentation_off:'Enable Road / sky for paths',calibration_missing:'Waiting for calibration',bumper_offset_missing:'Set bumper offset',no_supported_corridor:'No clear path detected',ground_unavailable:'Road projection unavailable'})[preview.path_status]||'No clear path detected';
 actionPanel.append(heading,reason,paths);
}
function updateTrafficLights(scene){
 const colors={red:'#ff4c4c',yellow:'#ffd84d',green:'#66e1a1'};
 const lights=(scene?.lights||[]).filter(color=>colors[color]);
 trafficLightRow.replaceChildren();
 trafficLightRow.style.display=lights.length?'flex':'none';
 trafficLightRow.setAttribute('aria-label',lights.join(', '));
 for(const color of lights){
  const dot=document.createElement('span');
  dot.style.cssText='display:block;width:14px;height:14px;border-radius:50%;background:'+colors[color];
  trafficLightRow.append(dot);
 }
 const dominant=scene?.dominant_light;
 if(colors[dominant]){
  const dot=document.createElement('span');
  dot.style.cssText='display:block;width:19px;height:19px;border-radius:50%;margin-left:6px;box-shadow:0 0 0 2px rgba(255,255,255,.65);background:'+colors[dominant];
  dot.setAttribute('aria-label','Dominant '+dominant);
  trafficLightRow.append(dot);
 }
}
updateTrafficLights(null);
const sceneLayoutStyle=document.createElement('style');
sceneLayoutStyle.textContent='.scene-layout{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:16px;align-items:start;margin:16px 0}.scene-layout .video{min-width:0}@media(max-width:900px){.scene-layout{grid-template-columns:1fr}.scene-layout section{max-width:460px;width:100%;box-sizing:border-box}}';
document.head.append(sceneLayoutStyle);
function sizeTopDownPanel(){
 topDownPanel.style.height=window.innerWidth>900?cameraPanel.getBoundingClientRect().height+'px':'auto';
 topDownCanvas.style.height=window.innerWidth>900?'100%':'520px';
 drawTopDown(lastTopDownScene);
}
new ResizeObserver(sizeTopDownPanel).observe(cameraPanel);
window.addEventListener('resize',sizeTopDownPanel);

const topDownCanvas=topDownPanel.querySelector('canvas'),topDownContext=topDownCanvas.getContext('2d');
let lastTopDownScene=null,segmentationImage=null,segmentationUrl=null;
function drawTopDown(scene){
 lastTopDownScene=scene;updateTrafficLights(scene);updateActions(scene);
 const rect=topDownCanvas.getBoundingClientRect(),w=rect.width||340,h=rect.height||520;
 const ratio=window.devicePixelRatio||1;
 const pixelWidth=Math.round(w*ratio),pixelHeight=Math.round(h*ratio);
 if(topDownCanvas.width!==pixelWidth||topDownCanvas.height!==pixelHeight){topDownCanvas.width=pixelWidth;topDownCanvas.height=pixelHeight;}
 const ctx=topDownContext,scale=Math.max(1,(h-44)/70),origin=h-24;
 ctx.setTransform(ratio,0,0,ratio,0,0);
 const point=(forward,left)=>[w/2-left*scale,origin-forward*scale];
 ctx.fillStyle='#101722';ctx.fillRect(0,0,w,h);
 if(scene?.segmentation!==segmentationUrl){
  segmentationUrl=scene?.segmentation;
  if(!segmentationUrl)segmentationImage=null;
  if(segmentationUrl){
   const url=segmentationUrl,img=new Image();
   img.onload=()=>{if(segmentationUrl===url){segmentationImage=img;drawTopDown(lastTopDownScene);}};
   img.src=url;
  }
 }
 if(segmentationImage)ctx.drawImage(segmentationImage,w/2-20*scale,origin-70*scale,40*scale,70*scale);
 ctx.font='11px system-ui';ctx.lineWidth=1;
 for(let distance=0;distance<=70;distance+=10){
  const y=point(distance,0)[1];ctx.strokeStyle='#253445';ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();
  ctx.fillStyle='#9cabbc';ctx.fillText(distance+' m',7,y-5);
 }
 if(scene){
  (scene.lanes||[]).forEach((line,index)=>{
   if((scene.probabilities||[])[index]<.05)return;
   ctx.strokeStyle='rgba(255,255,255,'+Math.max(.15,Math.min(1,(scene.probabilities||[])[index]||0))+')';ctx.lineWidth=2;ctx.beginPath();
   let drawing=false;
   (line.x||[]).forEach((x,i)=>{
    const y=(line.y||[])[i];
    if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>70){drawing=false;return;}
    const p=point(x-(scene.bumper_offset||0),-y);if(drawing)ctx.lineTo(...p);else ctx.moveTo(...p);drawing=true;
   });ctx.stroke();
  });
  for(const edge of scene.our_edges||[]){
   ctx.save();ctx.strokeStyle='#00dcdc';ctx.lineWidth=2;ctx.beginPath();
   edge.forEach((p,i)=>{if(i)ctx.lineTo(...point(...p));else ctx.moveTo(...point(...p));});ctx.stroke();ctx.restore();
  }
  for(const path of scene.action_preview?.show_paths ? scene.action_preview.paths : []){
   ctx.save();
   if(path.selected){
    const start=point(0,0),end=point(...path.points[path.points.length-1]);
    const gradient=ctx.createLinearGradient(...start,...end);gradient.addColorStop(0,'#41e150');gradient.addColorStop(1,'#4bbfff');
    ctx.strokeStyle=gradient;ctx.lineCap='round';ctx.lineJoin='round';
    const draw=()=>{ctx.beginPath();ctx.moveTo(...start);path.points.forEach(p=>ctx.lineTo(...point(...p)));ctx.stroke();};
    ctx.globalAlpha=.3;ctx.lineWidth=1.8*scale;draw();ctx.globalAlpha=1;ctx.lineWidth=3;draw();
    ctx.fillStyle='#41e150';ctx.beginPath();ctx.arc(...start,5,0,Math.PI*2);ctx.fill();
   }else{
    ctx.strokeStyle=path.blocked?'#ff9d45':'#74ccff';ctx.lineWidth=2;ctx.setLineDash([5,4]);ctx.beginPath();
    path.points.forEach(([forward,left],i)=>{const p=point(forward,left);if(i)ctx.lineTo(...p);else ctx.moveTo(...p);});ctx.stroke();
   }
   ctx.restore();
   const end=path.points[path.points.length-1];
   ctx.fillStyle=path.blocked?'#ff9d45':'#74ccff';ctx.fillText(path.direction+(path.partial?' · possible':''),...point(...end));
  }
  (scene.radar||[]).forEach(track=>{
   if(track.forward<0||track.forward>70)return;
   const [x,y]=point(track.forward,track.left);
   ctx.strokeStyle=({radar:'#ff50ff',camera:'#00dcff',candidate_radar:'#ffa000'})[track.source]||'#aaa';
   ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x,y-5);ctx.lineTo(x+5,y);ctx.lineTo(x,y+5);ctx.lineTo(x-5,y);ctx.closePath();ctx.stroke();
  });
  (scene.cars||[]).forEach(car=>{
   if(car.forward<0||car.forward>70||Math.abs(car.left)>22)return;
   const [x,y]=point(car.forward,car.left);
   ctx.fillStyle=car.lane==='ego lane'?'#66e1a1':car.lane==='lane unknown'?'#a0a8b4':'#ffcf62';
   const length=car.type==='bus'||car.type==='truck'?6:4;
   ctx.save();ctx.translate(x,y);ctx.rotate(Number.isFinite(car.heading)?car.heading:0);
   ctx.fillRect(-.9*scale,-length*scale/2,1.8*scale,length*scale);
   ctx.restore();
   ctx.fillStyle='#eaf0f6';ctx.fillText(car.id===null?car.type:'ID '+car.id,x+1.2*scale,y+4);
  });
 }
 const [x,y]=point(0,0);ctx.fillStyle='#5aaaff';ctx.fillRect(x-.9*scale,y-2*scale,1.8*scale,4*scale);ctx.fillStyle='#eaf0f6';ctx.fillText('YOU',x+15,y+4);
 if(!scene){ctx.fillStyle='#9cabbc';ctx.fillText('Waiting for camera and lane data',85,35);}
}
drawTopDown(null);

// Render only the newest scene per browser paint; never accumulate old scenes.
let pendingTopDown=null,topDownPaint=null;
const topDownStream=new EventSource('/top-down-stream');
topDownStream.onmessage=event=>{
 pendingTopDown=JSON.parse(event.data);
 if(topDownPaint===null)topDownPaint=requestAnimationFrame(()=>{topDownPaint=null;drawTopDown(pendingTopDown);});
};
window.addEventListener('pagehide',()=>{topDownStream.close();if(topDownPaint!==null)cancelAnimationFrame(topDownPaint);});

// Visible, aligned controls with one consistent layout.
const viewerHeader=document.querySelector('header');
const primaryControls=viewerHeader.querySelector('.controls');
const settingsPanel=document.createElement('div');settingsPanel.className='viewer-settings';
function settingsSection(title,nodes){
 const section=document.createElement('div');section.className='settings-section';section.setAttribute('role','group');section.setAttribute('aria-label',title);
 const content=document.createElement('div');content.className='settings-content';
 for(const node of nodes)if(node)content.append(node);
 section.append(content);settingsPanel.append(section);return section;
}
const featureControls=document.createElement('div');featureControls.className='controls';
for(const id of ['feature-objects','feature-masks','feature-scene'])featureControls.append(document.getElementById(id).closest('label'));
featureControls.append(segmentationSource);
settingsSection('Detection',[featureControls]);
const displayControls=document.createElement('div');displayControls.className='controls';
displayControls.append(objectModeLabel,commaOverlay.closest('label'),annotationControls);
const displaySection=settingsSection('Overlays',[displayControls,document.querySelector('.opacity-controls'),laneStyleControls]);
displaySection.classList.add('wide-settings');
settingsSection('Areas',[areaControls]);
const sidesSection=settingsSection('Side cameras',[sideControls]);
sidesSection.classList.add('wide-settings');
const connectionSection=settingsSection('Source & calibration',[bumperLabel,document.querySelector('#connection')]);
connectionSection.classList.add('full-settings');
viewerHeader.append(settingsPanel);
primaryControls.prepend(camera,modelSize);
button.classList.add('primary-action');
const cleanStyle=document.createElement('style');
cleanStyle.textContent=`
body{background:#080d14}main{padding:18px 24px;max-width:none}
header{margin-bottom:12px;align-items:center;flex-wrap:wrap}header h1{font-size:21px;letter-spacing:-.5px}header p{font-size:12px}
.controls{gap:10px}button,select{padding:9px 12px;font-size:13px;border-radius:8px}
button{background:#243244;color:#eaf0f6;border:1px solid #35465c}button:hover{background:#30425a}.primary-action{background:#66e1a1;color:#09120e;border-color:#66e1a1;min-width:88px}
.video{border-radius:10px}.scene-layout{margin:12px 0;gap:12px;grid-template-columns:minmax(0,1fr) 340px}
header{display:flex;gap:8px 16px;padding:12px;background:#101722;border:1px solid #263241;border-radius:10px;justify-content:flex-start;align-items:center}
header .controls{gap:8px;flex-wrap:wrap}header select,header button{font-size:12px;padding:7px 9px}
.viewer-settings{display:contents}
.settings-section{display:contents}.settings-content{display:contents}
.settings-content .controls,.settings-content .opacity-controls,.settings-content .side-controls{display:flex;align-items:center;flex-wrap:wrap;gap:8px 12px;margin:0;width:auto;max-width:none}
.settings-content .controls,.settings-content .opacity-controls,.settings-content .side-controls{padding-left:12px;border-left:1px solid #334155}
.settings-content label,.settings-content .overlay-toggle{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:#ccd6e3;white-space:nowrap}
.settings-content input[type=checkbox]{margin:0;width:14px;height:14px}
.settings-content .opacity-controls label{display:inline-flex;gap:6px}
.settings-content input[type=range]{width:72px;min-width:0;padding:0}
.settings-content output{font-size:11px;color:#94a3b8;width:34px;text-align:right}
.settings-content #connection{margin:0;gap:8px}.settings-content #connection input{width:160px;max-width:100%;padding:7px;font-size:12px}
.settings-content button{white-space:nowrap}
.settings-content .side-column{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.settings-content .side-column label{display:inline-flex}
.settings-content .side-column strong{font-size:11px;color:#8494a8}
.settings-content .side-controls>span{font-size:11px;color:#8494a8}
.settings-content #bumper-offset{width:64px!important;padding:6px;font-size:12px}
@media(max-width:600px){header{padding:10px}header .controls{width:auto}.settings-content .controls,.settings-content .opacity-controls{padding-left:0;border-left:0}}
footer{margin-top:8px;font-size:12px;gap:14px}#status{font-size:12px;margin-top:10px;line-height:1.5}
.replay-controls{margin:0 0 12px;font-size:12px}.replay-controls span{color:#94a3b8}
@media(max-width:900px){.scene-layout{grid-template-columns:1fr}}
@media(max-width:600px){main{padding:12px}header .controls{width:100%}header .controls select{flex:1;min-width:0}.opacity-controls label{flex-wrap:wrap}}
`;
document.head.append(cleanStyle);
annotationControls.style.flexWrap='wrap';
annotationControls.style.gap='12px 18px';

function controlLabel(id,text){
 const input=document.getElementById(id),label=input?.closest('label');
 if(!label)return;
 for(const node of label.childNodes)if(node.nodeType===Node.TEXT_NODE)node.textContent='';
 const caption=document.createTextNode(text+' ');
 if(input.type==='checkbox')label.append(caption);else label.insertBefore(caption,label.firstChild);
}
for(const [id,text] of Object.entries({'feature-masks':'Masks','feature-scene':'Road / sky','comma-overlay':'Lanes / edges','show-boxes':'Boxes','show-motion':'Motion','road-signals':'Lights / signs','show-radar':'Radar','seg-opacity':'Scene','lane-opacity':'Areas','lane-ui-width':'Lane width','lane-ui-opacity':'Lanes'}))controlLabel(id,text);
document.getElementById('add-area').textContent='Add area';
document.getElementById('remove-area').textContent='Delete area';
viewerHeader.querySelector('h1').parentElement.remove();

const routeForm=document.createElement('form');routeForm.className='controls';
routeForm.innerHTML='<input aria-label="Replay route" id="replay-route" placeholder="dongle/route/segment" style="width:300px;max-width:55vw;font-size:12px;padding:7px"><button type="submit">Connect route</button>';
primaryControls.append(routeForm);
const connectionForm=document.querySelector('#connection');primaryControls.append(connectionForm);
connect.textContent='Connect IP';
connectionForm.style.cssText='display:flex;gap:8px;margin:0;flex-wrap:wrap';
source.style.width='190px';
source.closest('label').firstChild.textContent='Car IP ';
source.placeholder='IP address or server URL';
fetch('/status').then(r=>r.json()).then(s=>{
 document.getElementById('replay-route').value=s.replay_route||'d59ca223dca8da93/00000498--3190be1e8b/6';
 if(s.input_mode==='idle')waiting.textContent='Choose a route or car address, then Connect.';
});
async function connectInput(mode,route){
 const response=await fetch('/input-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode,...(route?{route}:{})})});
 if(!response.ok)throw Error('Could not connect input; check the route or address');
}
routeForm.onsubmit=async event=>{
 event.preventDefault();const submit=routeForm.querySelector('button');submit.disabled=true;
 try{await connectInput('replay',document.getElementById('replay-route').value.trim());}
 catch(error){document.querySelector('#status').textContent=error.message;submit.disabled=false;}
};
connectionForm.onsubmit=async event=>{
 event.preventDefault();connect.disabled=true;
 try{
  const response=await fetch('/source',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source:source.value})});
  if(!response.ok)throw Error('Invalid car address');
  await connectInput('live');
 }catch(error){document.querySelector('#status').textContent=error.message;connect.disabled=false;}
};
