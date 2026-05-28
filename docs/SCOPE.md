# IsoMap — Project Scoping Document

> **Version:** 1.0 · **Date:** 2026-05-29 · **Author:** Marcus Quinn
> **Status:** Draft — Pending Review

---

## 1. Vision & Problem Statement

### The Problem

Palaeontologists, archaeologists, archaeozoologists, and paleoecologists generate vast quantities of isotopic and paleoecological data — δ13C, δ15N, δ18O, δ34S, ⁸⁷Sr/⁸⁶Sr measurements, pollen counts, vertebrate fauna assemblages, and more. These datasets are collected over decades using bespoke spreadsheet formats with idiosyncratic column names, heterogeneous taxonomic classifications, incompatible chronological systems, and inconsistent reporting of analytical metadata.

To make this data findable, accessible, interoperable, and reusable (FAIR), researchers must submit it to centralised repositories — **Neotoma**, **IsoArcH**, **IsoMemo**, **PANGAEA**, and others. This submission process currently requires:

- Manually mapping dozens of column names to rigid repository schemas
- Resolving taxonomic names against multiple authority lists (GBIF, ITIS, WoRMS, PBDB)
- Converting between calendar year conventions (¹⁴C BP, cal BP, cal BCE/CE, ka, Ma)
- Validating geochemical quality indicators (C:N ratios, collagen yields, diagenesis screening)
- Transforming coordinate reference systems (UTM → WGS84, DMS → decimal degrees)
- Formatting outputs to repository-specific template structures

This process is **tedious, error-prone, and a major bottleneck** preventing open-access publication of critical palaeoscience datasets. Rejection rates from repositories remain high due to unresolved taxonomic synonyms, malformed coordinates, incomplete metadata, and missing quality indicators.

### The Solution

**IsoMap** is an open-source desktop application that automates the standardisation, validation, and export of legacy isotopic and paleoecological datasets for submission to centralised repositories. It acts as an intelligent middleware layer between a researcher's messy spreadsheet and the rigid schema requirements of target repositories.

### The Name

**IsoMap** — from *isotope* + *map/mapping*. The tool maps isotopic and paleoecological data from legacy formats to standardised repository schemas, while also mapping spatial coordinates and taxonomic nomenclature.

---

## 2. Target Users

| User Persona | Description | Primary Workflow |
|---|---|---|
| **Stable isotope researcher** | Preparing δ13C/δ15N/δ18O/⁸⁷Sr/⁸⁶Sr data for IsoArcH/IsoMemo | Column mapping → quality validation → template export |
| **Paleoecologist** | Submitting pollen, diatom, or vertebrate data to Neotoma | Taxonomy resolution → chronology normalisation → DataBUS upload |
| **Archaeozoologist** | Standardising fauna assemblage taxonomic lists | Taxonomy matching → controlled vocabulary alignment |
| **Paleoclimatologist** | Submitting speleothem, coral, or ice core data to NOAA/PANGAEA | Schema mapping → unit normalisation → tabular export |
| **Data steward** | Institutional data manager curating legacy datasets | Batch processing → validation reports → audit trails |
| **Legacy data researcher** | Researchers with pre-standardisation project datasets | Import → guided mapping → iterative validation → export |

---

## 3. Target Repository Ecosystem

IsoMap must support export to these repositories, listed in priority order:

### Tier 1 — MVP Targets

| Repository | Domain | Submission Mechanism | Schema Type |
|---|---|---|---|
| **Neotoma** | Multiproxy paleoecology (Pliocene–Holocene) | DataBUS Python scripts → holding database → steward review | Strict relational PostgreSQL (181 tables, 1074 columns). YAML crosswalk templates. |
| **IsoArcH** | Bioarchaeological isotopic data | Excel/Grist template upload → web form validation → DOI minting | Template-driven. Strict controlled vocabularies via dropdown validation. No public API for submission. |

### Tier 2 — v2 Targets

