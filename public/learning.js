"use strict";
(() => {
  const element = id => document.getElementById(id);
  const names = {single: 'Single event', pair: 'Timed pair', count: 'Sliding count', leaky: 'Leaky evidence'};
  let example = null;

  function renderExample() {
    if (!example) return;
    const t = Number(element('example-step').value);
    element('example-position').textContent = `t = ${t}`;
    element('example-prev').disabled = t === 0;
    element('example-next').disabled = t === example.events.length - 1;
    element('example-sequence').replaceChildren(...example.events.map((event, index) => {
      const slot = document.createElement('div');
      slot.className = `example-bit${index === t ? ' is-current' : ''}${index > t ? ' is-future' : ''}`;
      const time = document.createElement('span'); time.textContent = `t=${index}`;
      const bit = document.createElement('strong'); bit.textContent = String(event);
      slot.append(time, bit);
      return slot;
    }));
    element('example-cards').replaceChildren(...Object.keys(names).map(method => {
      const trace = example.detectors[method];
      const alarm = trace.alarms.includes(t);
      const state = trace.confidence[t];
      const card = document.createElement('article'); card.className = `trace-card trace-${method}`;
      const title = document.createElement('h4'); title.textContent = names[method];
      const decision = document.createElement('span'); decision.className = `decision-tag${alarm ? ' is-alarm' : ''}`; decision.textContent = alarm ? 'Alarm' : 'Waiting';
      const value = document.createElement('strong');
      value.className = 'trace-value';
      value.textContent = method === 'leaky' ? state.toFixed(2) : method === 'pair' ? (alarm ? 'Pair complete' : state ? 'One recent event' : 'No recent event') : String(state);
      const caption = document.createElement('p');
      caption.textContent = method === 'single' ? 'Current binary event' : method === 'pair' ? 'Recorded pair state' : method === 'count' ? 'Events retained in the window' : 'Recorded evidence before reset';
      card.append(title, decision, value, caption);
      return card;
    }));
    const alarms = Object.keys(names).filter(method => example.detectors[method].alarms.includes(t)).map(method => names[method]);
    let reading = `At t = ${t}, the observed event is ${example.events[t]}. ${alarms.length ? 'Alarms: ' + alarms.join(', ') + '.' : 'No method raises an alarm.'}`;
    if (t === 2) reading += ' Leaky evidence reaches 1.64, above its 1.60 threshold. Sliding count has only two events and needs three.';
    else if (t === 3) reading += ' Sliding count now has three events. Leaky evidence was reset after its previous alarm, so its score is 1.00.';
    else reading += " An alarm clears that method's evidence before the next step.";
    element('example-reading').textContent = reading;
  }

  async function loadExample() {
    example = null;
    ['example-prev', 'example-next', 'example-step'].forEach(id => element(id).disabled = true);
    element('example-retry').hidden = true;
    element('example-status').textContent = 'Loading the Python teaching trace...';
    try {
      const response = await fetch('/learning-example.json', {signal: AbortSignal.timeout(8000)});
      if (!response.ok) throw new Error('Teaching trace unavailable');
      const result = await response.json();
      if (!Array.isArray(result.events) || result.events.length !== 12 || !Object.keys(names).every(method => result.detectors?.[method]?.confidence?.length === result.events.length)) throw new Error('Incomplete teaching trace');
      example = result;
      element('example-step').max = String(example.events.length - 1);
      element('example-step').value = '0';
      element('example-step').disabled = false;
      renderExample();
      element('example-status').textContent = 'Ready. Step through the recorded Python decisions.';
    } catch {
      element('example-status').textContent = 'The teaching example could not load. The main experiment and written explanations are still available.';
      element('example-retry').hidden = false;
    }
  }

  element('example-step').addEventListener('input', renderExample);
  element('example-prev').addEventListener('click', () => {element('example-step').stepDown(); renderExample();});
  element('example-next').addEventListener('click', () => {element('example-step').stepUp(); renderExample();});
  element('example-retry').addEventListener('click', loadExample);
  loadExample();
})();
