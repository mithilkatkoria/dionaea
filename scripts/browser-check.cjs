"use strict";
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {spawn}=require('node:child_process');
const {chromium}=require('playwright');
const base=(process.env.BASE_URL||'http://127.0.0.1:8765').replace(/\/$/,'');
const shotDir=process.env.SCREENSHOT_DIR||'test-results/screenshots';
const results={base,checks:[],widths:[],accessibility:[],consoleErrors:[],failedResponses:[]};
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let server,browser;
function pass(name,details){results.checks.push({name,passed:true,...details});console.log('PASS '+name);}
async function ready(page){await page.waitForFunction(()=>document.querySelector('#request-message').textContent.startsWith('Ready.')&&!document.querySelector('#replay').disabled);}
async function start(){
 try{const health=await fetch(base+'/api/health',{signal:AbortSignal.timeout(2000)});if((await health.json()).data_kind==='synthetic')return;}catch{}
 if(process.env.BASE_URL)throw new Error('Target health endpoint unavailable');
 server=spawn(process.env.PYTHON||'python',['app.py'],{cwd:path.resolve(__dirname,'..'),stdio:'ignore'});
 for(let i=0;i<40;i++){await pause(200);try{if((await(await fetch(base+'/api/health')).json()).ok)return;}catch{}}
 throw new Error('Local server did not start');
}
(async()=>{
 await start();fs.mkdirSync(shotDir,{recursive:true});
 browser=await chromium.launch({headless:true,...(process.env.BROWSER_CHANNEL?{channel:process.env.BROWSER_CHANNEL}:{})});
 const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
 let expectedFailure=false;
 page.on('pageerror',e=>results.consoleErrors.push(e.message));
 page.on('console',m=>{if(m.type()==='error'&&!expectedFailure)results.consoleErrors.push(m.text());});
 page.on('response',r=>{if(r.status()>=400&&!expectedFailure)results.failedResponses.push({url:r.url(),status:r.status()});});
 await page.goto(base,{waitUntil:'networkidle'});await ready(page);
 await page.waitForFunction(()=>!document.querySelector('#regime').disabled);
 assert.equal(await page.locator('#results-table tbody tr').count(),4);pass('successful initial simulation and saved benchmark');
 const saved=await(await page.request.get(base+'/api/benchmark')).json();
 for(const width of [375,390,768,1024,1440]){
  await page.setViewportSize({width,height:1000});
  const layout=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));
  results.widths.push(layout);assert.ok(layout.scrollWidth<=width,`Global overflow at ${width}`);
  await page.evaluate(fs.readFileSync(require.resolve('axe-core/axe.min.js'),'utf8'));
  const audit=await page.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}}));
  results.accessibility.push({width,violations:audit.violations.map(v=>({id:v.id,targets:v.nodes.map(n=>n.target)})),incomplete:audit.incomplete.map(v=>v.id)});
  assert.equal(audit.violations.length,0,JSON.stringify(results.accessibility.at(-1)));
 }pass('five responsive widths and zero automated WCAG A/AA violations');
 await page.setViewportSize({width:1440,height:1000});
 for(const id of ['noise','signal','burst','window','count','alpha','threshold','cooldown']){
  const before=Number(await page.locator('#'+id).inputValue());
  const pending=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/simulate'&&r.ok());
  await page.locator('#'+id).focus();await page.locator('#'+id).press('ArrowRight');
  const json=await(await pending).json();await ready(page);
  assert.ok(Number(await page.locator('#'+id).inputValue())>before);
  const expected=Number(await page.locator('#'+id).inputValue())/(['noise','signal','burst','alpha','threshold'].includes(id)?100:1);
  assert.ok(Math.abs((json.config[id]??json.detectors.single.settings[id])-expected)<1e-8);
 }pass('all eight sliders recalculate through the Python API');
 await page.locator('#seed').fill('777');await page.waitForFunction(()=>document.querySelector('#request-message').textContent.includes('Seed 777,'));
 await page.locator('#random').click();await page.waitForFunction(()=>document.querySelector('#request-message').textContent.startsWith('Ready.')&&!document.querySelector('#request-message').textContent.includes('Seed 777,'));
 assert.notEqual(await page.locator('#seed').inputValue(),'777');pass('manual seed and new seed');
 await page.locator('#seed').fill('1000000');await page.waitForFunction(()=>document.querySelector('#data-state').textContent==='CHECK INPUT');assert.equal(await page.locator('#replay').isDisabled(),true);
 await page.locator('#seed').fill('');await page.waitForFunction(()=>document.querySelector('#data-state').textContent==='CHECK INPUT');pass('invalid and empty seed states');
 await page.locator('#reset-btn').click();await ready(page);assert.equal(await page.locator('#seed').inputValue(),'42');
 await page.locator('#replay').click();await pause(500);const revealed=Number(await page.locator('#chart').getAttribute('data-cursor'));assert.ok(revealed>0&&revealed<150);
 await page.locator('#replay').click();const stopped=await page.locator('#chart').getAttribute('data-cursor');await pause(180);assert.equal(await page.locator('#chart').getAttribute('data-cursor'),stopped);
 await page.locator('#inspect-step').focus();await page.locator('#inspect-step').press('End');assert.equal(Number(await page.locator('#inspect-step').inputValue()),Number(stopped)-1);
 assert.ok((await page.locator('#inspect-detail').textContent()).includes('Step '+(Number(stopped)-1)));
 const hit=await page.locator('#plot-hit').boundingBox();await page.mouse.move(hit.x+hit.width-2,hit.y+10);assert.equal(Number(await page.locator('#inspect-step').inputValue()),Number(stopped)-1);
 pass('replay timing, pause, keyboard inspector and future-step restriction',{revealedAfter500ms:revealed});
 const replayStart=Date.now();await page.locator('#replay').click();await page.waitForFunction(()=>document.querySelector('#replay').getAttribute('aria-pressed')==='false',{},{timeout:12000});assert.equal(await page.locator('#chart').getAttribute('data-cursor'),'360');pass('replay completes in elapsed time',{remainingReplayMs:Date.now()-replayStart});
 await page.locator('#replay').click();await page.locator('#reset-btn').click();await ready(page);assert.equal(await page.locator('#replay').getAttribute('aria-pressed'),'false');assert.equal(await page.locator('#chart').getAttribute('data-cursor'),'360');pass('reset stops replay and restores defaults');
 const pendingDownload=page.waitForEvent('download');await page.locator('#download-btn').click();const download=await pendingDownload;const stream=await download.createReadStream();let csv='';for await(const chunk of stream)csv+=chunk;
 assert.equal(download.suggestedFilename(),'dionaea-synthetic-seed-42.csv');assert.equal(csv.trim().split('\n').length,361);assert.ok(csv.startsWith('t,event,label\n'));pass('synthetic CSV download');
 const regimes=Object.keys(saved.results);await page.locator('#regime').selectOption(regimes[1]);assert.ok((await page.locator('#benchmark-table').textContent()).includes(saved.results[regimes[1]].pair.cost.toFixed(2)));pass('published environment selector');
 expectedFailure=true;
 await page.route('**/api/simulate?**',r=>r.fulfill({status:503,contentType:'application/json',body:'{"error":"Deliberate QA outage"}'}));
 await page.locator('#random').click();await page.waitForFunction(()=>document.querySelector('#data-state').textContent==='UNAVAILABLE');assert.ok(await page.locator('#retry-btn').isVisible());assert.equal(await page.locator('#download-btn').isDisabled(),true);assert.equal(await page.locator('#results-table tbody tr').count(),0);
 await page.unroute('**/api/simulate?**');await page.locator('#retry-btn').click();await ready(page);pass('HTTP failure clears stale results and retry recovers');
 await page.route('**/api/simulate?**',r=>r.abort('failed'));await page.locator('#random').click();await page.waitForFunction(()=>document.querySelector('#data-state').textContent==='UNAVAILABLE');await page.unroute('**/api/simulate?**');await page.locator('#retry-btn').click();await ready(page);pass('network failure and recovery');
 await page.route('**/api/simulate?**',async r=>{if(new URL(r.request().url()).searchParams.get('seed')==='12345'){await pause(500);try{await r.fulfill({status:503,contentType:'application/json',body:'{"error":"Stale failed request"}'});}catch{}}else await r.continue();});
 const pending=page.waitForRequest(r=>new URL(r.url()).searchParams.get('seed')==='12345');await page.locator('#seed').fill('12345');await pending;await page.locator('#seed').fill('54321');await page.waitForFunction(()=>document.querySelector('#request-message').textContent.includes('Seed 54321,'));await pause(650);assert.ok((await page.locator('#request-message').textContent()).includes('Seed 54321,'));await page.unroute('**/api/simulate?**');pass('stale requests cannot replace newer results');
 expectedFailure=false;await page.locator('#reset-btn').click();await ready(page);
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(shotDir,'desktop-home.png')});await page.locator('#laboratory').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(shotDir,'desktop.png')});
 await page.goto(base);await ready(page);await page.keyboard.press('Tab');assert.equal(await page.locator(':focus').getAttribute('href'),'#laboratory');await page.keyboard.press('Enter');await page.keyboard.press('Tab');assert.equal(await page.locator(':focus').getAttribute('id'),'seed');assert.notEqual(await page.locator(':focus').evaluate(el=>getComputedStyle(el).outlineStyle),'none');pass('skip link, keyboard order and visible focus');
 const links=await page.locator('.source-grid a').evaluateAll(links=>links.map(a=>({href:a.href,rel:a.rel,target:a.target})));assert.equal(links.length,6);assert.ok(links.filter(l=>l.target==='_blank').every(l=>l.rel.includes('noopener')));pass('scientific and reproducibility links present and safe');
 const mobile=await browser.newContext({viewport:{width:390,height:1000},isMobile:true,hasTouch:true,deviceScaleFactor:1,reducedMotion:'reduce'});const touch=await mobile.newPage();await touch.goto(base);await ready(touch);await touch.screenshot({path:path.join(shotDir,'mobile.png')});await touch.locator('#replay').tap();await pause(160);await touch.locator('#replay').tap();assert.ok(Number(await touch.locator('#chart').getAttribute('data-cursor'))>0);await touch.locator('#reset-btn').tap();await ready(touch);const slider=await touch.locator('#inspect-step').boundingBox();await touch.locator('#inspect-step').tap({position:{x:slider.width*.6,y:slider.height/2}});assert.ok(Number(await touch.locator('#inspect-step').inputValue())>0);await touch.locator('.analysis-toolbar').scrollIntoViewIfNeeded();await touch.screenshot({path:path.join(shotDir,'mobile-lab.png')});pass('touch replay, reset and step inspection');
 assert.deepEqual(results.consoleErrors,[]);assert.deepEqual(results.failedResponses,[]);pass('no unexpected console errors or failing HTTP responses');results.passed=true;
})().catch(error=>{results.passed=false;results.error=error.stack;console.error(error);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();if(server)server.kill();fs.mkdirSync('test-results',{recursive:true});fs.writeFileSync(process.env.QA_OUTPUT||'test-results/browser.json',JSON.stringify(results,null,2)+'\n');console.log('Browser QA '+(results.passed?'PASSED':'FAILED'));});
