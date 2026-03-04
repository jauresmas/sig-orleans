"""
generate_map.py
===============
Analyse les données et génère la carte interactive d'Orléans.
Exécuter APRÈS fetch_data.py :  python scripts/generate_map.py
"""

import json
import os
import math
from collections import defaultdict

OUTPUT_DIR = "output"
DATA_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# Chargement des données GeoJSON
# ─────────────────────────────────────────────
def load_geojson(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"  ⚠️  Fichier manquant : {path}  → données vides utilisées")
        return {"type": "FeatureCollection", "features": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)

print("📂 Chargement des données...")
arrets      = load_geojson("arrets_transport.geojson")
hopitaux    = load_geojson("hopitaux.geojson")
ecoles      = load_geojson("ecoles.geojson")
pharmacies  = load_geojson("pharmacies.geojson")
parcs       = load_geojson("parcs.geojson")

# ─────────────────────────────────────────────
# Statistiques
# ─────────────────────────────────────────────
stats = {
    "arrets":     len(arrets["features"]),
    "hopitaux":   len(hopitaux["features"]),
    "ecoles":     len(ecoles["features"]),
    "pharmacies": len(pharmacies["features"]),
    "parcs":      len(parcs["features"]),
}
print(f"  🚌 Arrêts de transport : {stats['arrets']}")
print(f"  🏥 Hôpitaux            : {stats['hopitaux']}")
print(f"  🏫 Écoles              : {stats['ecoles']}")
print(f"  💊 Pharmacies          : {stats['pharmacies']}")
print(f"  🌿 Parcs               : {stats['parcs']}")

# Sauvegarder les stats pour le dashboard
with open(os.path.join(OUTPUT_DIR, "stats.json"), "w") as f:
    json.dump(stats, f)

# ─────────────────────────────────────────────
# Analyse densité de couverture transport
# ─────────────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def nearest_stop_distance(lat, lon, stops):
    """Distance en mètres vers l'arrêt le plus proche."""
    min_d = float("inf")
    for feat in stops["features"]:
        coords = feat["geometry"]["coordinates"]
        d = haversine(lat, lon, coords[1], coords[0])
        if d < min_d:
            min_d = d
    return min_d

# Calculer la distance aux transports pour hôpitaux et écoles
print("\n📊 Calcul des distances aux transports en commun...")

for feat in hopitaux["features"]:
    c = feat["geometry"]["coordinates"]
    feat["properties"]["dist_transport_m"] = round(nearest_stop_distance(c[1], c[0], arrets))

for feat in ecoles["features"]:
    c = feat["geometry"]["coordinates"]
    feat["properties"]["dist_transport_m"] = round(nearest_stop_distance(c[1], c[0], arrets))

# ─────────────────────────────────────────────
# Génération HTML de la carte
# ─────────────────────────────────────────────
print("\n🗺️  Génération de la carte interactive...")

def features_to_js(features, var_name):
    return f"const {var_name} = {json.dumps({'type':'FeatureCollection','features':features})};"

