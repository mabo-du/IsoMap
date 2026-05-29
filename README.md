# IsoMap

Isotopic and paleoecological data standardisation middleware. 

IsoMap is an open-source desktop application that automates the standardisation, validation, and export of legacy isotopic and paleoecological datasets for submission to centralised repositories (Neotoma, IsoArcH).

## Features

IsoMap is fully functional and features the following engines:
- **Import Engine**: Handles CSV and Excel spreadsheets with automatic encoding detection and type inference.
- **Column Mapping Engine**: Uses a robust fallback pipeline (exact → cache → fuzzy → embeddings → distribution → Valentine ensemble) to accurately map source columns to target repositories.
- **Valentine Ensemble Matching (v2.1)**: Employs structural schema-matching algorithms (Coma & Cupid) when semantic context is insufficient.
- **Chronology Engine**: Automates normalisation of uncalibrated and calibrated dates into a standard `cal_BP` format with a 1950 CE anchor.
- **Spatial Verification Engine**: Cleans unnormalised geographic coordinates and exports native `GeoDataFrame` bounds for validation.
- **Validation Engine**: Uses `pandera` dynamically injected with schema definitions to highlight exactly which dataset rows fail constraints.
- **Export & Provenance Engine**: Emits standard REST JSON arrays, NeoToma GeoJSONs, Excel files, LiPD archives, PANGAEA/NOAA formats, and Semantic Web RO-Crates for transparent reproducible provenance.
- **Automated Data Papers (v3.0)**: Built-in Jinja2 templating engine generates ESSD-compliant LaTeX manuscripts from harmonised datasets.

## Technology Stack
- **Frontend**: Tauri, React, Vite.
- **Backend (Sidecar)**: Python, Pandas, Pandera, GeoPandas.

## Getting Started

To launch the UI in development mode:
```bash
cd ui
npm install
npm run dev
```

To run unit tests on the backend engine:
```bash
pytest tests/
```
