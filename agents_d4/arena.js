const $ = (selector, root = document) => root.querySelector(selector);
const fields = ['gender', 'positions', 'species', 'resource', 'range_type', 'regions', 'release_year'];
const systems = {
  direct: 'D1 · Prompt directo',
  d2_lora: 'D2 · Modelo ajustado',
  d3: 'D3 · Tres agentes',
  d4: 'D4 · Selector ajustado',
  control: 'Control · Reglas'
};
const roles = {memory: 'Memoria', selector: 'Selector', verifier: 'Verificador', controller: 'Controlador', game: 'Juego'};
const target = $('#target');
const suggestions = $('.suggestions');
const options = $('#champions');
const lanes = [];
let config;
let portraits = {};
let selectedTarget = '';
let matches = [];
let activeMatch = -1;
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
const seconds = value => typeof value === 'number' && Number.isFinite(value)
  ? (value > 0 && value < .1 ? '<0,1 s' : value.toLocaleString('es', {maximumFractionDigits: 1}) + ' s')
  : '—';

async function json(url) {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) throw Error(data.error || 'No se pudo conectar con la demo.');
  return data;
}

function portrait(element, name) {
  const initials = document.createElement('span');
  initials.setAttribute('aria-hidden', 'true');
  initials.textContent = name?.slice(0, 2).toUpperCase() || '—';
  element.replaceChildren(initials);
  if (!portraits[name]) return;
  const img = new Image();
  img.alt = '';
  img.src = portraits[name];
  img.onerror = () => img.remove();
  element.append(img);
}

function status(lane, message, tone = '') {
  lane.status.textContent = message;
  lane.status.dataset.tone = tone;
}

function configure(lane) {
  const key = lane.select.value;
  const available = config.systems[key].mode === 'live';
  lane.button.textContent = available ? 'Jugar' : 'Reproducir';
  const hasTrace = Boolean(config.replays[key] && config.split.test.includes(selectedTarget));
  lane.traceButton.hidden = !available || !hasTrace;
  status(lane, available ? 'Listo para jugar en vivo' : hasTrace
    ? 'En vivo no disponible · Traza guardada'
    : 'En vivo no disponible · Sin traza para este campeón');
  lane.status.title = config.systems[key].why || '';
}

function updateControls() {
  target.disabled = lanes.some(lane => lane.running);
  if (target.disabled) closeSuggestions();
  for (const lane of lanes) {
    const key = lane.select.value;
    lane.button.disabled = lane.running || !selectedTarget || (
      config.systems[key].mode !== 'live' && !config.split.test.includes(selectedTarget)
    );
    lane.traceButton.disabled = lane.running;
    lane.select.disabled = lane.running;
  }
}

function reset(lane) {
  lane.rows.replaceChildren();
  lane.events.replaceChildren();
  lane.empty.hidden = false;
  lane.current.textContent = '';
  lane.attempts.textContent = '0';
  lane.total.textContent = '—';
  lane.count = 0;
  lane.conflicts = [];
  lane.turnStart = null;
  lane.started = null;
  lane.latency = null;
  lane.lastGuess = 0;
  lane.played = false;
}

function compare() {
  for (const lane of lanes) {
    const {meter, metricValue, examples} = lane;
    meter.max = Math.max(1, lane.count);
    meter.value = lane.conflicts.length;
    metricValue.textContent = lane.played ? lane.conflicts.length + ' / ' + lane.count : '—';
    meter.hidden = lane.count === 0;
    examples.replaceChildren();
    for (const conflict of lane.conflicts) {
      const item = document.createElement('li');
      item.textContent = conflict;
      examples.append(item);
    }
  }
}

function addGuess(lane, event, elapsed, replay) {
  const row = lane.rows.insertRow();
  const guess = row.insertCell();
  const name = event.guess || 'Intento inválido';
  const identity = document.createElement('span');
  identity.className = 'guess';
  const icon = document.createElement('span');
  icon.className = 'portrait';
  portrait(icon, event.guess);
  identity.append(icon, document.createTextNode(name));
  guess.append(identity);
  const champion = config.roster[event.guess];
  for (const field of fields) {
    const cell = row.insertCell();
    const match = event.feedback?.[field];
    const value = champion?.[field];
    cell.dataset.match = match || '';
    cell.textContent = (match === 'higher' ? '↑ ' : match === 'lower' ? '↓ ' : '')
      + (Array.isArray(value) ? value.join(', ') : value ?? '—');
    cell.title = ({green: 'Coincide', yellow: 'Coincidencia parcial', red: 'Distinto', higher: 'El objetivo es posterior', lower: 'El objetivo es anterior'})[match] || '';
  }
  const timing = row.insertCell();
  const turnStart = lane.turnStart ?? lane.lastGuess;
  const duration = elapsed == null ? event.latency_s ?? lane.latency : Math.max(0, elapsed - turnStart);
  timing.textContent = seconds(duration);
  timing.title = elapsed == null ? 'Latencia registrada del modelo' : 'Tiempo hasta proponer el campeón';
  if (elapsed != null) lane.lastGuess = elapsed;
  if (!replay && lane.select.value === 'control') timing.textContent = '—';
  lane.turnStart = null;
  lane.latency = null;
  lane.count++;
  lane.attempts.textContent = lane.count;
  lane.empty.hidden = true;
  if (event.strict_violation) {
    lane.conflicts.push(name + ' · ' + (event.strict_errors || []).map(error =>
      typeof error === 'string' ? error : JSON.stringify(error)).join(' · '));
  }
  compare();
}