arrets_js     = features_to_js(arrets["features"],     "data_arrets")
hopitaux_js   = features_to_js(hopitaux["features"],   "data_hopitaux")
ecoles_js     = features_to_js(ecoles["features"],     "data_ecoles")
pharmacies_js = features_to_js(pharmacies["features"], "data_pharmacies")
parcs_js      = features_to_js(parcs["features"],      "data_parcs")

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SIG Orléans — Transports & Services Urbains</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <style>
    :root {{
      --bg:       #0d0f14;
      --surface:  #161820;
      --border:   #2a2d3a;
      --accent:   #e8c547;
      --accent2:  #4fc3f7;
      --accent3:  #ef5350;
      --green:    #66bb6a;
      --text:     #e8eaf0;
      --muted:    #6b7280;
      --font-h:   'Syne', sans-serif;
      --font-m:   'DM Mono', monospace;
    }}

    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:var(--bg); color:var(--text); font-family:var(--font-h); overflow:hidden; height:100vh; display:flex; flex-direction:column; }}

    /* ── HEADER ── */
    header {{
      display:flex; align-items:center; justify-content:space-between;
      padding:0 24px; height:56px; background:var(--surface);
      border-bottom:1px solid var(--border); flex-shrink:0; z-index:1000;
    }}
    .logo {{ display:flex; align-items:center; gap:10px; }}
    .logo-dot {{
      width:10px; height:10px; border-radius:50%; background:var(--accent);
      box-shadow:0 0 12px var(--accent);
      animation: pulse 2s ease-in-out infinite;
    }}
    @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.4}} }}
    .logo-text {{ font-size:15px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; }}
    .logo-sub {{ font-family:var(--font-m); font-size:11px; color:var(--muted); margin-left:4px; }}

    .header-stats {{
      display:flex; gap:20px; font-family:var(--font-m); font-size:12px;
    }}
    .hstat {{ display:flex; flex-direction:column; align-items:center; }}
    .hstat-val {{ font-size:18px; font-weight:500; color:var(--accent); line-height:1; }}
    .hstat-lbl {{ color:var(--muted); font-size:10px; margin-top:2px; }}

    /* ── LAYOUT ── */
    .main {{ display:flex; flex:1; overflow:hidden; }}

    /* ── SIDEBAR ── */
    aside {{
      width:260px; background:var(--surface); border-right:1px solid var(--border);
      display:flex; flex-direction:column; flex-shrink:0; overflow-y:auto;
    }}
    .section-title {{
      font-family:var(--font-m); font-size:9px; letter-spacing:0.15em;
      text-transform:uppercase; color:var(--muted);
      padding:16px 16px 8px;
    }}

    /* Couches */
    .layer-btn {{
      display:flex; align-items:center; gap:10px;
      padding:10px 16px; cursor:pointer;
      border:none; background:none; color:var(--text); width:100%;
      text-align:left; font-family:var(--font-h); font-size:13px;
      transition:background .15s;
      border-left:3px solid transparent;
    }}
    .layer-btn:hover {{ background:rgba(255,255,255,.04); }}
    .layer-btn.active {{ border-left-color:var(--accent); background:rgba(232,197,71,.06); }}
    .layer-dot {{ width:10px; height:10px; border-radius:50%; flex-shrink:0; }}
    .layer-count {{
      margin-left:auto; font-family:var(--font-m); font-size:11px;
      color:var(--muted); background:rgba(255,255,255,.07);
      padding:2px 7px; border-radius:99px;
    }}

    /* Info card */
    .info-card {{
      margin:12px; padding:14px; background:rgba(255,255,255,.03);
      border:1px solid var(--border); border-radius:8px;
    }}
    .info-card h4 {{ font-size:12px; color:var(--accent); margin-bottom:8px; font-weight:600; }}
    .info-row {{ display:flex; justify-content:space-between; font-size:11px; font-family:var(--font-m); color:var(--muted); margin:4px 0; }}
    .info-row span {{ color:var(--text); }}

    /* ── MAP ── */
    #map {{ flex:1; }}
    .leaflet-container {{ background:#0d0f14 !important; }}

    /* ── POPUP ── */
    .leaflet-popup-content-wrapper {{
      background:var(--surface) !important;
      border:1px solid var(--border) !important;
      border-radius:8px !important;
      box-shadow:0 8px 32px rgba(0,0,0,.6) !important;
      color:var(--text) !important;
      font-family:var(--font-h) !important;
    }}
    .leaflet-popup-tip {{ background:var(--surface) !important; }}
    .popup-title {{ font-weight:700; font-size:13px; margin-bottom:6px; color:var(--accent); }}
    .popup-row {{ font-size:11px; color:var(--muted); font-family:var(--font-m); margin:3px 0; }}
    .popup-row b {{ color:var(--text); }}

    /* ── BOTTOM BAR ── */
    .bottom-bar {{
      height:36px; background:var(--surface); border-top:1px solid var(--border);
      display:flex; align-items:center; padding:0 16px; gap:20px;
      font-family:var(--font-m); font-size:11px; color:var(--muted); flex-shrink:0;
    }}
    .bottom-bar span {{ display:flex; align-items:center; gap:6px; }}
    .live-dot {{ width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 6px var(--green); }}

    /* scrollbar */
    aside::-webkit-scrollbar {{ width:4px; }}
    aside::-webkit-scrollbar-track {{ background:transparent; }}
    aside::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:2px; }}
  </style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-dot"></div>
    <div>
      <span class="logo-text">SIG Orléans</span>
      <span class="logo-sub">/ Transports & Services</span>
    </div>
  </div>
  <div class="header-stats">
    <div class="hstat"><span class="hstat-val" id="hs-arrets">{stats['arrets']}</span><span class="hstat-lbl">Arrêts</span></div>
    <div class="hstat"><span class="hstat-val" id="hs-hop">{stats['hopitaux']}</span><span class="hstat-lbl">Hôpitaux</span></div>
    <div class="hstat"><span class="hstat-val" id="hs-eco">{stats['ecoles']}</span><span class="hstat-lbl">Écoles</span></div>
    <div class="hstat"><span class="hstat-val" id="hs-pharma">{stats['pharmacies']}</span><span class="hstat-lbl">Pharmacies</span></div>
    <div class="hstat"><span class="hstat-val" id="hs-parcs">{stats['parcs']}</span><span class="hstat-lbl">Parcs</span></div>
  </div>
