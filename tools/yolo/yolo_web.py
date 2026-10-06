"""YOLO browser server, sunnydrive transport, and calibrated lane overlays."""
import fcntl
import json
import os
from pathlib import Path
import secrets
import socket
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlsplit

import cv2
import numpy as np

MODELS = {}  # Populated by the YOLO viewer.

WEB_PAGE = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>sunnydrive · Road segmentation</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#0b1016;color:#eaf0f6;font:15px system-ui,sans-serif}
main{max-width:1440px;margin:auto;padding:28px}header{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:24px}
h1{font-size:24px;margin:0 0 6px}p{margin:0;color:#94a3b8}button{background:#66e1a1;color:#09120e;border:0;border-radius:10px;padding:12px 22px;font:600 15px system-ui;cursor:pointer}
.controls{display:flex;align-items:center;gap:12px;flex-wrap:wrap}select{background:#141c26;color:#eaf0f6;border:1px solid #334155;border-radius:10px;padding:11px;font:15px system-ui}.overlay-toggle{white-space:nowrap}input[type=checkbox]{width:auto;accent-color:#66e1a1}
.video{background:#141c26;border:1px solid #263241;border-radius:16px;overflow:hidden;position:relative;min-height:220px;aspect-ratio:16/9;max-height:calc(100dvh - 210px);display:grid;place-items:center}
img{width:100%;height:100%;object-fit:contain;position:absolute;inset:0}#waiting{padding:28px;text-align:center;z-index:1;background:#141c26}
footer{display:flex;flex-wrap:wrap;gap:22px;margin-top:18px;color:#a9b6c7}.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px}
#stats{margin-left:auto;color:#eaf0f6;font-variant-numeric:tabular-nums}#status{margin-top:15px}#button:disabled{opacity:.5;cursor:wait}
#connection{display:flex;align-items:center;gap:12px;margin-top:16px;flex-wrap:wrap}#connection label{display:flex;align-items:center;gap:12px;color:#94a3b8}input{background:#141c26;color:#eaf0f6;border:1px solid #334155;border-radius:8px;padding:9px;width:360px;max-width:55vw;font:14px system-ui}#connect{padding:9px 15px}#ip{color:#94a3b8;font-size:13px}
.opacity-controls{display:flex;gap:28px;flex-wrap:wrap;margin-top:16px}.opacity-controls label{display:flex;align-items:center;gap:10px;color:#a9b6c7}.opacity-controls input{width:160px;padding:0;accent-color:#66e1a1}.opacity-controls output{width:42px;font-variant-numeric:tabular-nums}
@media(max-width:600px){main{padding:16px}h1{font-size:20px}#stats{margin-left:0}}
</style><main><header><div><h1>sunnydrive road segmentation</h1><p>Live comma camera · processing on your Mac</p></div><div class="controls"><select id="model" aria-label="Model">MODEL_OPTIONS</select><select id="camera" aria-label="Camera"><option value="road">Road camera</option><option value="wideRoad">Wide road camera</option></select><label class="overlay-toggle"><input id="comma-overlay" type="checkbox"> Comma overlay</label><button id="button" disabled>Pause</button></div></header>
<div class="video"><img id="video" alt="Live road segmentation overlay"><div id="waiting">Choose a route or car address, then Connect.</div></div>
<footer id="legend"></footer><div class="opacity-controls"><label>Segmentation opacity <input id="seg-opacity" aria-label="Segmentation opacity" type="range" min="0" max="100" value="45"><output id="seg-value">45%</output></label><label>Lane UI opacity <input id="lane-opacity" aria-label="Lane UI opacity" type="range" min="0" max="100" value="100"><output id="lane-value">100%</output></label></div><form id="connection"><label>Comma address <input id="source" aria-label="Comma address" placeholder="IP address or server URL" required></label><button id="connect">Connect</button><button id="lan" type="button">Use LAN IP</button><span id="ip"></span></form><p id="status" role="status">Starting…</p></main>
<script>
const button=document.querySelector('#button'),waiting=document.querySelector('#waiting'),video=document.querySelector('#video'),camera=document.querySelector('#camera'),model=document.querySelector('#model');
const source=document.querySelector('#source'),connect=document.querySelector('#connect');
const segOpacity=document.querySelector('#seg-opacity'),laneOpacity=document.querySelector('#lane-opacity');let opacityTimer,opacityEdited=false,viewerBoot=null;
function opacityLabels(){document.querySelector('#seg-value').textContent=segOpacity.value+'%';document.querySelector('#lane-value').textContent=laneOpacity.value+'%';}
segOpacity.oninput=laneOpacity.oninput=()=>{opacityEdited=true;opacityLabels();clearTimeout(opacityTimer);opacityTimer=setTimeout(()=>fetch('/opacity',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({segmentation:Number(segOpacity.value)/100,comma:Number(laneOpacity.value)/100})}),50);};
const commaOverlay=document.querySelector('#comma-overlay');commaOverlay.onchange=async()=>{await fetch('/overlay',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({overlay:commaOverlay.checked})});await update();};
document.querySelector('#lan').onclick=()=>{source.value='10.83.106.109';document.querySelector('#connection').requestSubmit();};
video.onload=()=>waiting.hidden=true;video.src='/video';
button.onclick=async()=>{button.disabled=true;try{const r=await fetch('/toggle',{method:'POST'});if(!r.ok)throw Error('Control failed');}finally{await update();}};
camera.onchange=async()=>{camera.disabled=true;try{const r=await fetch('/camera',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({camera:camera.value})});if(!r.ok)throw Error('Camera switch failed');}finally{camera.disabled=false;await update();}};
model.onchange=async()=>{model.disabled=true;try{const r=await fetch('/model',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model:model.value})});if(!r.ok)throw Error('Model switch failed');}finally{model.disabled=false;await update();}};
document.querySelector('#connection').onsubmit=async e=>{e.preventDefault();connect.disabled=true;try{const r=await fetch('/source',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source:source.value})});if(!r.ok)throw Error('Use an http:// or https:// comma address');}catch(e){document.querySelector('#status').textContent=e.message;}finally{connect.disabled=false;}};
async function update(){try{const r=await fetch('/status',{cache:'no-store'});const s=await r.json();
if(viewerBoot!==null&&viewerBoot!==s.viewer_boot){location.reload();return;}viewerBoot=s.viewer_boot;
document.querySelector('#status').textContent=(s.connection_message||s.message)+(s.input_mode!=='idle'&&s.comma_overlay&&!s.comma_overlay_ready?' · Waiting for comma model / calibration':'');button.disabled=!s.ready;button.textContent=s.paused?'Resume':'Pause';if(!camera.disabled)camera.value=s.camera;if(!model.disabled)model.value=s.requested_model;
if(document.activeElement!==source&&!connect.disabled)source.value=s.comma_url;document.querySelector('#ip').textContent=s.input_mode==='idle'?'':s.comma_ip?`IP: ${s.comma_ip}`:(s.ready?'Connected':'Connecting…');
commaOverlay.checked=s.comma_overlay;
if(!opacityEdited){segOpacity.value=Math.round(s.segmentation_opacity*100);laneOpacity.value=Math.round(s.comma_opacity*100);}opacityLabels();
waiting.hidden=!!s.ready;
if(!s.ready){waiting.textContent=s.connection_message||s.message;}
const colors=s.model==='comma10k'?[['Road','#3cc83c'],['Lane markings','#ffdc00'],['Vehicles / people','#f0aa14'],['Your car','#b450c8']]:[['Road','#3cc83c'],['Sidewalk','#b450c8'],['People','#f03232'],['Vehicles','#f0aa14']];
if(s.comma_overlay)colors.push(['Comma lanes','#ffffff'],['Road edges','#ff8000'],['Model path','#409dff']);
const legend=document.querySelector('#legend');legend.replaceChildren();for(const [label,color] of colors){const span=document.createElement('span'),dot=document.createElement('i');dot.className='dot';dot.style.background=color;span.append(dot,document.createTextNode(label));legend.append(span);}
const stats=document.createElement('span');stats.id='stats';stats.textContent=s.fps?`${s.fps.toFixed(1)} processing FPS · ${s.age_ms} ms since decode`:'';legend.append(stats);
}catch(e){document.querySelector('#status').textContent='Viewer disconnected. Restart the command in Terminal.';button.disabled=true;}}
update();setInterval(update,750);
</script></html>""".replace("MODEL_OPTIONS", "".join(f'<option value="{key}">{name}</option>' for key, name in MODELS.items()))


def acquire_viewer_lock():
  """One Mac web inference viewer, regardless of task or HTTP port."""
  handle = open(f"/tmp/sunnydrive-viewer-{os.getuid()}.lock", "a+")
  try:
    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
  except BlockingIOError:
    handle.close()
    raise SystemExit("A sunnydrive web viewer is already running. Stop it before starting another.") from None
  return handle


def open_viewer_if_absent(address, browser_seen):
  # Existing viewer tabs poll status, including after their server restarts.
  if not browser_seen.wait(timeout=3):
    webbrowser.open(address)


def start_web(args):
  if not getattr(args, "viewer_lock", None):
    args.viewer_lock = acquire_viewer_lock()
  changed = threading.Condition()
  browser_seen = threading.Event()
  enabled = threading.Event()
  enabled.set()
  state = {"model": args.model, "requested_model": args.model, "camera": args.camera, "comma_url": args.comma, "comma_ip": "", "comma_overlay": False, "comma_overlay_ready": False, "segmentation_opacity": .45, "comma_opacity": 1., "ready": False, "paused": False, "fps": 0, "age_ms": 0,
           "message": "Connecting / pairing: approve 'Mac road segmentation' on the comma if prompted."}
  state["viewer_boot"] = secrets.token_hex(8)
  state["input_mode"]="idle" if args.idle else "replay" if args.replay else "live"
  state["replay_route"]=args.route or args.replay_route or "d59ca223dca8da93/00000498--3190be1e8b/6"
  if args.idle:state["message"]="Choose a route or car address, then Connect."
  frame = [None, 0]

  class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
      pass

    def do_GET(self):
      if self.path == "/top-down-stream" and getattr(args,"custom_masks",False):
        self.send_response(200)
        self.send_header("Content-Type","text/event-stream")
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.connection.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        version=-1
        try:
          while True:
            with changed:
              updated=changed.wait_for(lambda:frame[1]!=version,timeout=15)
              if updated:
                version=frame[1]
                payload=json.dumps(state.get("top_down"),separators=(",",":"))
            self.wfile.write((f"data: {payload}\n\n" if updated else ": keepalive\n\n").encode())
            self.wfile.flush()
        except (BrokenPipeError,ConnectionResetError):
          return
      elif self.path == "/video":
        self.connection.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        version = 0
        try:
          while True:
            with changed:
              if not changed.wait_for(lambda: frame[1] != version, timeout=15):
                continue
              jpeg, version = frame
            self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: " + str(len(jpeg)).encode() + b"\r\n\r\n" + jpeg + b"\r\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
          return
      elif self.path in ("/", "/status"):
        if "Mozilla/" in self.headers.get("User-Agent",""):
          browser_seen.set()
        with changed:
          if getattr(args,"get_replay_paused",None):
            state["paused"]=args.get_replay_paused()
          body = WEB_PAGE.encode() if self.path == "/" else json.dumps(state).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8" if self.path == "/" else "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
      else:
        self.send_error(404)

    def do_POST(self):
      if self.path not in ("/input-mode", "/toggle", "/camera", "/model", "/source", "/overlay", "/opacity", "/masks", "/rotation", "/position", "/replay-key", "/mask-mode", "/lane-style", "/bumper-offset", "/object-mode", "/annotations", "/features"):
        return self.send_error(404)
      # Only the local viewer may control inference; reject cross-site requests.
      if self.headers.get("Origin") != f"http://127.0.0.1:{args.port}":
        return self.send_error(403)
      if self.path == "/input-mode":
        try:
          length=int(self.headers.get('Content-Length','0'))
          if not 0<length<=256:raise ValueError('Invalid request size')
          body=json.loads(self.rfile.read(length))
          mode=body['mode']
          route=body.get('route')
          if route is not None:
            import re
            if not isinstance(route,str) or not re.fullmatch(r'[a-f0-9]{16}[/|][A-Za-z0-9_-]+(?:/\d+)?',route):
              raise ValueError('Invalid route')
          if mode not in ('live','replay'):raise ValueError('Invalid input mode')
          if not getattr(args,'switch_input',None):raise ValueError('Mode switching unavailable')
        except (ValueError,KeyError,TypeError):
          return self.send_error(400)
        switching=args.idle or (mode=='replay')!=args.replay or route is not None
        if route is not None:args.route=route
        if switching:
          with changed:state.update(ready=False,message='Switching to '+mode+'…')
        self.send_response(204);self.end_headers()
        if switching:threading.Timer(.25,args.switch_input,args=(mode,)).start()
        return
      if self.path == "/features":
        if not getattr(args,"feature_selection",None):
          return self.send_error(404)
        try:
          length=int(self.headers.get("Content-Length","0"))
          if not 0<length<=256:
            raise ValueError("Invalid request size")
          body=json.loads(self.rfile.read(length))
          size=body["size"]
          objects,masks,scene=(body[key] for key in ("objects","masks","scene"))
          if size not in ('n','s','m','l','x') or any(type(value) is not bool for value in (objects,masks,scene)):
            raise ValueError("Invalid model features")
          source=body.get('segmentation_source',args.segmentation_source)
          if source not in ('yolo','comma10k'):
            raise ValueError("Invalid segmentation source")
          selection=args.feature_selection(size,objects,masks,scene)
        except (ValueError,KeyError,TypeError):
          return self.send_error(400)
        with changed:
          if args.model==selection and args.segmentation_source==source:
            self.send_response(204)
            self.end_headers()
            return
          state['connection_message']=''
          args.model=selection
          args.segmentation_source=source
          state['segmentation_source']=source
          if not masks:
            state['object_mode']='full'
          if getattr(args,'save_selection',None):
            args.save_selection()
          state.update(requested_model=selection,ready=False,message="Updating model features…")
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/annotations":
        if not getattr(args,"custom_masks",False):
          return self.send_error(404)
        try:
          size=int(self.headers.get("Content-Length","0"))
          if not 0<size<=256:
            raise ValueError("Invalid request size")
          body=json.loads(self.rfile.read(size))
          labels,boxes=body["labels"],body["boxes"]
          motion=body.get("motion",True)
          signals=body.get("signals",True)
          radar=body.get("radar",True)
          hide_stationary=body.get("hide_stationary",False)
          top_seg=body.get("top_seg",False)
          actions=body.get("actions",True)
          our_edges=body.get("our_edges",False)
          if type(labels) is not bool or type(boxes) is not bool or type(motion) is not bool or type(signals) is not bool or type(radar) is not bool or type(hide_stationary) is not bool or type(top_seg) is not bool or type(actions) is not bool or type(our_edges) is not bool:
            raise ValueError("Invalid annotation visibility")
        except (ValueError,KeyError,TypeError):
          return self.send_error(400)
        with changed:
          state.update(show_labels=labels,show_boxes=boxes,show_motion=motion,road_signals=signals,show_radar=radar,hide_stationary=hide_stationary,show_top_seg=top_seg,show_actions=actions,show_our_edges=our_edges)
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/object-mode":
        if not getattr(args,"custom_masks",False):
          return self.send_error(404)
        try:
          size=int(self.headers.get("Content-Length","0"))
          if not 0<size<=64:
            raise ValueError("Invalid request size")
          value=json.loads(self.rfile.read(size))["mode"]
          if value not in ("full","masked","original"):
            raise ValueError("Invalid object display mode")
        except (ValueError,KeyError,TypeError):
          return self.send_error(400)
        with changed:
          state["object_mode"]=value
          if value!="full" and getattr(args,"feature_selection",None):
            task,size=args.model.split('-')
            args.model=args.feature_selection(size,True,True,task in ('scene','sceneMask','semantic'))
            if getattr(args,"save_selection",None):
              args.save_selection()
            state.update(requested_model=args.model,ready=False,message="Loading object instance masks…")
          elif value!="full" and not args.model.startswith("segment-"):
            args.model="segment-"+args.model.rsplit("-",1)[1]
            if getattr(args,"save_selection",None):
              args.save_selection()
            state.update(requested_model=args.model,ready=False,message="Loading object instance masks…")
            enabled.set()
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/bumper-offset":
        if not getattr(args,"custom_masks",False):
          return self.send_error(404)
        try:
          size=int(self.headers.get("Content-Length","0"))
          if not 0<size<=256:
            raise ValueError("Invalid request size")
          value=json.loads(self.rfile.read(size))["meters"]
          if value is not None and (type(value) not in (int,float) or not np.isfinite(value) or not 0<=value<=5):
            raise ValueError("Invalid bumper offset")
        except (ValueError,KeyError,TypeError):
          return self.send_error(400)
        with changed:
          state["bumper_offset"]=value
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/lane-style":
        if not getattr(args,"custom_masks",False):
          return self.send_error(404)
        try:
          size=int(self.headers.get("Content-Length","0"))
          if not 0<size<=256:
            raise ValueError("Invalid request size")
          body=json.loads(self.rfile.read(size))
          width,opacity=body["width"],body["opacity"]
          if type(width) is not int or not 1<=width<=16:
            raise ValueError("Invalid lane width")
          if type(opacity) not in (int,float) or not np.isfinite(opacity) or not 0<=opacity<=1:
            raise ValueError("Invalid lane opacity")
        except (ValueError,KeyError,TypeError):
          return self.send_error(400)
        with changed:
          state.update(lane_width=width,lane_opacity=opacity)
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/mask-mode":
        if not getattr(args, "custom_masks", False):
          return self.send_error(404)
        try:
          size = int(self.headers.get("Content-Length", "0"))
          if not 0 < size <= 128:
            raise ValueError("Invalid request size")
          body = json.loads(self.rfile.read(size))
          mode = body["mode"]
          camera = body.get("camera",args.camera)
          if camera not in args.camera_choices:
            raise ValueError("Unknown camera")
          if mode not in ("exclude", "keep"):
            raise ValueError("Choose exclude or keep")
        except (ValueError, KeyError, TypeError):
          return self.send_error(400)
        with changed:
          state.setdefault("mask_modes", {})[camera] = mode
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/replay-key":
        if not getattr(args, "send_replay_key", None):
          return self.send_error(409, "This viewer did not launch the replay")
        try:
          size = int(self.headers.get("Content-Length", "0"))
          if not 0 < size <= 128:
            raise ValueError("Invalid request size")
          key = json.loads(self.rfile.read(size))["key"]
          if not isinstance(key, str) or key not in (" ","s","S","m","M","e","d","t","i","w","c","+","-","q"):
            raise ValueError("Unknown replay shortcut")
          args.send_replay_key(key)
        except (ValueError, KeyError, TypeError):
          return self.send_error(400)
        except (OSError, RuntimeError):
          return self.send_error(409, "Replay is no longer running")
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/position":
        if not getattr(args, "custom_masks", False):
          return self.send_error(404)
        try:
          size = int(self.headers.get("Content-Length", "0"))
          if not 0 < size <= 1024:
            raise ValueError("Invalid request size")
          body = json.loads(self.rfile.read(size))
          positions = {side: body[side] for side in ("left", "right")}
          if any(not isinstance(p, list) or len(p) != 2 or any(type(v) not in (int, float) or not np.isfinite(v) or not -.5 <= v <= .5 for v in p) for p in positions.values()):
            raise ValueError("Position must be between -50% and 50%")
        except (ValueError, KeyError, TypeError):
          return self.send_error(400)
        with changed:
          state["side_position"] = positions
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/rotation":
        if not getattr(args, "custom_masks", False):
          return self.send_error(404)
        try:
          size = int(self.headers.get("Content-Length", "0"))
          if not 0 < size <= 1024:
            raise ValueError("Invalid request size")
          body = json.loads(self.rfile.read(size))
          angles = {side: body[side] for side in ("left", "right")}
          if any(type(v) not in (int, float) or not np.isfinite(v) or not -180 <= v <= 180 for v in angles.values()):
            raise ValueError("Rotation must be between -180 and 180 degrees")
        except (ValueError, KeyError, TypeError):
          return self.send_error(400)
        with changed:
          state["side_rotation"] = angles
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/masks":
        if not getattr(args, "custom_masks", False):
          return self.send_error(404)
        try:
          size = int(self.headers.get("Content-Length", "0"))
          if not 0 < size <= 32768:
            raise ValueError("Invalid request size")
          body = json.loads(self.rfile.read(size))
          camera, polygons = body["camera"], body["polygons"]
          layout = body.get("layout")
          sides = body.get("sides")
          if sides is not None and (not isinstance(sides,list) or len(sides)!=len(polygons) or any(side not in (None,"left","right") for side in sides)):
            raise ValueError("Invalid mask attachment")
          if layout is not None:
            for side in ("left", "right"):
              angle,position = layout["rotation"][side],layout["position"][side]
              if type(angle) not in (int,float) or not np.isfinite(angle) or not -180 <= angle <= 180:
                raise ValueError("Invalid mask rotation")
              if not isinstance(position,list) or len(position)!=2 or any(type(v) not in (int,float) or not np.isfinite(v) or not -.5 <= v <= .5 for v in position):
                raise ValueError("Invalid mask position")
          if camera not in args.camera_choices or not isinstance(polygons, list) or len(polygons) > 16:
            raise ValueError("Invalid masks")
          for polygon in polygons:
            if not isinstance(polygon, list) or not 3 <= len(polygon) <= 32:
              raise ValueError("Invalid polygon")
            if any(not isinstance(p, list) or len(p) != 2 or any(type(v) not in (int, float) or not np.isfinite(v) or not -10 <= v <= 10 for v in p) for p in polygon):
              raise ValueError("Invalid coordinates")
        except (ValueError, KeyError, TypeError):
          return self.send_error(400)
        with changed:
          state.setdefault("blackout_areas", {})[camera] = polygons
          state.setdefault("mask_layouts", {})[camera] = layout
          state.setdefault("mask_sides", {})[camera] = sides
        self.send_response(204)
        self.end_headers()
        return
      if self.path == "/opacity":
        try:
          size = int(self.headers.get("Content-Length", "0"))
          if not 0 < size <= 1024:
            raise ValueError("Invalid request length")
          body = json.loads(self.rfile.read(size))
          values = [body["segmentation"], body["comma"]]
          if any(type(value) not in (int, float) or not np.isfinite(value) or not 0 <= value <= 1 for value in values):
            raise ValueError("Opacity must be between 0 and 1")
        except (ValueError, KeyError, TypeError):
          return self.send_error(400)
        with changed:
          state.update(segmentation_opacity=values[0], comma_opacity=values[1])
        self.send_response(204)
        self.end_headers()
        return
      if self.path in ("/camera", "/model", "/source", "/overlay"):
        try:
          size = int(self.headers.get("Content-Length", "0"))
          if not 0 < size <= 1024:
            raise ValueError("Invalid request length")
          field = self.path[1:]
          value = json.loads(self.rfile.read(size))[field]
          if field == "overlay":
            if not isinstance(value, bool):
              raise ValueError("Overlay must be a boolean")
            with changed:
              state["comma_overlay"] = value
            self.send_response(204)
            self.end_headers()
            return
          choices = getattr(args, "camera_choices", ("road", "wideRoad")) if field == "camera" else MODELS
          if not isinstance(value, str):
            raise ValueError("Invalid selection")
          if field == "source":
            value = value.strip()
            if "://" not in value:
              value = "http://" + value + (":8766" if ":" not in value else "")
            parsed = urlsplit(value)
            if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
              raise ValueError("Use a comma server URL without credentials or a path")
            value = value.rstrip("/")
          elif value not in choices:
            raise ValueError("Unknown selection")
        except (ValueError, KeyError, TypeError):
          return self.send_error(400)
        with changed:
          attribute = "comma" if field == "source" else field
          if getattr(args, attribute) != value:
            setattr(args, attribute, value)
            if field=="model" and state.get("object_mode","full")!="full" and not value.startswith("segment-"):
              state["object_mode"]="full"
            if field in ("camera", "model") and getattr(args, "save_selection", None):
              args.save_selection()
            state.update(ready=False, paused=False, connection_message="", message=f"Switching {field}…")
            state[{"camera": "camera", "model": "requested_model", "source": "comma_url"}[field]] = value
            if field == "source":
              state["comma_ip"] = ""
            enabled.set()
        self.send_response(204)
        self.end_headers()
        return
      if getattr(args,"send_replay_key",None):
        try:
          args.send_replay_key(" ")
        except (OSError,RuntimeError):
          return self.send_error(409,"Replay is no longer running")
        self.send_response(204)
        self.end_headers()
        return
      with changed:
        if enabled.is_set():
          enabled.clear()
        else:
          enabled.set()
        state["paused"] = not enabled.is_set()
        state["message"] = "Paused — showing the last processed frame." if state["paused"] else "Live · segmentation runs on your Mac."
      self.send_response(204)
      self.end_headers()

  server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
  server.daemon_threads = True
  threading.Thread(target=server.serve_forever, daemon=True).start()
  address = f"http://127.0.0.1:{args.port}"
  print(f"Browser viewer: {address} (Ctrl+C to stop)", flush=True)
  if not args.no_open:
    threading.Thread(target=open_viewer_if_absent,args=(address,browser_seen),daemon=True).start()
  return state, frame, changed, enabled, server










def api(base, path, body=None):
  data = json.dumps(body).encode() if body is not None else None
  with urlopen(Request(base + path, data=data, headers={"Content-Type": "application/json"}), timeout=10) as response:
    return json.load(response)


def _save_tokens(path,saved):
  fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
  os.fchmod(fd,0o600)
  with os.fdopen(fd,'w') as out:json.dump(saved,out)


_pairing_lock=threading.Lock()


def token_for(base,path,on_status=lambda message:None):
  with _pairing_lock:
    try:
      token=_token_for(base,path,on_status)
      on_status('')
      return token
    except Exception as error:
      on_status(str(error))
      raise


def _token_for(base, path, on_status):
  path.parent.mkdir(parents=True, exist_ok=True)
  saved = json.loads(path.read_text()) if path.exists() else {}
  if base in saved:
    try:
      with urlopen(Request(base+'/alerts',headers={'Authorization':'Bearer '+saved[base]}),timeout=5):pass
      return saved[base]
    except HTTPError as error:
      if error.code!=401:raise
      saved.pop(base)
  legacy=Path('/private/tmp/roadseg-tokens.json')
  if legacy.exists() and legacy!=path:
    try:previous=json.loads(legacy.read_text())
    except (OSError,ValueError):previous={}
    for token in dict.fromkeys(previous.values()):
      try:
        with urlopen(Request(base+'/alerts',headers={'Authorization':'Bearer '+token}),timeout=5):pass
      except HTTPError as error:
        if error.code in (401,403):continue
        raise
      saved[base]=token
      _save_tokens(path,saved)
      return token
  on_status('Approve Mac YOLO viewer on the comma to connect live video.')
  request = api(base, "/pair/request", {"clientId": "mac-roadseg-" + secrets.token_hex(12), "name": "Mac YOLO viewer"})["request"]
  print("Approve 'Mac YOLO viewer' on the comma.", flush=True)
  deadline = time.monotonic() + 240
  while time.monotonic() < deadline:
    status = api(base, "/pair/status?request=" + request)
    if status["status"] == "approved":
      saved[base] = status["token"]
      _save_tokens(path,saved)
      return saved[base]
    if status["status"] == "expired":
      break
    time.sleep(1)
  raise RuntimeError("Pairing was not approved before expiry")


def read_exact(stream, size):
  data = bytearray()
  while len(data) < size:
    chunk = stream.read(size - len(data))
    if not chunk:
      raise EOFError("Comma video connection closed")
    data.extend(chunk)
  return bytes(data)


def project_comma_line(shape, calibration, line, offset=0, z_offset=0):
  height,width = shape[:2]
  ground = np.asarray(calibration["ground"], dtype=float).reshape(3,3)
  x, y = np.asarray(line.get("x", []), float), np.asarray(line.get("y", []), float)
  if x.size != y.size or not x.size:
    return np.empty((0, 2), np.int32)
  # modelV2 uses calibration coordinates (y right); ground uses road coordinates (y left).
  z = np.asarray(line.get("z", []),float)
  if "modelProjection" in calibration and z.size==x.size:
    projection = np.asarray(calibration["modelProjection"],float).reshape(3,3)
    points = np.stack((x,y+offset,z+z_offset),axis=1)
    projected = points @ projection.T
  else:
    points = np.stack((x, -(y + offset), np.ones_like(x)), axis=1)
    projected = points @ ground.T
  valid = np.isfinite(projected).all(axis=1) & (x >= .5) & (x <= 100) & (projected[:, 2] > .05)
  projected = projected[valid]
  pixels = projected[:, :2] / projected[:, 2:3]
  pixels *= [width / calibration["width"], height / calibration["height"]]
  pixels = np.clip(pixels, [-width * 4, -height * 4], [width * 4, height * 4])
  return pixels.round().astype(np.int32)


def draw_comma_overlay(image, sample, camera, opacity=1., line_width=None):
  """Project the telemetry's XY curves using its calibrated ground-plane matrix."""
  calibration = sample.get("wideRoadCamera" if camera == "wideRoad" else "roadCamera")
  model = sample.get("model")
  if not calibration or not model:
    return False
  if opacity == 0:
    return True
  before = image.copy() if opacity < 1 else None
  ground = np.asarray(calibration["ground"], dtype=float).reshape(3, 3)
  height, width = image.shape[:2]

  def project(line, offset=0, z_offset=0):
    return project_comma_line(image.shape,calibration,line,offset,z_offset)

  for line in model.get("roadEdges", []):
    points = project(line)
    if len(points) > 1:
      cv2.polylines(image, [points], False, (0, 128, 255), line_width or 3, cv2.LINE_AA)
  for index, line in enumerate(model.get("laneLines", [])):
    points = project(line)
    probabilities = model.get("laneLineProbs", [])
    confidence = probabilities[index] if index < len(probabilities) else 0
    if len(points) > 1 and confidence is not None and confidence >= .05:
      layer = image.copy()
      cv2.polylines(layer, [points], False, (255, 255, 255), line_width or 3, cv2.LINE_AA)
      cv2.addWeighted(layer, float(np.clip(confidence, .15, 1)), image, 1-float(np.clip(confidence, .15, 1)), 0, dst=image)
  if before is not None:
    cv2.addWeighted(image, opacity, before, 1-opacity, 0, dst=image)
  return True