function log(lane, message, detail) {
  const item = document.createElement('li');
  item.textContent = message;
  if (detail) {
    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = 'Ver mensaje';
    const content = document.createElement('div');
    content.textContent = typeof detail === 'string' ? detail : JSON.stringify(detail, null, 2);
    details.append(summary, content);
    item.append(details);
  }
  lane.events.append(item);
  lane.events.scrollTop = lane.events.scrollHeight;
}

function receive(lane, event, replay = false) {
  const role = roles[event.agent] || 'Modelo';
  const elapsed = event.t ?? (!replay && lane.started != null ? (performance.now() - lane.started) / 1000 : null);
  switch (event.kind) {
    case 'queued':
      status(lane, 'Esperando el servidor de modelos…');
      break;
    case 'start':
      lane.started = performance.now();
      status(lane, 'Jugando en vivo');
      break;
    case 'turn_start':
      lane.turnStart = elapsed;
      break;
    case 'model_call':
      lane.current.textContent = role + ' pensando…';
      log(lane, role + ' recibió una entrada', event.messages?.at(-1)?.content);
      break;
    case 'model_output':
      lane.latency = event.latency_s;
      log(lane, role + ' respondió · ' + seconds(event.latency_s), event.content);
      break;
    case 'decision': {
      const decision = event.decision || {};
      if (Array.isArray(decision.candidates)) {
        log(lane, 'Selector · ' + (decision.candidates.join(', ') || 'Sin candidatos'));
      } else if (decision.action) {
        log(lane, role + ' · ' + decision.action, decision.reason);
      }
      break;
    }
    case 'handoff':
      if (event.candidate) log(lane, (roles[event.source] || 'Modelo') + ' propuso ' + event.candidate, event.reason);
      break;
    case 'protocol_error':
      log(lane, role + ' · Respuesta fuera de formato', event.errors);
      break;
    case 'game_feedback':
      lane.current.textContent = '';
      addGuess(lane, event.event, elapsed, replay);
      break;
    case 'finished':
      lane.total.textContent = seconds(event.record.wall_seconds);
      status(lane, (replay ? 'Traza guardada · ' : 'En vivo · ') + (event.record.solved
        ? 'Campeón acertado' : 'Partida terminada sin acertar'), event.record.solved ? 'success' : '');
      if (event.record.stop_reason) log(lane, 'Motivo de parada', event.record.stop_reason);
      break;
  }
}

async function play(lane, key, name) {
  const url = '/api/play?' + new URLSearchParams({system: key, target: name});
  const response = await fetch(url);
  if (!response.ok) throw Error((await response.json()).error);
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = '';
  try {
    while (true) {
      const {value, done} = await reader.read();
      if (done) throw Error('La conexión terminó antes de finalizar la partida.');
      buffer += value;
      const blocks = buffer.split('\n\n');
      buffer = blocks.pop();
      for (const block of blocks) {
        if (!block.startsWith('data: ')) continue;
        const event = JSON.parse(block.slice(6));
        if (event.kind === 'error') throw Error(event.error);
        receive(lane, event);
        if (event.kind === 'finished') return;
      }
    }
  } finally {
    await reader.cancel().catch(() => {});
  }
}

async function replay(lane, key, name) {
  const query = new URLSearchParams({file: config.replays[key], target: name});
  let data;
  try {
    data = await json('/api/trace?' + query);
  } catch (error) {
    throw Error(error.message + '. Elige un campeón del conjunto de prueba para reproducir.');
  }
  const record = data.record;
  const events = record.agent_trace?.length ? record.agent_trace
    : record.trace.map(event => ({kind: 'game_feedback', event}));
  for (const event of events) {
    receive(lane, event, true);
    if (event.kind === 'game_feedback') await wait(400);
    else if (event.kind === 'model_call' || event.kind === 'decision') await wait(75);
  }
  receive(lane, {kind: 'finished', record}, true);
}

async function run(lane, useTrace = false) {
  const key = lane.select.value;
  const name = selectedTarget;
  if (lane.running || !config.names.includes(name)) return;
  reset(lane);
  lane.running = true;
  updateControls();
  const live = !useTrace && config.systems[key].mode === 'live';
  status(lane, live ? 'Conectando…' : 'Reproduciendo traza guardada');
  lane.played = true;
  compare();
  try {
    await (live ? play(lane, key, name) : replay(lane, key, name));
  } catch (error) {
    if (!lane.count) lane.played = false;
    status(lane, error.message, 'error');
  } finally {
    lane.running = false;
    lane.current.textContent = '';
    updateControls();
    compare();
  }
}