| Repository | Domain | Submission Mechanism | Schema Type |
|---|---|---|---|
| **PANGAEA** | Earth & environmental science (general) | Web form + TAB-delimited UTF-8 files → editorial curation → DOI | Flexible parameter-code system. OAI-PMH + REST API for retrieval. |
| **IsoMemo Network** | Federated isotopic databases (AfriArch, IsoMad, MAIA, CERN, FRUIT, MedIsoPal) | Via IsoArcH or constituent database templates | Cross-database schema differences by sub-network. |
| **NOAA Paleoclimatology** | Speleothem, coral, tree-ring, ice core | Semi-manual email to curator; JSON REST API for retrieval | Template-based text files. |

### Tier 3 — Future Targets

| Repository | Domain | Notes |
|---|---|---|
| **Open Context** | Archaeological data publishing | Dublin Core metadata standard |
| **tDAR** | Digital Archaeological Record | Dublin Core + custom fields, web interface |
| **StraboSpot** | Structural geology/stratigraphy | GeoJSON hierarchy, HTTP REST API |
| **LiPD** | Linked Paleo Data container | Hierarchical JSON-LD format; bridge between Neotoma and NOAA |
| **IsoBank** | Centralised isotopic repository | Overlapping schema with IsoMemo |

---

## 4. MVP Scope (v1.0)

### Core Workflow

```
Import → Auto-Detect → Map → Validate → Export
```

### 4.1 Data Import

- Import from CSV and Excel (`.xlsx`, `.xls`) formats
- Handle common encoding issues (UTF-8, Latin-1, Windows-1252)
- Preview imported data with automatic column type inference
- Support for multi-sheet Excel workbooks (one sheet per dataset)

### 4.2 Intelligent Column Mapping

Automated schema mapping using a hierarchical fallback pipeline:

1. **Exact normalised match** — strip whitespace, lowercase, remove special characters
2. **User preference dictionary** — query local SQLite cache of previously resolved manual overrides
3. **Fuzzy string match** — Jaro-Winkler / Levenshtein distance via rapidfuzz
4. **Semantic embedding similarity** — cosine distance between source column embedding and target schema embeddings using `all-MiniLM-L6-v2` (~80 MB, offline-capable)
5. **Value distribution profiling** — statistical analysis of row values (e.g., values between −25‰ and −10‰ → δ13C; positive integers 1000–50000 → uncalibrated ¹⁴C BP)
6. **Manual mapping** — user confirms or overrides all suggestions

Present ranked suggestions with confidence scores. Store user overrides for learning.

### 4.3 Taxonomic Harmonisation

- Match user's taxon names against standard authority lists:
  - **GBIF Species Match API** (`/v1/species/match`) — primary authority for ecological taxa
  - **ITIS Solr API** — North American focus, TSN-based resolution
  - **WoRMS** — marine taxa (foraminifera, diatoms, ostracodes)
  - **PBDB** — extinct/fossil taxa not in modern registries
  - **Neotoma internal taxon list** (`/v2.0/data/taxa`) — when targeting Neotoma
- Handle synonymy chains (A → B → C) with user-facing disambiguation interface
- Bundled offline taxonomy snapshots for field use (SQLite/DuckDB)
- Store custom taxon resolutions in local dictionary

### 4.4 Chronology Normalisation

