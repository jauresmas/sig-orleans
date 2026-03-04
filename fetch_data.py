"""
fetch_data.py
============
Récupère automatiquement les données OpenStreetMap d'Orléans :
  - Arrêts de bus / tramway
  - Lignes de transport
  - Quartiers / limites de la ville
  - Hôpitaux, écoles, pharmacies

Exécuter : python scripts/fetch_data.py
"""

import requests
import json
import os

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def query_overpass(query: str) -> dict:
    print(f"  → Requête Overpass API...")
    response = requests.post(OVERPASS_URL, data={"data": query}, timeout=60)
    response.raise_for_status()
    return response.json()

def osm_to_geojson_points(data: dict) -> dict:
    """Convertit les nœuds OSM en GeoJSON FeatureCollection."""
    features = []
    for el in data.get("elements", []):
        if el["type"] == "node":
            feat = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [el["lon"], el["lat"]]},
                "properties": el.get("tags", {})
            }
            feat["properties"]["osm_id"] = el["id"]
            features.append(feat)
    return {"type": "FeatureCollection", "features": features}

def save_geojson(data: dict, filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Sauvegardé : {path} ({len(data['features'])} éléments)")

# ─────────────────────────────────────────────
# 1. Arrêts de bus et tramway
# ─────────────────────────────────────────────
print("\n📍 Récupération des arrêts de transport (bus + tram)...")
query_arrets = """
[out:json][timeout:60];
area["name"="Orléans"]["admin_level"="8"]->.orleans;
(
  node["highway"="bus_stop"](area.orleans);
  node["public_transport"="stop_position"](area.orleans);
  node["railway"="tram_stop"](area.orleans);
);
out body;
"""
data_arrets = query_overpass(query_arrets)
geojson_arrets = osm_to_geojson_points(data_arrets)
save_geojson(geojson_arrets, "arrets_transport.geojson")

# ─────────────────────────────────────────────
# 2. Hôpitaux
# ─────────────────────────────────────────────
print("\n🏥 Récupération des hôpitaux et cliniques...")
query_hopitaux = """
[out:json][timeout:60];
area["name"="Orléans"]["admin_level"="8"]->.orleans;
(
  node["amenity"="hospital"](area.orleans);
  node["amenity"="clinic"](area.orleans);
);
out body;
"""
data_hopitaux = query_overpass(query_hopitaux)
geojson_hopitaux = osm_to_geojson_points(data_hopitaux)
save_geojson(geojson_hopitaux, "hopitaux.geojson")

# ─────────────────────────────────────────────
# 3. Écoles
# ─────────────────────────────────────────────
print("\n🏫 Récupération des écoles...")
query_ecoles = """
[out:json][timeout:60];
area["name"="Orléans"]["admin_level"="8"]->.orleans;
(
  node["amenity"="school"](area.orleans);
  node["amenity"="university"](area.orleans);
  node["amenity"="college"](area.orleans);
);
out body;
"""
data_ecoles = query_overpass(query_ecoles)
geojson_ecoles = osm_to_geojson_points(data_ecoles)
save_geojson(geojson_ecoles, "ecoles.geojson")

# ─────────────────────────────────────────────
# 4. Pharmacies
# ─────────────────────────────────────────────
print("\n💊 Récupération des pharmacies...")
query_pharmacies = """
[out:json][timeout:60];
area["name"="Orléans"]["admin_level"="8"]->.orleans;
node["amenity"="pharmacy"](area.orleans);
out body;
"""
data_pharmacies = query_overpass(query_pharmacies)
geojson_pharmacies = osm_to_geojson_points(data_pharmacies)
save_geojson(geojson_pharmacies, "pharmacies.geojson")

# ─────────────────────────────────────────────
# 5. Parcs et espaces verts
# ─────────────────────────────────────────────
print("\n🌿 Récupération des parcs...")
query_parcs = """
[out:json][timeout:60];
area["name"="Orléans"]["admin_level"="8"]->.orleans;
node["leisure"="park"](area.orleans);
out body;
"""
data_parcs = query_overpass(query_parcs)
geojson_parcs = osm_to_geojson_points(data_parcs)
save_geojson(geojson_parcs, "parcs.geojson")

print("\n🎉 Toutes les données ont été téléchargées dans le dossier /data !")
print("👉 Lance maintenant : jupyter notebook notebooks/analyse.ipynb")
