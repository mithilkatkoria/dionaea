"use strict";
const defaults = {seed:42, noise:9, signal:67, burst:0.6, window:6, count:3, alpha:80, threshold:160, cooldown:6};
const ids = Object.keys(defaults);
const $ = (id) => document.getElementById(id);
const colors = {single:'#737650', pair:'#477c5a', count:'#9a5c34', leaky:'#2b6951'};
const labels = {single:'Single event', pair:'Timed pair', count:'Sliding count', leaky:'Leaky evidence'};
let data = null, benchmark = null, frame = null, cursor = 360, requestCounter = 0, debounce = null, controller = null;
const number = (id) => Number($(id).value);
function params(){
  return {seed:number('seed'), noise:number('noise')/100, signal:number('signal')/100,
    burst:number('burst')/100, window:number('window'), count:number('count'),
    alpha:number('alpha')/100, threshold:number('threshold')/100, cooldown:number('cooldown')};
}
function updateOutputs(){
  const p = params();
  $('seed-value').textContent = $('seed').value || 'N/A';
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
function cleanStop(){
  if(frame!==null) cancelAnimationFrame(frame);
  frame=null;
  $('replay').innerHTML='<span aria-hidden="true">▶</span> Replay';
  $('replay').setAttribute('aria-label','Replay time steps');
  $('replay').setAttribute('aria-pressed','false');
}
function invalidate(){
  ++requestCounter;
  controller?.abort();
  cleanStop();
  data=null;
  $('replay').disabled=true;
  $('download-btn').disabled=true;
  $('inspect-step').disabled=true;
  $('retry-btn').hidden=true;
  $('results-table').textContent='';
  $('chart').textContent='Calculating a new synthetic stream...';
  $('chart').setAttribute('aria-busy','true');
  $('data-state').textContent='CALCULATING';
  $('request-message').textContent='Calculating the simulation...';
  $('inspect-detail').textContent='Waiting for a new stream.';
}
async function refresh(){
  clearTimeout(debounce);
  invalidate(); updateOutputs();
  if(ids.some(id=>!$(id).checkValidity())){
    $('chart').textContent='Enter a whole-number seed between 0 and 999999.';
    $('request-message').textContent='Check the seed. It must be a whole number from 0 to 999999.';
    $('chart').setAttribute('aria-busy','false');
    $('data-state').textContent='CHECK INPUT';
    return;
  }
  const current=requestCounter;
  const active=new AbortController(); controller=active;
  const timeout=setTimeout(()=>active.abort(),10000);
  try{
    const response=await fetch(`/api/simulate?${new URLSearchParams(params())}`,{signal:active.signal});
    const result=await response.json();
    if(!response.ok) throw new Error(result.error || 'Simulation unavailable');
    if(current!==requestCounter) return;
    if(!Array.isArray(result.events) || !result.events.length || !result.detectors) throw new Error('The server returned an incomplete stream');
    data=result; cursor=data.events.length;
    $('replay').disabled=false; $('download-btn').disabled=false; $('inspect-step').disabled=false;
    $('data-state').textContent='SYNTHETIC DATA';
    $('request-message').textContent=`Ready. Seed ${data.config.seed}, ${data.events.length} steps, ${data.episodes.length} labelled episodes.`;
    draw(); drawTable(); inspect(0);
  }catch(error){
    if(current!==requestCounter) return;
    const message=error.name==='AbortError'?'The request timed out. Please retry.':error.message;
    $('chart').textContent='The simulation could not be loaded.';
    $('request-message').textContent=`Unable to load simulation: ${message}`;
    $('data-state').textContent='UNAVAILABLE';
    $('retry-btn').hidden=false;
  }finally{
    clearTimeout(timeout);
    if(current===requestCounter) $('chart').setAttribute('aria-busy','false');
  }
}
function rect(x,y,w,h,color,extra=''){return `<rect x="${x.toFixed(2)}" y="${y}" width="${Math.max(w,.1).toFixed(2)}" height="${h}" fill="${color}" ${extra}/>`;}
function inspect(step){
  if(!data) return;
  const max=Math.max(0,Math.min(cursor,data.events.length)-1);
  const t=Math.max(0,Math.min(max,Math.floor(step)));
  $('inspect-step').max=String(max); $('inspect-step').value=String(t); if($('inspect-value').textContent!==String(t)) $('inspect-value').textContent=String(t);
  if(cursor===0){const message='Replay is at the beginning. No steps have been revealed.';$('inspect-detail').textContent=message;$('chart-tip').textContent=message;return;}
  const alarms=Object.keys(labels).filter(k=>data.detectors[k].alarms.includes(t)).map(k=>labels[k]);
  const text=`Step ${t}: observed event ${data.events[t]}; ${data.truth[t]?'true episode':'background'}; alarms: ${alarms.join(', ')||'none'}.`;
  if($('inspect-detail').textContent!==text) $('inspect-detail').textContent=text;
  if($('chart-tip').textContent!==text) $('chart-tip').textContent=text;
}
function draw(){
  if(!data)return;
  const W=1000, left=110, available=856, n=data.events.length;
  const x=t=>left+t*available/n;
  const tracks=[{name:'INPUT',top:42,key:null},{name:'Single event',top:116,key:'single'},
    {name:'Timed pair',top:161,key:'pair'},{name:'Sliding count',top:206,key:'count'},
    {name:'Leaky evidence',top:251,key:'leaky'}];
  let svg='<svg viewBox="0 0 1000 329" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">';
  svg+='<text x="18" y="22" fill="#526b5b" font-size="10" font-family="monospace" letter-spacing="1">TIME / t</text>';
  for(let t=0;t<=n;t+=Math.max(1,Math.floor(n/6))){const q=x(t);svg+=`<line x1="${q}" y1="28" x2="${q}" y2="289" stroke="#d6dfcf"/><text x="${q}" y="310" text-anchor="middle" font-family="monospace" fill="#526b5b" font-size="11">${t}</text>`;}
  for(const track of tracks){
    svg+=`<text x="15" y="${track.top+12}" fill="#466956" font-family="Arial,sans-serif" font-size="12" font-weight="600">${track.name}</text><line x1="${left}" y1="${track.top+23}" x2="${x(n)}" y2="${track.top+23}" stroke="#d7e0d3"/>`;
    for(const e of data.episodes){const a=x(e.start),b=Math.min(x(e.end),x(cursor));if(b>a)svg+=rect(a,track.top-8,b-a,32,'#dceac8','opacity="0.75"');}
    if(track.key) for(const t of data.detectors[track.key].alarms){if(t>=cursor)continue;const c=x(t);svg+=`<polygon points="${c},${track.top-4} ${c+5},${track.top+4} ${c},${track.top+12} ${c-5},${track.top+4}" fill="${colors[track.key]}" stroke="#fafaf6" stroke-width=".8"/>`;}
  }
  for(let t=0;t<Math.min(cursor,n);t++)if(data.events[t])svg+=rect(x(t)+.7,43,Math.max(1.5,available/n-1.5),25,'#496f59','rx=".7"');
  svg+=`<line x1="${x(cursor)}" y1="26" x2="${x(cursor)}" y2="289" stroke="#aa5d32" stroke-dasharray="4,4"/><rect id="plot-hit" x="${left}" y="26" width="${available}" height="264" fill="transparent"/></svg>`;
  $('chart').innerHTML=svg;
  $('chart').dataset.cursor=String(cursor);
  $('inspect-step').max=String(Math.max(0,cursor-1));
  inspect(Number($('inspect-step').value));
  $('plot-hit').addEventListener('pointermove',event=>{
    const b=event.currentTarget.ownerSVGElement.getBoundingClientRect();
    inspect(((event.clientX-b.left)*W/b.width-left)*n/available);
  });
  $('plot-hit').addEventListener('pointerdown',event=>{
    const b=event.currentTarget.ownerSVGElement.getBoundingClientRect();
    inspect(((event.clientX-b.left)*W/b.width-left)*n/available);
  });
}
function drawTable(){
  if(!data)return;
  const rows=Object.keys(labels).map(k=>{
    const m=data.detectors[k].metrics;
    return `<tr><th scope="row"><i class="method-bullet method-${k}" aria-hidden="true"></i>${labels[k]}</th><td>${m.tp}/${data.episodes.length}</td><td>${m.fp}</td><td>${(m.precision*100).toFixed(0)}%</td><td>${(m.recall*100).toFixed(0)}%</td><td>${m.mean_delay===null?'N/A':m.mean_delay.toFixed(1)}</td></tr>`;
  }).join('');
  $('results-table').innerHTML=`<table><caption class="sr-only">Full-run detector performance on this synthetic stream. Delay in simulation steps, detected episodes only.</caption><thead><tr><th scope="col">Detector</th><th scope="col">Detected</th><th scope="col">False alerts</th><th scope="col">Precision</th><th scope="col">Recall</th><th scope="col">Delay*</th></tr></thead><tbody>${rows}</tbody></table>`;
  const p=params();
  $('interpretation').textContent=p.burst>=0.02?'Clustered background noise may imitate true events. Watch for false alarms from detectors that rely on repeated evidence.':p.signal<0.4?'Sparse true events can be missed by cautious detectors. Suppressing false alarms can reduce recall.':p.noise>0.2?'Frequent random events create false positives. A longer memory window can sometimes make this worse.':'Try increasing noise bursts or lowering real-event strength. Does the best detector change?';
}
function play(){
  if(frame!==null){cleanStop();return;}
  if(!data)return;
  if(cursor>=data.events.length)cursor=0;
  $('replay').innerHTML='<span aria-hidden="true">Ⅱ</span> Pause';
  $('replay').setAttribute('aria-label','Pause replay'); $('replay').setAttribute('aria-pressed','true');
  inspect(0); draw();
  let previous=performance.now();
  const tick=now=>{
    if(!data)return;
    if(now-previous>=40){
      const steps=Math.floor((now-previous)/40)*2;
      previous+=Math.floor((now-previous)/40)*40;
      cursor=Math.min(data.events.length,cursor+steps);draw();
      if(cursor>=data.events.length){cleanStop();return;}
    }
    frame=requestAnimationFrame(tick);
  };
  frame=requestAnimationFrame(tick);
}
function schedule(){clearPreset();updateOutputs();invalidate();clearTimeout(debounce);debounce=setTimeout(refresh,160);}
function drawBenchmark(){
  if(!benchmark)return;
  const regime=$('regime').value;
  const results=benchmark.results[regime];
  const lowest=Object.keys(labels).reduce((best,method)=>results[method].cost<results[best].cost?method:best,'single');
  const rows=Object.keys(labels).map(k=>{
    const m=results[k];
    return `<tr${k===lowest?' class="lowest-cost"':''}><th scope="row">${labels[k]}${k===lowest?'<span class="lowest-label">Lowest mean cost</span>':''}</th><td>${(m.recall*100).toFixed(1)}%</td><td>${(m.precision*100).toFixed(1)}%</td><td>${m.fp.toFixed(2)}</td><td>${m.mean_delay_detected_only===null?'N/A':m.mean_delay_detected_only.toFixed(2)}</td><td>${m.cost.toFixed(2)} ± ${m.cost_sd.toFixed(2)}</td></tr>`;
  }).join('');
  $('benchmark-table').innerHTML=`<table><caption class="sr-only">Held-out synthetic results for ${regime}. Mean cost and sample standard deviation over 40 seeds. Delay uses detected episodes only.</caption><thead><tr><th scope="col">Detector</th><th scope="col">Recall</th><th scope="col">Precision</th><th scope="col">False alerts</th><th scope="col">Delay (steps)</th><th scope="col">Cost ± SD</th></tr></thead><tbody>${rows}</tbody></table>`;
  const single=results.single, leaky=results.leaky;
  const notes=[
    ['False alerts per stream', `${single.fp.toFixed(2)} with single-event detection; ${leaky.fp.toFixed(2)} with leaky evidence.`],
    ['The price of caution', `Recall changes from ${(single.recall*100).toFixed(1)}% to ${(leaky.recall*100).toFixed(1)}%. Report both false alarms and misses.`],
    ['Read the ranking carefully', `${labels[lowest]} has the lowest mean cost in this environment under the chosen penalty weights. This is a descriptive result, not proof of superiority.`]
  ];
  $('benchmark-reading').replaceChildren(...notes.map(([title,text])=>{
    const article=document.createElement('article'), heading=document.createElement('h3'), paragraph=document.createElement('p');
    heading.textContent=title; paragraph.textContent=text; article.append(heading,paragraph); return article;
  }));
}
async function loadBenchmark(){
  try{
    const response=await fetch('/api/benchmark',{signal:AbortSignal.timeout(10000)});
    if(!response.ok)throw new Error('Saved results unavailable');
    benchmark=await response.json();
    $('regime').replaceChildren(...Object.keys(benchmark.results).map(name=>new Option(name,name)));
    $('regime').disabled=false; drawBenchmark();
    $('benchmark-state').textContent='Published benchmark loaded. Settings remain fixed across all four environments.';
  }catch{
    $('benchmark-state').textContent='The published benchmark could not be loaded. Use the repository results link below or reload this page.';
    $('regime').replaceChildren(new Option('Results unavailable',''));
  }
}
const presetValues={balanced:{noise:9,signal:67,burst:0},sparse:{noise:9,signal:30,burst:0},bursts:{noise:6,signal:67,burst:2.7}};
const presetNotes={balanced:'Independent background noise. Compare false alerts with missed episodes.',sparse:'Genuine episodes contain fewer events. Predict which cautious methods may miss them.',bursts:'Background events arrive in clusters. Repeated noise can imitate genuine evidence.'};
function clearPreset(){
  document.querySelectorAll('[data-preset]').forEach(button=>button.setAttribute('aria-pressed','false'));
  $('preset-status').textContent='Custom exploration. The frozen published benchmark is not changed by these controls.';
}
document.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{
  const preset=button.dataset.preset;
  ids.forEach(id=>$(id).value=({...defaults,...presetValues[preset]})[id]);
  document.querySelectorAll('[data-preset]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));
  $('preset-status').textContent=presetNotes[preset]+' Detector settings use the shared exploratory defaults, not the trained benchmark settings.';
  refresh();
}));
if(window.matchMedia('(max-width:740px)').matches) $('detector-controls').open=false;
ids.forEach(id=>$(id).addEventListener('input',schedule));
$('reset-btn').addEventListener('click',()=>{clearPreset();ids.forEach(id=>$(id).value=defaults[id]);refresh();});
$('retry-btn').addEventListener('click',refresh);
$('random').addEventListener('click',()=>{const seed=crypto.getRandomValues(new Uint32Array(1))[0]%1000000;$('seed').value=seed===number('seed')?(seed+1)%1000000:seed;refresh();});
$('replay').addEventListener('click',play);
$('inspect-step').addEventListener('input',()=>inspect(number('inspect-step')));
$('regime').addEventListener('change',drawBenchmark);
$('download-btn').addEventListener('click',()=>{
  if(!data)return;
  const csv='t,event,label\n'+data.events.map((value,t)=>`${t},${value},${data.truth[t]}`).join('\n')+'\n';
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  const link=document.createElement('a');link.href=url;link.download=`dionaea-synthetic-seed-${data.config.seed}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
document.addEventListener('visibilitychange',()=>{if(document.hidden)cleanStop();});
updateOutputs(); refresh(); loadBenchmark();
