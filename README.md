# 🗺️ SIG Orléans — Transports & Services Urbains

Projet SIG complet réalisé dans **GitHub Codespaces** : collecte, analyse et visualisation des transports et services publics d'Orléans (France).

---

## 🚀 Démarrage rapide (GitHub Codespaces)

### 1. Ouvrir dans Codespaces
```
Code → Codespaces → Create codespace on main
```
L'environnement s'installe automatiquement (Python 3.11 + toutes les librairies).

### 2. Télécharger les données OSM
```bash
python scripts/fetch_data.py
```
Cela récupère depuis OpenStreetMap :
- 🚌 Arrêts de bus et tramway
- 🏥 Hôpitaux et cliniques
- 🏫 Écoles, universités
- 💊 Pharmacies
- 🌿 Parcs

### 3. Explorer dans Jupyter
```bash
jupyter notebook --ip=0.0.0.0 --no-browser notebooks/analyse.ipynb
```

### 4. Générer la carte interactive
```bash
python scripts/generate_map.py
```
→ Crée `output/carte_orleans.html` (ouvrir dans le navigateur)
→ Crée `docs/index.html` (pour GitHub Pages)

---

## 📂 Structure du projet

```
sig-orleans/
├── .devcontainer/
│   └── devcontainer.json       ← Config Codespaces automatique
├── data/                       ← Données GeoJSON (générées par fetch_data.py)
│   ├── arrets_transport.geojson
│   ├── hopitaux.geojson
│   ├── ecoles.geojson
│   ├── pharmacies.geojson
│   └── parcs.geojson
├── notebooks/
│   └── analyse.ipynb           ← Analyse + graphiques
├── output/                     ← Résultats générés
│   ├── carte_orleans.html      ← Carte interactive
│   ├── analyse_orleans.png     ← Graphiques statistiques
│   └── stats.json              ← Statistiques JSON
├── scripts/
│   ├── fetch_data.py           ← Téléchargement OSM
│   └── generate_map.py         ← Génération carte HTML
├── docs/
│   └── index.html              ← GitHub Pages (carte publique)
└── README.md
```

---

## 🌐 Publier sur GitHub Pages

1. Dans GitHub → Settings → Pages
2. Source → "Deploy from branch"
3. Branch: `main`, Folder: `/docs`
4. ✅ Ta carte est accessible à : `https://[ton-pseudo].github.io/sig-orleans`

---

## 🛠️ Technologies utilisées

| Outil | Rôle |
|-------|------|
| Python 3.11 | Langage principal |
| GeoPandas | Analyse spatiale |
| Pandas | Traitement des données |
| Matplotlib | Graphiques |
| Leaflet.js | Carte web interactive |
| Overpass API | Accès données OpenStreetMap |
| GitHub Codespaces | Environnement de développement cloud |
| GitHub Pages | Publication web gratuite |

---

## 📊 Ce que la carte montre

- **Arrêts de transport** (bleu) — tous les arrêts bus et tram
- **Hôpitaux** (rouge) — avec distance au transport en commun le plus proche
- **Écoles** (orange) — accessibilité aux transports
- **Pharmacies** (violet) — répartition spatiale
- **Parcs** (vert) — espaces verts

Chaque couche est **activable/désactivable** et chaque point est **cliquable** pour voir ses détails.

---

## 📝 Aller plus loin

- Ajouter les **lignes de tramway** (couche polylignes)
- Calculer des **zones d'accessibilité** (isochrones)
- Intégrer les **données de population** par quartier
- Comparer avec **d'autres villes** (Tours, Blois...)

---

*Données © OpenStreetMap contributors — Licence ODbL*
