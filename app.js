const output = document.getElementById('output');
const vehicleInput = document.getElementById('vehicleInput');
const lineupInput = document.getElementById('lineupInput');
const vehicleList = document.getElementById('vehicleList');
const mode = document.getElementById('mode');
let vehicles = [];

function normalize(text) { return String(text || '').trim().toLowerCase().replace(/\s+/g, ' '); }
function findVehicle(name) { const target = normalize(name); return vehicles.find(v => normalize(v.name) === target); }

function imageMarkup(v) {
  if (!v.image_url) return '<div class="vehicle-image placeholder">SIN IMAGEN VERIFICADA</div>';
  return `<div class="vehicle-image"><img src="${escapeHtml(v.image_url)}" alt="${escapeHtml(v.name)}" loading="lazy" onerror="this.parentElement.classList.add('broken');this.remove()"></div>`;
}

function card(v, base = false) {
  const br = v.br ?? 'BR pendiente';
  const availability = v.availability || 'no indicado';
  return `<article class="vehicle-card ${base ? 'base' : ''}">${imageMarkup(v)}<div class="vehicle-info"><h3>${escapeHtml(v.name)}${base ? ' ← BASE' : ''}</h3><p>BR: ${escapeHtml(br)}</p><p>Rol: ${escapeHtml(v.role || 'N/D')}</p><p>Estado: ${escapeHtml(availability)}</p></div></article>`;
}
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c])); }

function analyze() {
  const v = findVehicle(vehicleInput.value);
  if (!v) { output.innerHTML = `<div class="warning"><strong>VEHÍCULO NO ENCONTRADO</strong><br>No existe una coincidencia exacta en la base de datos local.</div>`; return; }
  output.innerHTML = `<div class="result-head"><div><p class="eyebrow">VEHICLE ANALYSIS</p><h2>${escapeHtml(v.name)}</h2></div><span class="badge">${escapeHtml(v.nation || 'NACIÓN N/D')}</span></div><div class="cards">${card(v, true)}</div>`;
}
function role(v) {
  const text = normalize(`${v.role || ''} ${v.type || ''}`);
  if (/antiaéreo|antiaereo|spaa/.test(text)) return 'antiaereo';
  if (/atgm|antitanque|cazacarros/.test(text)) return 'antitanque';
  if (/explorador|recon|vehículo ligero|vehiculo ligero/.test(text)) return 'recon';
  if (/helicóptero|helicoptero/.test(text)) return 'helicoptero';
  if (/avión|avion|fighter|bomber|strike/.test(text)) return 'aire';
  return 'principal';
}
function generateLineup() {
  const base = findVehicle(vehicleInput.value);
  if (!base) { output.innerHTML = `<div class="warning"><strong>CONSULTA INVÁLIDA</strong><br>Introduce un vehículo que exista en la base de datos.</div>`; return; }
  if (typeof base.br !== 'number') { output.innerHTML = `<div class="warning"><strong>DATOS INSUFICIENTES</strong><br>${escapeHtml(base.name)} está en la base de datos, pero su BR actual no está verificado. WTGPT no inventará un BR ni fabricará un lineup.<br><br>Modo solicitado: ${escapeHtml(mode.value)}.</div>`; return; }
  const candidates = vehicles.filter(v => normalize(v.nation) === normalize(base.nation) && v !== base && typeof v.br === 'number' && Math.abs(v.br - base.br) <= 0.7);
  const selected = [base], roles = new Set();
  candidates.sort((a,b) => Math.abs(a.br-base.br)-Math.abs(b.br-base.br));
  for (const v of candidates) { const r = role(v); if (!roles.has(r) || selected.length < 2) selected.push(v), roles.add(r); if (selected.length >= 5) break; }
  output.innerHTML = `<div class="result-head"><div><p class="eyebrow">LINEUP INTELLIGENCE</p><h2>Lineup recomendado</h2><p class="hero-text">Base: ${escapeHtml(base.name)} · ${escapeHtml(mode.value)} · BR ${base.br}</p></div><span class="badge">${escapeHtml(base.nation)}</span></div><div class="cards">${selected.map((v,i)=>card(v,i===0)).join('')}</div>`;
}
function searchExactLineup() {
  const raw = lineupInput.value.trim();
  if (!raw) { output.innerHTML = `<div class="warning"><strong>LINEUP VACÍO</strong><br>Introduce los vehículos separados por comas.</div>`; return; }
  const names = raw.split(',').map(s=>s.trim()).filter(Boolean), found=[], missing=[], seen=new Set();
  for (const name of names) { const key=normalize(name); if(seen.has(key)) continue; seen.add(key); const vehicle=findVehicle(name); if(vehicle) found.push(vehicle); else missing.push(name); }
  if (missing.length) { output.innerHTML = `<div class="warning"><strong>LINEUP NO ENCONTRADO</strong><br>No se pudo verificar el lineup exacto porque faltan en la base de datos:<br><br>${missing.map(escapeHtml).join('<br>')}</div>`; return; }
  const nations=[...new Set(found.map(v=>normalize(v.nation)).filter(Boolean))], brs=found.map(v=>v.br).filter(br=>typeof br==='number');
  const brText=brs.length===found.length?`BR ${Math.min(...brs).toFixed(1)}–${Math.max(...brs).toFixed(1)}`:'BR pendiente en uno o más vehículos';
  const nationText=nations.length===1?found[0].nation:'Naciones mixtas', roles=[...new Set(found.map(role))];
  output.innerHTML=`<div class="result-head"><div><p class="eyebrow">EXACT LINEUP SEARCH</p><h2>Lineup verificado</h2><p class="hero-text">${found.length} vehículos · ${escapeHtml(nationText)} · ${escapeHtml(brText)}</p></div><span class="badge">COINCIDENCIA EXACTA</span></div><div class="cards">${found.map((v,i)=>card(v,i===0)).join('')}</div><div class="data-note">Roles detectados: ${escapeHtml(roles.join(', '))}.</div>`;
}
async function loadDatabase() {
  try { const response=await fetch('vehicles.json',{cache:'no-store'}); if(!response.ok) throw new Error('HTTP '+response.status); const data=await response.json(); vehicles=Array.isArray(data.vehicles)?data.vehicles:[]; document.getElementById('vehicleCount').textContent=vehicles.length; document.getElementById('verifiedCount').textContent=vehicles.filter(v=>typeof v.br==='number').length; vehicleList.innerHTML=vehicles.map(v=>`<option value="${escapeHtml(v.name)}"></option>`).join(''); }
  catch(error) { document.getElementById('vehicleCount').textContent='ERR'; document.getElementById('verifiedCount').textContent='ERR'; output.innerHTML=`<div class="warning"><strong>DATABASE OFFLINE</strong><br>No se pudo cargar vehicles.json.</div>`; }
}
document.getElementById('analyzeBtn').addEventListener('click',analyze); document.getElementById('lineupBtn').addEventListener('click',generateLineup); document.getElementById('exactLineupBtn').addEventListener('click',searchExactLineup); vehicleInput.addEventListener('keydown',e=>{if(e.key==='Enter')analyze();}); lineupInput.addEventListener('keydown',e=>{if(e.key==='Enter')searchExactLineup();}); loadDatabase();