- Parse heterogeneous date formats: ¹⁴C BP, cal BP, cal BCE/CE, ka, Ma, stratigraphic periods
- Distinguish uncalibrated vs calibrated ages
- Map to target repository fields (e.g., Neotoma's `ChronControls` and `SampleAges` tables)
- Support controlled vocabularies for dating methods (radiocarbon, OSL/TL, U-series, K-Ar, Ar-Ar, AAR)
- Support controlled vocabularies for stratigraphic periods (NALMA, MIS stages)

### 4.5 Validation Engine

Implement using **Pandera** (DataFrame-native, lightweight, fast):

| Validation Category | Examples |
|---|---|
| **Schema completeness** | Required fields present, investigator name not null |
| **Data type correctness** | Isotope values are floats, not strings with `<` or `~` |
| **Controlled vocabulary compliance** | Material type matches IsoArcH vocabulary list |
| **Cross-field logical consistency** | If material = "bone collagen", then C:N ratio must be 2.9–3.6 |
| **Scientific value ranges** | δ13C: −35‰ to +5‰; δ15N: −5‰ to +25‰; C:N atomic: 2.9–3.6 |
| **Spatial validity** | Point-in-polygon check (terrestrial site not in ocean) |
| **Taxon resolution status** | All taxa resolved or flagged for manual review |
| **Duplicate detection** | Duplicate sample IDs or coordinates within dataset |
| **Collagen quality** | C:N ratio, %C >30%, %N >11%, collagen yield >1% |
| **Carbonate diagenesis** | FTIR splitting factor, Mn/Fe ratios flagged |

**Severity levels:**
- 🔴 **Blocking Error** — prevents repository submission
- 🟡 **Warning** — allows submission, flags for curator review
- 🔵 **Informational** — best-practice suggestion

**UX pattern:** Aggregate errors by type and column (e.g., "Column *C:N Ratio* contains 45 values outside 2.9–3.6"). Click-through to filtered DataFrame view of offending rows.

### 4.6 Export

- Generate submission-ready files in target repository format:
  - **Neotoma:** YAML crosswalk template + mapped CSV for DataBUS pipeline
  - **IsoArcH:** Populated Excel template matching IsoArcH Grist schema
- Transformation audit log (JSON) recording every mapping decision

---

## 5. Feature Roadmap (v2.0+)

### Phase 2 — Extended Repository Support

- [ ] PANGAEA TAB-delimited export with editorial metadata
- [ ] NOAA Paleoclimatology template export
- [ ] LiPD hierarchical JSON-LD container export
- [ ] IsoMemo sub-network template variants (AfriArch, IsoMad, etc.)

### Phase 3 — Advanced Automation

- [ ] Direct API submission to Neotoma holding database (with authentication)
- [ ] ML-powered column name matching (train on accumulated user correction data)
- [ ] SciBERT embeddings for domain-specific semantic matching (768-dim, scientific pre-training)
- [ ] Batch processing of multiple datasets
- [ ] Radiocarbon calibration engine (IntCal20/Marine20/SHCal20 probability distributions)

### Phase 4 — Provenance & Reproducibility

- [ ] PROV-O (W3C) compatible provenance graph generation
- [ ] RO-Crate (Research Object Crate) packaging of datasets + transformation logs
- [ ] Frictionless Data Package export with `datapackage.json` manifest
- [ ] Auto-generated methodology section text for data papers (ESSD, JOAD, Scientific Data)
- [ ] Coordinate system transformation (UTM → WGS84 via pyproj, `always_xy=True`)
- [ ] Gazetteer enrichment (GeoNames, Getty Thesaurus) for text-based site localities

### Phase 5 — Ecosystem Integration

- [ ] ORCID identifier capture for dataset contributors
- [ ] DOI cross-referencing across repositories (prevent deduplication conflicts)
- [ ] Unit normalisation engine (ppm ↔ mg/kg ↔ wt%; ‰ VPDB ↔ ‰ VSMOW) via Pint
- [ ] Uncertainty propagation and missing-σ flagging
- [ ] Image/spectral data linkage (SEM, FTIR, XRD → tabular row IDs)
- [ ] Data paper generation (draft data descriptor manuscripts)
- [ ] Embargo and access control configuration per repository
- [ ] Collaborative workflows (shared transformation logs via GitHub/OSF)

---

## 6. Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Language** | Python 3.12+ | Pandas ecosystem, scientific computing libraries, data wrangling |
| **GUI** | Tauri + React frontend with Python sidecar | Lightweight cross-platform desktop app; modern UI; Python backend for data logic |
| **Alternative GUI** | PySide6 | Fallback if staying fully Python-native (simpler deployment, single language) |
| **Data manipulation** | Pandas + openpyxl + xlrd | Standard data wrangling and Excel I/O |
| **Taxonomy matching** | rapidfuzz + GBIF/ITIS/WoRMS/PBDB APIs | Fuzzy string matching + authoritative lookups |
| **Schema definitions** | JSON Schema (versioned) | Define target repository schemas as declarative, updatable JSON files |
| **Validation** | Pandera | DataFrame-native, lightweight, fast vectorized execution, readable reports |
| **Embedding model** | all-MiniLM-L6-v2 (~80 MB) | Offline-capable semantic similarity for column name matching |
| **Local database** | SQLite or DuckDB | Taxonomy snapshots, user preference dictionary, transformation logs |
| **CRS transformation** | pyproj | Coordinate reference system detection and transformation |
| **Spatial validation** | shapely + geopandas | Point-in-polygon geometry checks |
| **Packaging** | PyInstaller / cx_Freeze / conda-pack | Cross-platform standalone executables (Windows, macOS, Linux) |
| **Schema registry** | GitHub-hosted JSON files | Dynamic schema updates without full app recompilation |

---

## 7. Core Data Model

```
Dataset
  id, name, file_path, import_date, target_repository, status

ColumnMapping
  id, dataset_id, source_column, target_field, mapping_type (exact|fuzzy|semantic|value_dist|manual),
  confidence, user_override

TaxonMapping
  id, dataset_id, source_name, matched_name, authority (GBIF|ITIS|WoRMS|PBDB|Neotoma),
  authority_id, match_score, match_type (EXACT|FUZZY|HIGHERRANK), status (accepted|pending|rejected),
  synonymy_chain

ChronologyMapping
  id, dataset_id, source_format, target_format, conversion_method, calibration_curve,
  original_value, converted_value, uncertainty

ValidationIssue
  id, dataset_id, severity (error|warning|info), category, field, row_index, message, suggestion

TransformationLog
  id, dataset_id, created_at, source_hash (SHA-256), steps (JSON array),
  prov_entities, prov_activities

UserPreference
  id, source_column_normalised, target_field, repository, frequency, last_used
```

---

## 8. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         IsoMap Desktop App                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐    │
│  │  Import      │  │  Column     │  │  Taxonomy            │    │
│  │  Engine      │→ │  Mapper     │→ │  Resolver            │    │
│  │  (CSV/XLSX)  │  │  (pipeline) │  │  (GBIF/ITIS/WoRMS)  │    │
│  └─────────────┘  └─────────────┘  └──────────────────────┘    │
│         │                │                   │                   │
│         ▼                ▼                   ▼                   │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐    │
│  │  Chronology │  │  Validation │  │  Export               │    │
│  │  Normaliser  │→ │  Engine     │→ │  Generator            │    │
│  │             │  │  (Pandera)  │  │  (YAML/Excel/TAB)    │    │
│  └─────────────┘  └─────────────┘  └──────────────────────┘    │
│         │                │                   │                   │
│         ▼                ▼                   ▼                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            Transformation Audit Log (JSON)                │   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌───────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ SQLite/  │  │ JSON      │  │ Embedding    │  │ Taxonomy │  │
│  │ DuckDB   │  │ Schema    │  │ Model Cache  │  │ Snapshot │  │
│  │ (prefs)  │  │ Registry  │  │ (MiniLM)     │  │ (offline)│  │
│  └──────────┘  └───────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Technical Risks

| Risk | Impact | Mitigation |
|---|---|---|
| **Taxonomy ambiguity** | Same name valid in one authority, synonym in another | Disambiguation UI showing authority source + accepted name; hierarchical resolution fallback (Neotoma list → GBIF → ITIS → PBDB) |
| **Schema version drift** | Target repositories update schemas periodically | GitHub-hosted schema registry; check for updates on launch; versioned JSON Schema files |
| **Coordinate axis inversion** | pyproj silently swaps lat/lon depending on CRS | Enforce `always_xy=True` on all Transformer instances; before/after coordinate display |
| **Neotoma API write access** | No public POST endpoint; requires steward mediation | Generate DataBUS-compatible YAML + CSV for holding database; don't attempt direct production writes |
| **IsoArcH has no API** | Template-only submission; no programmatic upload | Generate pre-filled Excel templates matching exact template structure and vocabularies |
| **Offline requirement** | Researchers work in remote field locations | Bundle taxonomy snapshots, calibration curves, schema files, and embedding model (~80 MB) |
| **GBIF backbone size** | Full download is several GB | Pre-process into indexed SQLite/DuckDB; bundle only common archaeological/paleoecological taxa |
| **Chronology complexity** | ¹⁴C calibration produces multimodal probability distributions | Phase 3: integrate calibration engine; MVP: parse and normalize date strings without recalibration |
| **Missing uncertainty data** | Legacy datasets often omit ±σ | Flag missing fields; prompt user for conservative estimates; document assumptions in audit log |
| **High metadata missingness** | SISAL: 80% missing drip type, 55% missing δ18O water equilibrium | Handle gracefully; allow null-but-warned submission; don't block on optional fields |

---

## 10. Success Criteria

| Criterion | Measurement |
|---|---|
| **Successful Neotoma submission** | At least 3 test datasets pass DataBUS validation and reach holding database |
| **Successful IsoArcH submission** | At least 3 test datasets pass IsoArcH template validation |
| **Column mapping accuracy** | ≥85% correct auto-suggestions on first pass (measured against benchmark test datasets) |
| **Taxonomy resolution rate** | ≥90% of taxa auto-resolved without manual intervention |
| **Validation coverage** | All blocking errors from Neotoma/IsoArcH documented rejection reasons are covered |
| **Offline operation** | Full workflow completes without network access (using bundled snapshots) |
| **Cross-platform** | Runs on Windows 10+, macOS 12+, Ubuntu 22.04+ |

---

## 11. Out of Scope (v1)

- Direct database writes to Neotoma production (requires steward mediation)
- Real-time radiocarbon calibration (Phase 3)
- Web-based deployment (desktop-first)
- Multi-user collaborative editing
- Image/spectral file processing
- Data paper manuscript generation

---

## 12. Related Projects in Digital Heritage Research

IsoMap is part of a broader suite of open-source tools for digital heritage research. A review of sibling projects in `~/Projects/` has revealed significant integration opportunities and shared architectural patterns:

| Project | Direct Architectural Synergies with IsoMap |
|---|---|
| **Libby** | **Chronology & GIS:** IsoMap can directly leverage Libby's SQLite-backed curve registry (IntCal20, SHCal20, Marine20) and its calib.org integration for marine reservoir correction (ΔR). IsoMap can also borrow Libby's Leaflet-based GIS curve selector logic. |
| **Paleo** | **Data Harvesting & Proxies:** Paleo's existing harvest scripts for Neotoma, PBDB, and PANGAEA can be directly imported into IsoMap for taxonomy offline database generation. Both projects share a Python FastAPI/sidecar architecture and geochemical proxy handling (e.g., δ13C, δ18O calibration). |
| **HOARD** | **Data Ingestion:** HOARD's 'ARK Direct Data Input' module (parsing CSV/JSON finds catalogues and sample registers) can be repurposed for IsoMap's Phase 1 import engine. Both utilize Frictionless Data patterns. |
| **StratiGraph** | **Data Schema:** StratiGraph uses the Harris Matrix Data Package (HMDP). IsoMap datasets with stratigraphic ordering (e.g., core depths, `AnalysisUnits`) can export relationships that seamlessly import into StratiGraph for DAG topological validation. |

---

## 13. Appendix: Key External Resources

| Resource | URL | Usage |
|---|---|---|
| Neotoma API v2 | `https://api.neotomadb.org/v2.0/` | Pre-submission validation, metadata enrichment, taxon resolution |
| Neotoma DataBUS | `https://github.com/NeotomaDB/DataBUS` | Programmatic bulk upload scripts |
| IsoArcH submission | `https://isoarch.org/submit` | Template download, submission guidelines |
| IsoMemo network | `https://isomemo.gea.mpg.de/` | Cross-network schema differences |
| GBIF Species Match | `https://api.gbif.org/v1/species/match` | Taxon name resolution |
| ITIS Web Services | `https://services.itis.gov/` | North American taxonomy |
| WoRMS REST API | `https://www.marinespecies.org/rest/` | Marine taxonomy |
| PBDB API | `https://paleobiodb.org/data1.2/` | Extinct/fossil taxonomy |
| PANGAEA Wiki | `https://wiki.pangaea.de/` | Submission format guidelines |
| Valentine library | `https://github.com/delftdata/valentine` | Schema matching algorithms |
| IntCal20 | `https://www.intcal.org/` | Radiocarbon calibration curves |
