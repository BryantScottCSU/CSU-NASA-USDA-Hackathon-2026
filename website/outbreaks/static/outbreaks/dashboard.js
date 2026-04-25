const fmt = new Intl.NumberFormat();
const $ = (id) => document.getElementById(id);

<<<<<<< HEAD
const COLORS = {
  green: '#1E4D2B',
  gold: '#C8C372',
  goldBright: '#F1E8A6',
  cream: '#f7f4df',
  muted: '#d8d0a2',
  rust: '#d97757'
};

=======
>>>>>>> origin/main
let map = L.map('map').setView([37.8, -96], 4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
let detectionLayer = L.layerGroup().addTo(map);
let airportLayer = L.layerGroup().addTo(map);
let countryChart, timeChart;
let selectedCountry = null;

function metric() { return $('metric').value; }
function state() { return $('state').value; }
function lag() { return $('lag').value; }
function season() { return $('season').value; }
function year() { return $('year').value; }

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return await res.json();
}

function setSummary(data) {
  const cards = [
    ['Detection rows', data.detections.rows],
    ['Total detections', Math.round(data.detections.total || 0)],
    ['Inbound passengers', Math.round(data.air_traffic.passengers || 0)],
    ['Air freight', Math.round(data.air_traffic.freight || 0)],
  ];
  $('summaryCards').innerHTML = cards.map(([label, value]) => `<div class="card"><div class="value">${fmt.format(value || 0)}</div><div class="label">${label}</div></div>`).join('');
}

function upsertOptions(select, values, firstLabel, firstValue='all') {
  select.innerHTML = `<option value="${firstValue}">${firstLabel}</option>` + values.map(v => `<option value="${v}">${v}</option>`).join('');
}

function renderCountries(rows) {
  const top = rows.slice(0, 12);
  const labels = top.map(r => r.country);
  const risk = top.map(r => r.risk_score);
  if (countryChart) countryChart.destroy();
  countryChart = new Chart($('countryChart'), {
    type: 'bar',
<<<<<<< HEAD
    data: { labels, 
    datasets: [{
    label: 'Risk score',
    data: risk,
    backgroundColor: COLORS.gold,
    borderColor: COLORS.goldBright,
    borderWidth: 1
    }] 
    },
    options: { responsive: true, plugins: { legend: { labels: { color: COLORS.cream } } }, scales: { x: { ticks: { color: COLORS.muted } }, y: { ticks: { y: { ticks: { color: COLORS.muted } } } } } }
=======
    data: { labels, datasets: [{ label: 'Risk score', data: risk }] },
    options: { responsive: true, plugins: { legend: { labels: { color: '#e5e7eb' } } }, scales: { x: { ticks: { color: '#cbd5e1' } }, y: { ticks: { color: '#cbd5e1' } } } }
>>>>>>> origin/main
  });

  $('countryTable').querySelector('tbody').innerHTML = rows.map(r => `
    <tr data-country="${r.country}">
      <td>${r.country}</td>
      <td>${r.correlation === null ? 'n/a' : r.correlation.toFixed(3)}</td>
      <td>${fmt.format(Math.round(r.traffic_total || 0))}</td>
      <td>${r.risk_score.toFixed(2)}</td>
    </tr>`).join('');
  document.querySelectorAll('#countryTable tbody tr').forEach(tr => {
    tr.addEventListener('click', () => {
      selectedCountry = tr.dataset.country;
      loadTimeseries();
      loadHotspots();
    });
  });
  if (!selectedCountry && rows.length) selectedCountry = rows[0].country;
}

async function loadCountries() {
  const data = await getJSON(`/api/countries/?metric=${metric()}&state=${encodeURIComponent(state())}&lag=${lag()}`);
  renderCountries(data.countries);
  await loadTimeseries();
}