</header>

<div class="main">
  <aside>
    <div class="section-title">Couches de données</div>

    <button class="layer-btn active" id="btn-arrets" onclick="toggleLayer('arrets')">
      <span class="layer-dot" style="background:#4fc3f7; box-shadow:0 0 6px #4fc3f7"></span>
      Transports
      <span class="layer-count">{stats['arrets']}</span>
    </button>
    <button class="layer-btn active" id="btn-hopitaux" onclick="toggleLayer('hopitaux')">
      <span class="layer-dot" style="background:#ef5350; box-shadow:0 0 6px #ef5350"></span>
      Hôpitaux
      <span class="layer-count">{stats['hopitaux']}</span>
    </button>
    <button class="layer-btn active" id="btn-ecoles" onclick="toggleLayer('ecoles')">
      <span class="layer-dot" style="background:#ffa726; box-shadow:0 0 6px #ffa726"></span>
      Écoles
      <span class="layer-count">{stats['ecoles']}</span>
    </button>
    <button class="layer-btn active" id="btn-pharmacies" onclick="toggleLayer('pharmacies')">
      <span class="layer-dot" style="background:#ab47bc; box-shadow:0 0 6px #ab47bc"></span>
      Pharmacies
      <span class="layer-count">{stats['pharmacies']}</span>
    </button>
    <button class="layer-btn active" id="btn-parcs" onclick="toggleLayer('parcs')">
      <span class="layer-dot" style="background:#66bb6a; box-shadow:0 0 6px #66bb6a"></span>
      Parcs
      <span class="layer-count">{stats['parcs']}</span>
    </button>

    <div class="section-title" style="margin-top:8px">Fond de carte</div>
    <button class="layer-btn active" id="btn-dark" onclick="setBasemap('dark')">
      <span class="layer-dot" style="background:#555"></span>
      Sombre
    </button>
    <button class="layer-btn" id="btn-osm" onclick="setBasemap('osm')">
      <span class="layer-dot" style="background:#4fc3f7"></span>
      OpenStreetMap
    </button>
    <button class="layer-btn" id="btn-satellite" onclick="setBasemap('satellite')">
      <span class="layer-dot" style="background:#66bb6a"></span>
      Satellite
    </button>

    <div class="section-title" style="margin-top:8px">Analyse</div>
    <div class="info-card">
      <h4>📍 Zone d'étude</h4>
      <div class="info-row">Ville <span>Orléans, France</span></div>
      <div class="info-row">Lat/Lon <span>47.90° / 1.90°</span></div>
      <div class="info-row">Source <span>OpenStreetMap</span></div>
    </div>
    <div class="info-card">
      <h4>ℹ️ Comment utiliser</h4>
      <div style="font-size:11px; color:var(--muted); line-height:1.7; font-family:var(--font-m)">
        Cliquez sur les boutons pour afficher/masquer les couches.<br><br>
        Cliquez sur un point de la carte pour voir ses détails.
      </div>
    </div>
  </aside>

  <div id="map"></div>
</div>

<div class="bottom-bar">
  <span><div class="live-dot"></div> Données OpenStreetMap</span>
  <span>🗺️ Leaflet.js</span>
  <span>🐍 Python + GeoPandas</span>
  <span style="margin-left:auto; color:#4fc3f7">Orléans, Loiret (45) — France</span>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
// ── Données injectées par Python ──
{arrets_js}
{hopitaux_js}
{ecoles_js}
{pharmacies_js}
{parcs_js}

// ── Carte ──
const map = L.map('map', {{
  center: [47.9029, 1.9039],
  zoom: 14,
  zoomControl: false
}});
L.control.zoom({{ position: 'topright' }}).addTo(map);

// ── Fonds de carte ──
const basemaps = {{
  dark: L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '© OpenStreetMap, © CARTO', maxZoom: 19
  }}),
  osm: L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '© OpenStreetMap', maxZoom: 19
  }}),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
    attribution: '© Esri', maxZoom: 19
  }})
}};
basemaps.dark.addTo(map);
let currentBase = 'dark';

function setBasemap(name) {{
  map.removeLayer(basemaps[currentBase]);
  basemaps[name].addTo(map);
  basemaps[name].bringToBack();
  currentBase = name;
  document.querySelectorAll('[id^=btn-dark],[id^=btn-osm],[id^=btn-satellite]').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + name).classList.add('active');
}}

