async function sendReplayKey(key){
 try{
  const r=await fetch('/replay-key',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key})});
  document.querySelector('#status').textContent=r.ok?'':'Replay control unavailable';
  await update();
 }catch{document.querySelector('#status').textContent='Replay control unavailable';}
}
document.addEventListener('keydown',e=>{
 if(e.repeat||e.ctrlKey||e.metaKey||e.altKey||e.target.closest('input,select,textarea,button,[contenteditable="true"]'))return;
 let key=e.key;
 if(key==='ArrowLeft')key=e.shiftKey?'M':'S';
 if(key==='ArrowRight')key=e.shiftKey?'m':'s';
 if(![' ','s','S','m','M','e','d','t','i','w','c','+','-','q'].includes(key))return;
 e.preventDefault();sendReplayKey(key);
});