async function loadTimeseries() {
  if (!selectedCountry) return;
  const data = await getJSON(`/api/timeseries/?metric=${metric()}&state=${encodeURIComponent(state())}&country=${encodeURIComponent(selectedCountry)}`);
  if (timeChart) timeChart.destroy();
  timeChart = new Chart($('timeChart'), {
    type: 'line',
    data: {
<<<<<<< HEAD
    labels: data.labels,
    datasets: [
        {
        label: `${selectedCountry} ${data.metric}`,
        data: data.traffic,
        yAxisID: 'yTraffic',
        tension: .25,
        borderColor: COLORS.gold,
        backgroundColor: COLORS.gold,
        pointBackgroundColor: COLORS.goldBright
        },
        {
        label: 'Fruit fly detections',
        data: data.detections,
        yAxisID: 'yDetect',
        tension: .25,
        borderColor: COLORS.rust,
        backgroundColor: COLORS.rust,
        pointBackgroundColor: COLORS.rust
        }
    ]
=======
      labels: data.labels,
      datasets: [
        { label: `${selectedCountry} ${data.metric}`, data: data.traffic, yAxisID: 'yTraffic', tension: .25 },
        { label: 'Fruit fly detections', data: data.detections, yAxisID: 'yDetect', tension: .25 }
      ]
>>>>>>> origin/main
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
<<<<<<< HEAD
      plugins: { legend: { labels: { color: COLORS.cream } } },
      scales: {
        x: { ticks: { color: COLORS.muted, maxTicksLimit: 10 } },
        yTraffic: { position: 'left', ticks: { color: COLORS.muted } },
        yDetect: { position: 'right', grid: { drawOnChartArea: false }, ticks: { color: COLORS.muted } }
=======
      plugins: { legend: { labels: { color: '#e5e7eb' } } },
      scales: {
        x: { ticks: { color: '#cbd5e1', maxTicksLimit: 10 } },
        yTraffic: { position: 'left', ticks: { color: '#cbd5e1' } },
        yDetect: { position: 'right', grid: { drawOnChartArea: false }, ticks: { color: '#cbd5e1' } }
>>>>>>> origin/main
      }
    }
  });
}

function radius(value) {
  return Math.max(4, Math.min(32, Math.sqrt(value || 0) / 40));
}

async function loadHotspots() {
  detectionLayer.clearLayers();
  airportLayer.clearLayers();
  const c = selectedCountry ? `&country=${encodeURIComponent(selectedCountry)}` : '';
  const data = await getJSON(`/api/hotspots/?metric=${metric()}&state=${encodeURIComponent(state())}&season=${season()}&year=${year()}${c}`);
  data.detections.forEach(p => {
<<<<<<< HEAD
    L.circleMarker([p.lat, p.lon], { radius: radius(p.value) + 2, color: COLORS.rust, fillOpacity: .45, weight: 1 })
=======
    L.circleMarker([p.lat, p.lon], { radius: radius(p.value) + 2, color: '#fb7185', fillOpacity: .45, weight: 1 })
>>>>>>> origin/main
      .bindPopup(`<b>Detection</b><br>${p.name}, ${p.state}<br>${p.year}-${String(p.month).padStart(2,'0')}<br>Count: ${fmt.format(Math.round(p.value))}`)
      .addTo(detectionLayer);
  });
  data.airports.forEach(p => {
<<<<<<< HEAD
    L.circleMarker([p.lat, p.lon], { radius: radius(p.value), color: COLORS.gold, fillOpacity: .35, weight: 1 })
=======
    L.circleMarker([p.lat, p.lon], { radius: radius(p.value), color: '#38bdf8', fillOpacity: .35, weight: 1 })
>>>>>>> origin/main
      .bindPopup(`<b>Inbound airport</b><br>${p.name}<br>${p.state}<br>${p.year}-${String(p.month).padStart(2,'0')}<br>${data.metric}: ${fmt.format(Math.round(p.value))}`)
      .addTo(airportLayer);
  });
  $('portsTable').querySelector('tbody').innerHTML = data.ports.map(p => `
    <tr><td>${p.year}</td><td>${p.port_name}</td><td>${p.state}</td><td>${fmt.format(Math.round(p.value || 0))}</td></tr>`).join('');
}

async function boot() {
  const [options, summary] = await Promise.all([getJSON('/api/options/'), getJSON('/api/summary/')]);
  upsertOptions($('state'), options.states, 'All states');
  upsertOptions($('year'), options.years, 'All years', '');
  setSummary(summary);
  await loadCountries();
  await loadHotspots();
}

$('refresh').addEventListener('click', async () => {
  selectedCountry = null;
  await loadCountries();
  await loadHotspots();
});

boot().catch(err => {
  console.error(err);
  alert('Dashboard failed to load. Did you run migrations and import_data? See README.md.');
});