// ── Helpers popup ──
function popupHTML(title, rows) {{
  let html = `<div class="popup-title">${{title}}</div>`;
  for (const [k,v] of Object.entries(rows)) {{
    if (v) html += `<div class="popup-row">${{k}} &nbsp;<b>${{v}}</b></div>`;
  }}
  return html;
}}

// ── Couches ──
const layers = {{}};

// Arrêts de transport
layers.arrets = L.geoJSON(data_arrets, {{
  pointToLayer: (f, latlng) => L.circleMarker(latlng, {{
    radius: 5, fillColor: '#4fc3f7', color: '#0d0f14', weight: 1,
    fillOpacity: 0.9
  }}),
  onEachFeature: (f, layer) => {{
    const p = f.properties;
    layer.bindPopup(popupHTML('🚌 ' + (p.name || 'Arrêt de transport'), {{
      'Type': p.highway || p.public_transport || p.railway,
      'Réseau': p.network,
      'Ref': p.ref
    }}));
  }}
}}).addTo(map);

// Hôpitaux
layers.hopitaux = L.geoJSON(data_hopitaux, {{
  pointToLayer: (f, latlng) => L.circleMarker(latlng, {{
    radius: 8, fillColor: '#ef5350', color: '#fff', weight: 1.5,
    fillOpacity: 0.95
  }}),
  onEachFeature: (f, layer) => {{
    const p = f.properties;
    layer.bindPopup(popupHTML('🏥 ' + (p.name || 'Hôpital'), {{
      'Adresse': p['addr:street'],
      'Téléphone': p.phone,
      'Distance TC': p.dist_transport_m ? p.dist_transport_m + ' m' : null
    }}));
  }}
}}).addTo(map);

// Écoles
layers.ecoles = L.geoJSON(data_ecoles, {{
  pointToLayer: (f, latlng) => L.circleMarker(latlng, {{
    radius: 6, fillColor: '#ffa726', color: '#0d0f14', weight: 1,
    fillOpacity: 0.9
  }}),
  onEachFeature: (f, layer) => {{
    const p = f.properties;
    layer.bindPopup(popupHTML('🏫 ' + (p.name || 'École'), {{
      'Type': p.amenity,
      'Adresse': p['addr:street'],
      'Distance TC': p.dist_transport_m ? p.dist_transport_m + ' m' : null
    }}));
  }}
}}).addTo(map);

// Pharmacies
layers.pharmacies = L.geoJSON(data_pharmacies, {{
  pointToLayer: (f, latlng) => L.circleMarker(latlng, {{
    radius: 5, fillColor: '#ab47bc', color: '#0d0f14', weight: 1,
    fillOpacity: 0.9
  }}),
  onEachFeature: (f, layer) => {{
    const p = f.properties;
    layer.bindPopup(popupHTML('💊 ' + (p.name || 'Pharmacie'), {{
      'Adresse': p['addr:street'],
      'Téléphone': p.phone
    }}));
  }}
}}).addTo(map);

// Parcs
layers.parcs = L.geoJSON(data_parcs, {{
  pointToLayer: (f, latlng) => L.circleMarker(latlng, {{
    radius: 6, fillColor: '#66bb6a', color: '#0d0f14', weight: 1,
    fillOpacity: 0.9
  }}),
  onEachFeature: (f, layer) => {{
    const p = f.properties;
    layer.bindPopup(popupHTML('🌿 ' + (p.name || 'Parc'), {{
      'Type': p.leisure
    }}));
  }}
}}).addTo(map);

// ── Toggle couches ──
const layerState = {{ arrets:true, hopitaux:true, ecoles:true, pharmacies:true, parcs:true }};

function toggleLayer(name) {{
  layerState[name] = !layerState[name];
  const btn = document.getElementById('btn-' + name);
  if (layerState[name]) {{
    layers[name].addTo(map);
    btn.classList.add('active');
  }} else {{
    map.removeLayer(layers[name]);
    btn.classList.remove('active');
  }}
}}
</script>
</body>
</html>"""

out_path = os.path.join(OUTPUT_DIR, "carte_orleans.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

# Copier aussi dans docs/ pour GitHub Pages
os.makedirs("docs", exist_ok=True)
import shutil
shutil.copy(out_path, "docs/index.html")

print(f"\n✅ Carte générée : {out_path}")
print(f"✅ Copie GitHub Pages : docs/index.html")
print(f"\n🌐 Ouvre output/carte_orleans.html dans ton navigateur !")