function createLane(side, key, theme) {
  const root = $('#lane').content.firstElementChild.cloneNode(true);
  root.dataset.theme = theme;
  const select = $('.system', root);
  select.id = 'system-' + key;
  const label = $('.side', root);
  label.htmlFor = select.id;
  label.textContent = side;
  for (const [id, name] of Object.entries(systems)) select.add(new Option(name, id));
  select.value = key;
  const metric = document.createElement('div');
  metric.className = 'metric';
  metric.dataset.theme = theme;
  metric.innerHTML = '<strong><span></span><span class="metric-value"></span></strong><meter min="0" max="1" value="0"></meter><ul></ul>';
  $('strong span', metric).textContent = side;
  $('#comparison').append(metric);
  const lane = {
    select, button: $('.start', root), traceButton: $('.trace', root), status: $('.status', root), rows: $('tbody', root),
    events: $('.events', root), empty: $('.empty', root), current: $('.current', root),
    attempts: $('.attempts', root), total: $('.total', root), meter: $('meter', metric),
    metricValue: $('.metric-value', metric), examples: $('ul', metric), running: false
  };
  lane.meter.setAttribute('aria-label', 'Intentos que contradicen pistas · ' + side);
  $('#arena').append(root);
  reset(lane);
  configure(lane);
  select.onchange = () => { reset(lane); configure(lane); updateControls(); compare(); };
  lane.button.onclick = () => run(lane);
  lane.traceButton.onclick = () => run(lane, true);
  return lane;
}

function selectChampion(name) {
  const changed = name !== selectedTarget;
  selectedTarget = name;
  target.value = name;
  closeSuggestions();
  if (!changed) return;
  portrait($('#targetPortrait'), name);
  for (const lane of lanes) { reset(lane); configure(lane); }
  updateControls();
  compare();
}

function closeSuggestions() {
  suggestions.hidden = true;
  target.setAttribute('aria-expanded', 'false');
  target.removeAttribute('aria-activedescendant');
}

function setActiveMatch(index) {
  activeMatch = index;
  for (const [i, option] of [...options.children].entries()) {
    option.setAttribute('aria-selected', String(i === index));
  }
  if (index < 0) {
    target.removeAttribute('aria-activedescendant');
    return;
  }
  const option = options.children[index];
  target.setAttribute('aria-activedescendant', option.id);
  option.scrollIntoView({block: 'nearest'});
}

const searchKey = text => text.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();

function showSuggestions(query) {
  const term = searchKey(query);
  const filtered = config.names.filter(name => searchKey(name).includes(term));
  matches = filtered.sort((a, b) => Number(searchKey(b).startsWith(term))
    - Number(searchKey(a).startsWith(term)) || a.localeCompare(b, 'es'));
  options.replaceChildren();
  for (const [index, name] of matches.entries()) {
    const item = document.createElement('li');
    item.id = 'champion-option-' + index;
    item.setAttribute('role', 'option');
    item.setAttribute('aria-selected', 'false');
    const icon = document.createElement('span');
    icon.className = 'portrait';
    portrait(icon, name);
    const image = $('img', icon);
    if (image) image.loading = 'lazy';
    item.append(icon, document.createTextNode(name));
    item.addEventListener('pointerdown', event => event.preventDefault());
    item.onclick = () => selectChampion(name);
    options.append(item);
  }
  $('.no-results').hidden = matches.length > 0;
  suggestions.hidden = false;
  target.setAttribute('aria-expanded', 'true');
  suggestions.scrollTop = 0;
  setActiveMatch(-1);
}

async function initialize() {
  [config, portraits] = await Promise.all([json('/api/config'), json('/portraits.json').catch(() => ({}))]);
  lanes.push(createLane('Modelo A', 'd3', 'rose'), createLane('Modelo B', 'd4', 'cyan'));
  selectChampion(config.split.test.find(name => name === 'Samira') || config.split.test[0] || config.names[0]);
  target.onfocus = () => { target.select(); showSuggestions(''); };
  target.oninput = () => showSuggestions(target.value);
  $('.target-search').addEventListener('focusout', () => {
    setTimeout(() => {
      if ($('.target-search').contains(document.activeElement)) return;
      target.value = selectedTarget;
      closeSuggestions();
    }, 0);
  });
  target.onkeydown = event => {
    if (event.key === 'Escape') {
      target.value = selectedTarget;
      closeSuggestions();
    } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      if (suggestions.hidden) showSuggestions(target.value);
      if (matches.length) setActiveMatch(event.key === 'ArrowDown'
        ? Math.min(activeMatch + 1, matches.length - 1)
        : activeMatch < 0 ? matches.length - 1 : Math.max(activeMatch - 1, 0));
    } else if (event.key === 'Enter' && !suggestions.hidden && matches.length) {
      event.preventDefault();
      selectChampion(matches[Math.max(0, activeMatch)]);
    }
  };
}

initialize().catch(error => {
  const element = $('#setup-error');
  element.hidden = false;
  element.textContent = 'No se pudo cargar la demo. ' + error.message;
});
