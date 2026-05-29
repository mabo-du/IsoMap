# Deep Research Dossier: IsoMap v2.0 & v3.0 Roadmap

This document outlines the findings from a deep research dive into the architectural and ecosystem requirements for IsoMap's upcoming v2.0 and v3.0 features.

---

## 1. Repository Specifications & LiPD (v2.0)

### 1.1 LiPD (Linked Paleo Data) Architecture
*   **Finding:** The modern, actively maintained Python package for this is **PyLiPD**, which officially supersedes the deprecated "LiPD Utilities". 
*   **Implementation Strategy:** `PyLiPD` is built heavily on `rdflib` and converts LiPD formats into Semantic Web RDF graphs. To integrate this into IsoMap without forcing users to learn SPARQL, we can use `PyLiPD` to serialize our Pandas dataframes directly into LiPD JSON-LD files on export.
*   **Resource:** [PyLiPD Documentation](https://pylipd.readthedocs.io/)

### 1.2 PANGAEA & NOAA NCEI Ingestion APIs
> [!WARNING]
> Neither PANGAEA nor NOAA NCEI support public, programmatic REST APIs for *ingesting* or submitting new datasets. Both rely on highly curated, human-in-the-loop editorial processes.

*   **PANGAEA:** Operates via a strict manual web submission portal and issue tracking (JIRA). It utilizes ORCID authentication and assigns an editor to manually vet the data.
*   **NOAA NCEI:** Requires researchers to email specific data templates (e.g., ITRDB, IMPD) to `paleo@noaa.gov` for manual review by data managers.
*   **Implementation Strategy:** IsoMap cannot push data directly. Instead, we must pivot our "Export Engine" to generate **100% compliant, pre-formatted Excel/CSV submission templates** tailored explicitly to the PANGAEA web portal requirements and NOAA email specifications.

---

## 2. Machine Learning Feasibility for Desktop (v2.1)

### 2.1 SciBERT Desktop Memory Footprint
*   **Finding:** Raw SciBERT (FP32) is heavily memory-bound and would overwhelm a standard desktop CPU in an offline Tauri application. However, **ONNX Runtime INT8 Quantisation** is highly effective here.
*   **Impact:** Quantising SciBERT dynamically to 8-bit integers (INT8) reduces the memory footprint by **~4x** and accelerates CPU inference by **2x to 3x** with minimal accuracy loss (<1%). 
*   **Implementation Strategy:** We should bundle `onnxruntime` in the Python sidecar and load a pre-quantised `scibert-int8.onnx` model file to maintain offline agility on standard researcher laptops.

### 2.2 Valentine Ensemble Matching
*   **Finding:** The `valentine` Python library is actively maintained and explicitly supports Python versions **3.10 through 3.14**.
*   **Implementation Strategy:** It will seamlessly drop into our current Python 3.12/3.13 backend without dependency clashes. We can integrate it as a superior stage in our 6-Stage Matching Pipeline, replacing or augmenting the current fuzzy logic block.

---

## 3. Advanced Provenance & Data Papers (v3.0)

### 3.1 RO-Crate vs. Frictionless Data
*   **Finding:** RO-Crate and Frictionless Data are not competing standards; they are *complementary*. Frictionless excels at validating tabular schema logic, while RO-Crate excels at semantic, linked-data provenance (using JSON-LD and Schema.org).
*   **Implementation Strategy:** The best practice is **inclusion**. IsoMap v3.0 should use RO-Crate as the master archival container (`ro-crate-metadata.json`) and embed our existing Frictionless `datapackage.json` inside it as a "Data Entity."

### 3.2 Automated Data Paper Generation (ESSD / JOAD)
*   **Finding:** Journals like Earth System Science Data (ESSD) and the Journal of Open Archaeology Data (JOAD) mandate strict layouts, specific "Data Availability" sections requiring DOIs, and transparent methodologies.
*   **Implementation Strategy:** Copernicus (publisher of ESSD) provides official LaTeX templates. IsoMap can integrate a templating engine (like `Jinja2`) to programmatically inject the RO-Crate metadata, validation summaries, and methodology hashes directly into the `.tex` files. Researchers would then just compile the PDF.

---

## Conclusion & Recommendations

The v2/v3 roadmap is highly viable, but requires a strategic pivot regarding repository ingestion (API push -> Template generation). The ML footprint is manageable via ONNX, and the provenance upgrade is additive rather than a complete rewrite.

**Recommended Next Step:** Prioritize integrating `PyLiPD` and drafting the NOAA/PANGAEA Excel export templates, as these offer the most immediate value for data harmonisation.
