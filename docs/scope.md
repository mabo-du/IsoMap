# PROJECT 14 — Isotopic Data Standardisation & Mapping Tool
## Overview

A data wrangling desktop application specifically designed to help palaeontologists, archaeologists, and paleoecologists prepare their legacy isotopic and paleoecological datasets for submission to centralised repositories like Neotoma, IsoArcH, and the IsoMemo network. The current process requires researchers to manually map their bespoke column names, taxonomies, and chronologies to standardised schemas — a tedious, error-prone process that delays open-access publishing of critical datasets. This tool automates the schema mapping with intelligent column matching and vocabulary alignment.

## Target users

- Stable isotope researchers preparing data for IsoArcH/IsoMemo submission
- Paleoecologists submitting pollen, diatom, or vertebrate data to Neotoma
- Archaeozoologists standardising taxonomic lists
- Data stewards at research institutions
- Researchers with legacy datasets from pre-standardisation projects

## MVP scope (v1)

- Import researcher's data from CSV or Excel
- Auto-detect column types (measurement values, taxon names, dates, coordinates, sample IDs)
- Guided column mapping: suggest mappings between user's column names and target schema fields
- Taxonomic harmonisation: match user's taxon names to standard authority lists (ITIS, GBIF, Neotoma taxon list)
- Chronology normalisation: convert various date formats (14C BP, cal BP, cal BCE/CE, stratigraphic period) to standardised output
- Validation report: flag missing required fields, out-of-range values, and unresolved taxon names
- Export submission-ready files in target repository format

## Feature roadmap (v2+)

- Direct API submission to Neotoma and IsoArcH (with authentication)
- Support for the PANGAEA data publisher format (marine/Quaternary science repository)
- Machine learning column name matching (train on known good mappings)
- Batch processing of multiple datasets
- Provenance tracking: record transformation steps as a reproducible audit log
- ABCDE metadata schema support (Biological Collections Data)
- Coordinate system transformation (UTM to WGS84, etc.)

## Tech stack recommendation

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python | Pandas for data wrangling, excellent scientific data ecosystem |
| GUI | Tauri + React or PySide6 | Tauri gives a lighter desktop app; PySide6 if staying Python-native |
| Data manipulation | Pandas + openpyxl | Standard data wrangling |
| Taxonomy matching | FuzzyWuzzy/rapidfuzz + GBIF/ITIS API | Fuzzy string matching + authoritative lookups |
| Schema definitions | JSON Schema | Define target repository schemas as versioned JSON |
| Validation | Pandera or Great Expectations | Data quality validation with readable reports |

## Architecture notes

- Define **repository schemas as JSON Schema files** stored in the app. Each repository (Neotoma v2, IsoArcH, IsoMemo) has a schema file describing required/optional fields, data types, vocabularies, and validation rules. Schema files are versioned and can be updated independently of the app.
- The **column mapping step** uses multiple signals: (1) exact name match, (2) fuzzy string match, (3) data type inference, (4) value pattern matching (e.g., "values that look like δ13C measurements are likely isotope columns"). Show the user ranked suggestions and let them confirm.
- **Taxonomic matching** against GBIF and ITIS uses their APIs when online, and a bundled offline snapshot of common archaeological/paleoecological taxa when offline.
- The **transformation audit log** records every mapping decision as a reproducible JSON file. Researchers can share this "recipe" with collaborators so the transformation is fully documented and reproducible.

## Core data model

```
Dataset
  id, name, file_path, import_date, target_repository

ColumnMapping
  id, dataset_id, source_column, target_field, mapping_type (exact|fuzzy|manual), confidence

TaxonMapping
  id, dataset_id, source_name, matched_name, authority, match_score, status (accepted|pending|rejected)

ValidationIssue
  id, dataset_id, severity (error|warning), field, row_index, message, suggestion

TransformationLog
  id, dataset_id, created_at, steps (JSON array of transformation descriptions)
```

## Existing resources to leverage

- **Neotoma API v2.0** — submission protocol documentation: https://api.neotomadb.org
- **IsoArcH submission guidelines** — https://isoarch.org
- **GBIF Species API** — taxon name matching: https://www.gbif.org/developer/species
- **ITIS Solr API** — Integrated Taxonomic Information System
- **Neotoma Excel uploader** — existing submission tool to study and improve upon
- **PANGAEA submission format** — for marine/Quaternary science community

## Technical risks

- **Taxonomy ambiguity** — the same taxon name may be valid in one authority and a synonym in another. Build a disambiguation interface that shows authority source and accepted name.
- **Schema version drift** — target repositories update their schemas periodically. Build a schema update mechanism (check for new schema versions on launch) rather than hardcoding schemas.
- **Coordinate transformations** — isotopic sample data arrives in many CRS. Use pyproj for coordinate transformation but always show the user the before/after coordinates for validation.

---

## Deep Research Prompt — Project 14

> I am building an open-source isotopic and paleoecological data standardisation tool to help researchers prepare legacy datasets for submission to repositories like Neotoma and IsoArcH. I need research:
>
> 1. **Neotoma submission process**: What is the complete technical workflow for submitting data to the Neotoma Paleoecology Database? What are the required and optional fields for different dataset types (pollen, vertebrate, diatom, isotope)? Is there a documented API for programmatic submission, or does it require the Excel uploader tool? What validation checks does Neotoma apply?
>
> 2. **IsoArcH and IsoMemo submission**: What are the data submission requirements for IsoArcH and the broader IsoMemo network? What fields are required for isotopic datasets? What controlled vocabularies are used for sample type, tissue type, and element measured? Are there API endpoints for submission?
>
> 3. **Taxonomic authority APIs**: What are the GBIF Species Match API and ITIS Solr API? What are their endpoints, request formats, and response structures for taxon name matching? What other taxonomic authority services are used in paleoecological databases (WoRMS for marine, Fishbase, etc.)?
>
> 4. **Data quality standards for isotopic data**: What are the recommended reporting standards for stable isotope data in archaeology and paleoecology? Cover the recommendations of the IsoMemo Data Reporting Standards paper and any other published guidelines for δ13C, δ15N, δ18O, and 87Sr/86Sr data.
>
> 5. **Column name matching algorithms**: What ML or NLP approaches work best for automatically matching column names in messy research spreadsheets to standardised schema fields? Are there existing open-source tools for schema mapping in data integration that could be repurposed?
>
> 6. **PANGAEA and other repositories**: What other major paleoecological data repositories exist (PANGAEA, NOAA Paleoclimatology, Copernicus)? What are their submission formats and how do they relate to Neotoma's format?

---
---
