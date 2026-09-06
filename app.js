const output = document.getElementById('output');
const vehicleInput = document.getElementById('vehicleInput');
const vehicleList = document.getElementById('vehicleList');
const mode = document.getElementById('mode');
let vehicles = [];

function normalize(text) {
  return String(text || '').trim().toLowerCase().replace(/\s+/g, ' ');
}

function findVehicle(name) {
  const target = normalize(name);
  return vehicles.find(v => normalize(v.name) === target);
}

function card(v, base = false) {
  const br = v.br ?? 'BR pendiente';
  const availability = v.availability || 'no indicado';
  return `<article class="vehicle-card ${base ? 'base' : ''}">
    <h3>${escapeHtml(v.name)}${base ? ' ← BASE' : ''}</h3>
    <p>BR: ${escapeHtml(br)}</p>
    <p>Rol: ${escapeHtml(v.role || 'N/D')}</p>
    <p>Estado: ${escapeHtml(availability)}</p>
  </article>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}

function analyze() {
  const v = findVehicle(vehicleInput.value);
  if (!v) {
    output.innerHTML = `<div class="warning"><strong>VEHÍCULO NO ENCONTRADO</strong><br>No existe una coincidencia exacta en la base de datos local.</div>`;
    return;
  }
  output.innerHTML = `<div class="result-head"><div><p class="eyebrow">VEHICLE ANALYSIS</p><h2>${escapeHtml(v.name)}</h2></div><span class="badge">${escapeHtml(v.nation || 'NACIÓN N/D')}</span></div><div class="cards">${card(v, true)}</div>`;
}

function role(v) {
  const text = normalize(`${v.role || ''} ${v.type || ''}`);
  if (/antiaéreo|antiaereo|spaa/.test(text)) return 'antiaereo';
  if (/atgm|antitanque|cazacarros/.test(text)) return 'antitanque';
  if (/explorador|recon|vehículo ligero|vehiculo ligero/.test(text)) return 'recon';
  if (/helicóptero|helicoptero/.test(text)) return 'helicoptero';
  if (/avión|avion/.test(text)) return 'aire';
  return 'principal';
}

function generateLineup() {
  const base = findVehicle(vehicleInput.value);
  if (!base) {
    output.innerHTML = `<div class="warning"><strong>CONSULTA INVÁLIDA</strong><br>Introduce un vehículo que exista en la base de datos.</div>`;
    return;
  }
  if (typeof base.br !== 'number') {
    output.innerHTML = `<div class="warning"><strong>DATOS INSUFICIENTES</strong><br>${escapeHtml(base.name)} está en la base de datos, pero su BR actual no está verificado. WTGPT no inventará un BR ni fabricará un lineup.<br><br>Modo solicitado: ${escapeHtml(mode.value)}.</div>`;
    return;
  }
  const candidates = vehicles.filter(v => normalize(v.nation) === normalize(base.nation) && v !== base && typeof v.br === 'number' && Math.abs(v.br - base.br) <= 0.7);
  const selected = [base];
  const roles = new Set();
  candidates.sort((a,b) => Math.abs(a.br-base.br)-Math.abs(b.br-base.br));
  for (const v of candidates) {
    const r = role(v);
    if (!roles.has(r) || selected.length < 2) selected.push(v), roles.add(r);
    if (selected.length >= 5) break;
  }
  output.innerHTML = `<div class="result-head"><div><p class="eyebrow">LINEUP INTELLIGENCE</p><h2>Lineup recomendado</h2><p class="hero-text">Base: ${escapeHtml(base.name)} · ${escapeHtml(mode.value)} · BR ${base.br}</p></div><span class="badge">${escapeHtml(base.nation)}</span></div><div class="cards">${selected.map((v,i)=>card(v,i===0)).join('')}</div>`;
}

async function loadDatabase() {
  try {
    const response = await fetch('vehicles.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const data = await response.json();
    vehicles = Array.isArray(data.vehicles) ? data.vehicles : [];
    document.getElementById('vehicleCount').textContent = vehicles.length;
    document.getElementById('verifiedCount').textContent = vehicles.filter(v => typeof v.br === 'number').length;
    vehicleList.innerHTML = vehicles.map(v => `<option value="${escapeHtml(v.name)}"></option>`).join('');
  } catch (error) {
    document.getElementById('vehicleCount').textContent = 'ERR';
    document.getElementById('verifiedCount').textContent = 'ERR';
    output.innerHTML = `<div class="warning"><strong>DATABASE OFFLINE</strong><br>No se pudo cargar vehicles.json.</div>`;
  }
}

document.getElementById('analyzeBtn').addEventListener('click', analyze);
document.getElementById('lineupBtn').addEventListener('click', generateLineup);
vehicleInput.addEventListener('keydown', e => { if (e.key === 'Enter') analyze(); });
loadDatabase();
