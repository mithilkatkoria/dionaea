"use strict";
const defaults = {seed:42, noise:9, signal:67, burst:0.6, window:6, count:3, alpha:80, threshold:160, cooldown:6};
const ids = Object.keys(defaults);
const $ = (id) => document.getElementById(id);
const colors = {single:'#9c9d80', pair:'#5b9572', count:'#bc784c', leaky:'#2b6951'};
const labels = {single:'Single event', pair:'Timed pair', count:'Sliding count', leaky:'Leaky evidence'};
let data = null, timer = null, cursor = 360, requestCounter = 0, debounce = null;
const int = (id) => Number($(id).value);
function params(){
  return {seed:Math.max(0,Math.floor(int('seed')||0)), noise:int('noise')/100, signal:int('signal')/100,
    burst:int('burst')/100, window:int('window'), count:int('count'),
    alpha:int('alpha')/100, threshold:int('threshold')/100, cooldown:int('cooldown')};
}
function updateOutputs(){
  const p = params();
  $('seed-value').textContent = String(p.seed);
  $('noise-value').textContent = `${Math.round(p.noise*100)}%`;
  $('signal-value').textContent = `${Math.round(p.signal*100)}%`;
  $('burst-value').textContent = `${(p.burst*100).toFixed(1)}%`;
  $('window-value').textContent = `${p.window} steps`;
  $('count-value').textContent = p.count;
  $('alpha-value').textContent = p.alpha.toFixed(2);
  $('threshold-value').textContent = p.threshold.toFixed(2);
  $('cooldown-value').textContent = `${p.cooldown} steps`;
  $('experiment-id').textContent = `SEED / ${String(p.seed).padStart(4,'0')}`;
}
function cleanStop(){if(timer!==null){clearInterval(timer);timer=null;} $('play-icon').textContent='▶';}
async function refresh(){
  cleanStop(); cursor=360; updateOutputs();
  const current = ++requestCounter;
  const q = new URLSearchParams(params());
  try{
    const response = await fetch(`/api/simulate?${q.toString()}`);
    const result = await response.json();
    if(!response.ok) throw new Error(result.error||'Simulation failed');
    if(current!==requestCounter) return;
    data=result;cursor=data.events.length;draw();drawTable();
  }catch(e){ if(current===requestCounter){$('chart').textContent='Unable to load simulation: '+e.message; $('results-table').textContent='';} }
}
function rect(x,y,w,h,color,extra=''){return `<rect x="${x.toFixed(2)}" y="${y}" width="${Math.max(w,.1).toFixed(2)}" height="${h}" fill="${color}" ${extra}/>`;}
function draw(){
 if(!data)return;
 const W=1000, left=110,right=34, available=W-left-right, n=data.events.length;
 const x=(t)=>left+t*available/n;
 const tracks=[{name:'INPUT',top:42,key:null},{name:'Single event',top:116,key:'single'},
   {name:'Timed pair',top:161,key:'pair'},{name:'Sliding count',top:206,key:'count'},
   {name:'Leaky evidence',top:251,key:'leaky'}];
 let svg=`<svg viewBox="0 0 1000 329" xmlns="http://www.w3.org/2000/svg" aria-label="Time series with true episodes and four alarm tracks">`;
 svg+=`<text x="18" y="22" fill="#778b7d" font-size="10" font-family="monospace" letter-spacing="1">TIME / t</text>`;
 for(let t=0;t<=n;t+=Math.max(1, Math.floor(n/6))){const q=x(t);svg+=`<line x1="${q}" y1="28" x2="${q}" y2="289" stroke="#e0e6db" stroke-width="1"/><text x="${q}" y="310" text-anchor="middle" font-family="monospace" fill="#7f9587" font-size="11">${t}</text>`;}
 for(let i=0;i<tracks.length;i++){
   const track=tracks[i];svg+=`<text x="15" y="${track.top+12}" fill="#466956" font-family="Arial,sans-serif" font-size="12" font-weight="600">${track.name}</text>`;
   svg+=`<line x1="${left}" y1="${track.top+23}" x2="${x(n)}" y2="${track.top+23}" stroke="#d7e0d3"/>`;
   for(const e of data.episodes){const a=Math.max(0,x(e.start)),b=Math.min(x(e.end),x(cursor));if(b>a){svg+=rect(a,track.top-8,b-a,32,'#dceac8','opacity="0.75"');}}
   if(track.key){for(const t of data.detectors[track.key].alarms){if(t>=cursor)continue; const c=x(t);svg+=`<polygon points="${c},${track.top-4} ${c+5},${track.top+4} ${c},${track.top+12} ${c-5},${track.top+4}" fill="${colors[track.key]}" stroke="#fafaf6" stroke-width=".8"/>`;}}
 }
 for(let t=0;t<Math.min(cursor,n);t++)if(data.events[t])svg+=rect(x(t)+.7,43,Math.max(1.5,available/n-1.5),25,'#496f59','rx=".7"');
 svg+=`<line x1="${x(Math.min(cursor,n))}" y1="26" x2="${x(Math.min(cursor,n))}" y2="289" stroke="#cf7f51" stroke-dasharray="4,4" opacity=".7"/>`;
 svg+=`<rect id="plot-hit" x="${left}" y="26" width="${available}" height="264" fill="transparent" style="cursor:crosshair"/>`;
 svg+='</svg>';
 $('chart').innerHTML=svg;
 const hit=$('plot-hit');
 hit.addEventListener('mousemove',(event)=>{
   const b=hit.ownerSVGElement.getBoundingClientRect();
   const xpos=(event.clientX-b.left)*(W/b.width);
   const t=Math.max(0,Math.min(n-1,Math.floor((xpos-left)*n/available)));
   const trueEpisode=data.truth[t]?'TRUE EPISODE':'BACKGROUND';
   const alarms=Object.keys(data.detectors).filter(k=>data.detectors[k].alarms.includes(t)).map(k=>labels[k]);
   $('chart-tip').textContent=`t=${t}  ·  observed=${data.events[t]}  ·  ${trueEpisode}  ·  alarms: ${alarms.join(', ')||'none'}`;
 });
 hit.addEventListener('mouseleave',()=>{$('chart-tip').textContent='Hover to examine a time step';});
}
function drawTable(){
  if(!data)return;
  const rows=Object.keys(labels).map(k=>{
    const m=data.detectors[k].metrics;
    const delay=m.mean_delay===null?'—':m.mean_delay.toFixed(1);
    return `<tr><td><i class="method-bullet" style="background:${colors[k]}"></i>${labels[k]}</td><td>${m.tp}/${data.episodes.length}</td><td>${m.fp}</td><td>${(m.precision*100).toFixed(0)}%</td><td>${(m.recall*100).toFixed(0)}%</td><td>${delay}</td></tr>`;
  }).join('');
  $('results-table').innerHTML=`<table><thead><tr><th>Detector</th><th>Detected</th><th>False alerts</th><th>Precision</th><th>Recall</th><th>Delay*</th></tr></thead><tbody>${rows}</tbody></table>`;
  const p=params();
  let note='Compare both missed episodes and false alarms; neither metric tells the full story.';
  if(p.burst>0.03)note='Clustered background noise may imitate true events. Watch for false alarms from detectors that rely on repeated evidence.';
  else if(p.signal<0.4)note='Sparse true events can be missed by cautious detectors. Suppressing false alarms can reduce recall.';
  else if(p.noise>0.2)note='Frequent random events create false positives. A longer memory window can sometimes make this worse.';
  else note='Try increasing noise bursts or lowering real-event strength. Does the best detector change?';
  $('interpretation').textContent=note;
}
function play(){
 if(timer!==null){cleanStop();return;}
 if(!data)return;
 if(cursor>=data.events.length)cursor=0;
 $('play-icon').textContent='Ⅱ';draw();
 timer=setInterval(()=>{cursor=Math.min(data.events.length,cursor+3);draw();if(cursor>=data.events.length)cleanStop();},30);
}
function schedule(){updateOutputs();clearTimeout(debounce);debounce=setTimeout(refresh,160);}
ids.forEach(id=>$(id).addEventListener('input',schedule));
$('seed').addEventListener('change',schedule);
$('reset-btn').addEventListener('click',()=>{ids.forEach(id=>$(id).value=defaults[id]);refresh();});
$('random').addEventListener('click',()=>{$('seed').value=Math.floor(Math.random()*100000);refresh();});
$('replay').addEventListener('click',play);
updateOutputs();refresh();
