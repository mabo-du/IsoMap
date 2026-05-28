# **Architecting Data Standardisation and Submission Workflows for Paleoscience: A Technical Evaluation**

## **1\. Neotoma Paleoecology Database — Submission Workflow**

The Neotoma Paleoecology Database represents a foundational infrastructure for multiproxy paleoscience, encompassing data from the Pliocene, Pleistocene, and Holocene epochs.1 Developing an integration pathway into Neotoma requires a comprehensive understanding of its tiered submission architecture, API constraints, and underlying relational data models, which differ substantially from generalist repositories.

### **End-to-End Submission Architecture**

The submission pathway for Neotoma v2 does not operate via a direct, unmediated API push to the production database. Instead, the architecture relies on a curation-mediated model designed to ensure rigorous taxonomic and chronological standardisation.2 Data enter the Neotoma ecosystem primarily via two routes: Tilia, a dedicated desktop curation application, or a Python-based bulk upload mechanism targeting an intermediary schema known as the neotomaholding database.3  
The integration workflow for a desktop data standardisation tool must follow this trajectory:

1. **Local Data Preparation**: Researchers assemble tabular data—such as pollen counts, vertebrate minimum number of individuals (MNI), or isotopic measurements—alongside extensive environmental metadata.  
2. **Template Mapping**: The dataset is mapped using a YAML configuration file that links local spreadsheet columns to Neotoma's strict relational tables (e.g., mapping a local "SiteName" column to ndb.sites.sitename). This acts as a semantic crosswalk between the user's legacy data and the Neotoma schema.3  
3. **Holding Database Insertion**: The mapped CSV and YAML files are programmatically pushed to neotomaholding, an isolated PostgreSQL database environment.3 This holding environment supports bulk uploads via tools like the DataBUS python scripts.3  
4. **Steward Review**: Authorized Neotoma data stewards retrieve the holding records via Tilia. Stewards perform final validations against controlled vocabularies, resolve taxonomic synonymies, and subsequently commit the data to the production PostgreSQL database.2  
5. **Public Availability**: Once committed by a steward, the dataset becomes instantly exposed via the public Neotoma v2 REST API, the Neotoma Explorer interactive web application, and programmatic clients such as the neotoma2 R package.4

### **Dataset Structures and Required Fields**

Neotoma normalises data across dozens of interlinked PostgreSQL tables to prevent data redundancy and ensure referential integrity.7 Submissions must strictly populate a hierarchical structure: *Site* ![][image1] *Collection Unit* ![][image1] *Analysis Unit* ![][image1] *Sample* ![][image1] *Data*.7  
Table 1 outlines the core structural requirements across major paleoscientific dataset types.

| Dataset Type | Core Required Fields | Dependent Tables & Controlled Vocabularies |
| :---- | :---- | :---- |
| **Pollen / Diatom / Ostracode** | Taxon name, count/abundance value, depth/thickness | Taxa, VariableElements, VariableUnits, FaciesTypes |
| **Vertebrate Fauna** | Taxon name, skeletal element (NISP/MNI), taphonomy | FAUNMAP constituent lists, Specimens, Taphonomy |
| **Geochronology** | Conventional ![][image2]), material dated, lab code | GeochronTypes, RadiocarbonCalibration, Geochronology 7 |
| **Stable Isotope** | Element system (C, N, O), measurement value, standard | IsotopeTypes, Specimens |

### **Programmatic API and Authentication Mechanisms**

While production insertion requires steward mediation, Neotoma exposes a highly developed RESTful JSON API (https://api.neotomadb.org/v2.0/) that a data wrangling tool must utilize heavily for pre-submission validation and metadata enrichment.4

* **Base URL**: https://api.neotomadb.org/  
* **Authentication**: Read-only queries do not require authentication tokens or OAuth. Write access to the holding database requires negotiated credentials, typically handled through direct collaboration with the Neotoma IT working group.  
* **Endpoint Examples**: The API allows querying via the /v2.0/data/sites endpoint to retrieve site coordinates using the sitename parameter.9 The /v2.0/data/taxa endpoint allows software to dynamically resolve taxon names against Neotoma's internal list.6 Complex querying parameters include ageyoung, ageold, altmin, and altmax.10  
* **Rate Limits**: Explicit rate limits are not formally documented, but aggressive automated querying can result in throttling. High-volume geographic or taxonomic queries should be paginated, leveraging the all\_data=TRUE parameter carefully or respecting default API offsets (typically returning 25 records per call).10

### **Dataset Versioning and the Stewardship Model**

Neotoma datasets are essentially immutable once published and assigned a Digital Object Identifier (DOI).9 Updates or modifications—such as revised chronologies or updated taxonomic identifications—generate a new version or an entirely new dataset record that is relationally linked to the original Collection Unit.  
The stewardship model is heavily decentralised, relying on domain-specific constituent databases (e.g., FAUNMAP for vertebrates, or the European Pollen Database).2 Appointed stewards conduct peer-review-level curation. Rejections during the holding phase typically stem from unresolved taxonomic synonyms, conflicting coordinate bounds (e.g., a terrestrial site bounding box falling into the ocean), or incomplete Bayesian age-depth models.

### **Chronologies and Age Models**

Chronological structures in Neotoma are highly explicit to accommodate advanced Bayesian age-depth modelling routines.7

* **ChronControls**: This table represents the anchor points (such as uncalibrated radiocarbon dates or identifiable tephra layers) used to construct the overall age model.1  
* **SampleAges**: This table stores the interpolated age for a specific biological sample down-core. To accurately capture chronological uncertainty, Neotoma stores age probability distributions using specific quantiles: sampleages.agelimitolder (0.5 quantile of the upper bound distribution), sampleages.age (0.5 quantile of the event age distribution), and sampleages.agelimityounger (0.5 quantile of the lower bound distribution).12 An integration tool must map median ages and error margins to these specific quantiles rather than attempting to pass a single static age string.

## **2\. IsoArcH and IsoMemo — Submission Requirements**

IsoArcH operates as a premier open-access repository specifically designed for bioarchaeological isotopic data, serving as a critical constituent node of the broader IsoMemo network.14 Data standardisation is strictly enforced prior to ingestion to permit large-scale, cross-regional meta-analyses.

### **IsoArcH Data Schema and Controlled Vocabularies**

Unlike Neotoma, IsoArcH does not expose a public REST or GraphQL API for programmatic data submission. Instead, the upload mechanism relies on highly structured, validation-enforced templates implemented via Excel spreadsheets or Grist (a relational, cloud-based spreadsheet tool).14  
The IsoArcH schema requires exhaustive contextualisation of the isotopic signal, bridging geochemical data with archaeological metadata:

* **Isotopic Values**: Measurements for $\\delta^{13}$C, $\\delta^{15}$N, $\\delta^{18}$O, $\\delta^{34}$S, and $^{87}![][image3]^{86}$Sr, alongside essential elemental yields (%C, %N) and atomic C:N ratios.19  
* **Sample Metadata**: Precise identification of the skeletal element (e.g., femur, rib, third molar) and the tissue type (e.g., bone collagen, enamel bioapatite, dentine carbonate, bone phosphate).22  
* **Site and Contextual Data**: Site name, precise spatial coordinates (Decimal Degrees WGS84), chronological period, cultural affiliation, burial type, biological sex, and age-at-death osteological estimations.23

Vocabularies are strictly controlled within the Grist and Excel templates via drop-down logic and data validation rules.24 Deviations from standard nomenclature—such as submitting "tooth" instead of specifying the precise tissue like "enamel bioapatite"—will result in validation failure upon upload.22

### **IsoMemo Data Reporting Standards and Network Integration**

IsoArcH feeds into the IsoMemo network, an initiative linking independent databases such as AfriArch, IsoMad, and MAIA.15 Data submitted must adhere to stringent community reporting standards to ensure interoperability across this network.

1. **Uncertainty Reporting**: Single-point isotope values are deemed insufficient for modern meta-analyses. Submissions must explicitly state the analytical uncertainty (![][image4]) calculated from in-house and international reference materials (e.g., IAEA-CH-6) measured during the specific analytical session.27  
2. **Calibration Status**: Data must be reported relative to established international standards (VPDB for $\\delta^{13}$C and $\\delta^{18}$O; AIR for $\\delta^{15}$N; VCDT for $\\delta^{34}$S).29  
3. **Cross-Database Schema Differences**: While IsoMemo attempts overarching harmonisation, constituent databases maintain internal metadata models reflecting their domain focus.15 For instance, IsoMad focuses heavily on terrestrial consumer diets and environmental modern baselines in Madagascar 29, whereas IsoArcH emphasizes Greco-Roman bioarchaeological and mortuary contexts.16 A standardisation tool must account for these structural differences by mapping generalized user metadata schemas to the specific required fields of the target sub-network.

### **Licensing and Access Control (Embargoes)**

IsoArcH mandates adherence to FAIR (Findable, Accessible, Interoperable, Reusable) and CARE (Collective benefit, Authority to control, Responsibility, Ethics) principles.16 While open access is the default—often licensed under Creative Commons CC BY-NC-SA 4.0 32—researchers retain ownership of their data.18 The repository supports mechanisms to embargo datasets pre-publication, or permanently restrict public access to sensitive data (such as isotopic profiles derived from ethically complex or culturally sensitive human remains), satisfying institutional ethical compliance requirements.17

## **3\. PANGAEA and Other Major Repositories**

PANGAEA is an internationally recognized, fully curated data publisher for earth and environmental sciences, functioning as a primary repository for paleoclimate and paleoecological data.33

### **PANGAEA Submission Formats and Interoperability**

PANGAEA requires submission via a guided web form, assisted by human editorial curators.33

* **Format Constraints**: Data must be structured as TAB-delimited text files utilizing UTF-8 encoding, or open spreadsheet formats.35  
* **Required Metadata**: Submissions necessitate a comprehensive dataset title, full literature references, project/grant associations, and structured principal investigator contacts.35  
* **API Architecture**: PANGAEA utilizes the Open Archives Initiative Protocol for Metadata Harvesting (OAI-PMH) alongside SOAP and REST web services.37 This architecture supports schema.org/dataset metadata exposure and cross-linking to genomic data and literature via Scholix.37  
* **Schema Overlap**: PANGAEA's structure is highly flexible and generalized compared to Neotoma or IsoArcH. A standardisation tool capable of mapping data to Neotoma's rigid ndb schema can trivially project a simplified tabular export suitable for PANGAEA submission. PANGAEA relies on dynamically defined parameter codes rather than a rigid, pre-defined central database schema, allowing for immense flexibility in proxy reporting.

### **Alternate Paleoscience Repositories**

The landscape of paleoscience repositories is highly fragmented, requiring diverse export capabilities:

* **NOAA Paleoclimatology**: The primary repository for speleothem, coral, tree-ring, and ice core data.38 Submissions are semi-manual (often requiring researchers to email templated text files to a curator). However, data retrieval is supported by a robust JSON REST API (e.g., utilizing the endpoint /access/paleo-search/study/search.json?dataTypeId=17 to filter specifically for speleothem records).41  
* **Copernicus Climate Change Service (C3S)**: ERA5 meteorological datasets and paleoclimate reconstructions are hosted on the Climate Data Store (CDS).42 Access and ingestion rely heavily on Python API clients (cdsapi) yielding complex NetCDF or GRIB array formats rather than simple tabular data.42  
* **Strabospot**: Focused on structural geology, stratigraphy, and petrology. The system is built on a strict spatial GeoJSON hierarchy, utilizing HTTP POST/GET interactions against an API to manage "spots" of geological data.44  
* **tDAR (The Digital Archaeological Record) & Open Context**: Designed for archaeological contexts, tDAR uses the Dublin Core metadata standard extended with custom archaeological fields.46 Uploading relies on user-driven web interfaces that generate tracking XML logs for versioning.46

While comprehensive shared metadata crosswalks (like strict RDF/Linked Open Data ontologies) are not yet universally implemented across all these databases, the widespread adoption of Dublin Core and DataCite for repository-level metadata provides a common denominator that a submission tool can leverage to ensure interoperability.

## **4\. Taxonomic Authority APIs — Technical Detail**

Paleoscience datasets are highly susceptible to taxonomic synonymy drift. A species considered valid in 1995 may have been reassigned to a new genus by 2024\. A local data wrangling tool must programmatically resolve legacy names against major taxonomic backbones to prevent repository rejection.

### **GBIF Species Match API**

The Global Biodiversity Information Facility (GBIF) provides a backbone taxonomy used universally across ecology.48

* **Endpoint**: https://api.gbif.org/v1/species/match.49  
* **Request Parameters**: Accepts parameters such as name, kingdom, rank, strict, and verbose (e.g., ?name=Passer+domesticus\&strict=false\&verbose=true).50  
* **Response Schema**: Returns a JSON object containing the usageKey (the internal GBIF taxon identifier), the taxonomic hierarchy (kingdomKey, phylumKey, etc.), the matchType (which can be EXACT, FUZZY, HIGHERRANK, or NONE), a confidence score ranging from 0 to 100, and a boolean synonym flag indicating if the submitted name is a junior synonym.50  
* **Rate Limits**: GBIF does not enforce hard rate limits or require an API key, but a descriptive User-Agent HTTP header is strongly advised to prevent temporary IP throttling during bulk queries.51

### **ITIS Solr API**

The Integrated Taxonomic Information System (ITIS) operates a high-performance Solr-backed web service.48

* **Endpoints**: Critical endpoints include getAcceptedNamesFromTSN and getFullHierarchyFromTSN.54  
* **Usage**: Queries map a legacy scientific name to a Taxonomic Serial Number (TSN). If the resulting TSN is flagged as a synonym, the software must route a secondary call to getAcceptedNamesFromTSN to retrieve the valid senior synonym.55 Output formats are flexible, supporting CSV, JSON, JSONP, and XML.56

### **WoRMS, PBDB, and Domain-Specific Authorities**

* **WoRMS (World Register of Marine Species)**: Essential for marine paleoecological proxies such as foraminifera, diatoms, and marine ostracodes. The REST API provides the /AphiaRecordsByMatchNames endpoint to execute advanced TAXAMATCH fuzzy algorithms, yielding an AphiaID.57  
* **Paleobiology Database (PBDB)**: Critical for deep-time extinct taxa not covered by modern biodiversity registries. The PBDB API returns extinct taxonomy and explicit taxonomic opinions resolving junior synonyms specific to paleontological literature.59  
* **Fishbase/SeaLifeBase**: Essential for archaeozoological fish bone identification. Programmatic access is best facilitated via R packages like rfishbase or equivalent direct REST calls to extract ecological data matching the taxonomic record.62

### **Resolution Workflows and Synonymy Chains**

Taxonomic synonymy is non-linear. A standardisation tool must account for chains (e.g., Taxon A is reclassified as Taxon B, which is later subsumed into Taxon C).  
The software architecture should implement a hierarchical resolution fallback. It should query Neotoma's internal list (/v2.0/data/taxa) first if the ultimate target is the Neotoma database, ensuring immediate compliance with their specific nomenclature.6 If targeting IsoArcH, it should query GBIF or ITIS. Conflicting resolutions (e.g., PBDB recognizing a generic reassignment that GBIF ignores due to differing update frequencies) must be surfaced to the user in a manual review table. The tool should store user overrides in a local SQLite database, building a custom dictionary to inform and train future automated resolutions.

## **5\. Chronology, Dating, and Geochronology Standardisation**

The standardisation of absolute and relative dating mechanisms is arguably the most complex aspect of wrangling legacy paleoscience data.

### **Radiocarbon Conventions**

Legacy datasets exhibit extreme heterogeneity in age reporting. The standard representation of radiocarbon ($^{14}$C) dates across databases like Neotoma and IsoArcH requires precise decomposition into specific fields:

1. **Conventional Age**: Uncalibrated $^{14}$C years BP (where the anchor "Present" is formally defined as 1950 CE).64  
2. **Uncertainty**: Analytical measurement error reported as ![][image4].64  
3. **Lab Code**: A unique alphanumeric identifier for the laboratory and measurement run.  
4. **Contextual Metadata**: The specific material dated (e.g., bone collagen, charcoal, shell), the pretreatment method utilized (e.g., ultrafiltration, acid-base-acid), and the isotopic fractionation correction ($\\delta^{13}$C).

### **Calibration Infrastructure**

Converting uncalibrated BP to calendar ages (cal BP or cal BCE/CE) utilizes specific, updated calibration curves (IntCal20 for Northern Hemisphere terrestrial samples, Marine20 for marine samples, SHCal20 for Southern Hemisphere).64 Radiocarbon calibration is not a linear multiplier; it generates a multimodal probability density function.64 Reporting calibrated ages requires stating the 1$\\sigma$ (68.2%) and 2$\\sigma$ (95.4%) highest posterior density (HPD) ranges, or the median absolute age.64  
To implement calibration offline within a Python desktop application, the tool should avoid relying solely on external web services which fail in remote fieldwork settings. Options include:

* **Subprocess execution of OxCal**: Requires local installation of the OxCal software suite on the user's machine, interacting via command-line interfaces or R wrappers.65  
* **oxcAAR or Bchron via R integration**: Utilizing Python libraries like rpy2 to interact with robust R packages such as Bchron or oxcAAR, which handle bulk calibration effectively.65  
* **Native Python Ports**: Utilizing Python libraries or porting the basic numerical integration of the IntCal20 dataset to generate probability density functions directly in memory.

### **Stratigraphic and Alternative Geochronology**

Repositories like Neotoma accommodate non-radiocarbon geochronology (e.g., OSL/TL, U-series, K-Ar, Ar-Ar, Amino Acid Racemisation) via specific relational tables (GeochronTypes).7 These require method-specific metadata, such as analytical precision, half-life values used, and dose rates. Furthermore, relative stratigraphic age assignments (e.g., North American Land Mammal Ages \[NALMA\], Marine Isotope Stages) are stored using controlled vocabulary lists mapped against boundary ages within the repository schema.

## **6\. Coordinate Reference Systems and Spatial Data**

A substantial portion of legacy dataset rejection occurs due to malformed or ambiguous spatial data. The tool must parse heterogeneous inputs: Decimal Degrees WGS84, Degrees Minutes Seconds (DMS), Universal Transverse Mercator (UTM), and historical localized grid systems (e.g., OSGB36).

### **pyproj Implementation and Architectural Hazards**

The pyproj library is the industry standard for robust Coordinate Reference System (CRS) detection and mathematical transformation in Python.70 However, a major architectural failure mode in Python spatial processing is the silent axis order inversion (switching latitude/longitude vs. longitude/latitude, or northing/easting).  
To avert this catastrophic geographic error, the Transformer class must be invoked strictly defining always\_xy=True:

Python  
from pyproj import Transformer  
\# EPSG:4326 is the WGS84 datum; target could be EPSG:3857 (Web Mercator)  
transformer \= Transformer.from\_crs("EPSG:4326", "EPSG:3857", always\_xy=True)  
lon, lat \= 5.0689, 52.0675  
x, y \= transformer.transform(lon, lat)

Without the always\_xy=True parameter, pyproj defaults to the axis order formally mandated by the EPSG registry definition. This order can arbitrarily flip between ![][image5] and ![][image6] depending on the specific CRS code, leading to coordinates mathematically plotting in the wrong hemisphere or deep within ocean basins.72

### **Spatial Validation and Gazetteer Enrichment**

Spatial validation queries must execute point-in-polygon geometry checks (e.g., utilizing shapely or geopandas within the tool) to validate that terrestrial site coordinates do not inadvertently intersect marine shapefiles. Imprecise localities (e.g., a legacy site described only as "nearest town") should be mapped with explicit radius uncertainties or coordinate bounding boxes, which are metadata fields natively supported by Neotoma's site tables. Integration with gazetteer services like GeoNames or the Getty Thesaurus of Geographic Names can automatically enrich text-based site localities with verifiable coordinates.

## **7\. Isotopic Data Quality Standards and Validation Rules**

Ensuring the scientific integrity of paleodietary and paleoecological isotopic data requires embedding complex geochemical validation thresholds directly into the tool's core validation engine.

### **Bone Collagen Quality Indicators**

Bone collagen is highly susceptible to diagenesis (post-mortem chemical alteration) and humic acid contamination from the burial environment.76 The standardisation application must enforce the following geochemical thresholds:

1. **C:N Atomic Ratio**: The universally accepted range for pristine, undegraded collagen is 2.9 to 3.6.77 Ratios exceeding 3.6 strongly suggest humic acid contamination (which adds exogenous carbon); ratios below 2.9 indicate severe degradation or exogenous nitrogen input.77  
2. **Collagen Yield**: The weight percent of extracted collagen relative to the whole bone must generally exceed 1% to be deemed reliable.21  
3. **%C and %N Ranges**: Total carbon and nitrogen weight percentages drop abruptly when collagen is poorly preserved; specific thresholds depend on the analytical matrix but generally require %C \> 30% and %N \> 11% for intact mammalian collagen.78

If a dataset row violates these metrics, the validation engine should tag it with a "Warning" or "Blocking Error," depending on the strictness of the target repository.

### **Carbonate Diagenesis Screening**

For enamel bioapatite or dentine carbonate $\\delta^{13}$C and $\\delta^{18}$O values, C:N ratios are geochemically irrelevant. Validation requires reporting distinct metadata on FTIR (Fourier Transform Infrared) splitting factors to assess mineral crystallinity, alongside XRD (X-ray diffraction) indices or trace element ratios (e.g., Mn/Fe).81 IsoArcH and IsoMemo guidelines emphasize that these metadata fields are critical for assessing whether a $\\delta^{18}$O signal accurately reflects biogenic drinking water or has been overwritten by groundwater diagenesis.82  
Furthermore, laboratories must report their inter-laboratory standards and ![][image4] measurement uncertainty, ensuring that instrumental drift over analytical sessions does not masquerade as biological variation.27

## **8\. Column Name Matching and Schema Mapping — ML/NLP Approaches**

Mapping a legacy spreadsheet containing hundreds of idiosyncratic column names (e.g., Radiocarbon Age, Uncal 14C BP, Date\_BP\_Uncalibrated) to a target repository schema (e.g., Neotoma's Geochronology table) requires robust, automated schema matching.7 Manual mapping places an unacceptable cognitive load on the researcher.

### **State-of-the-Art Approaches**

Classical data integration approaches rely on simple string similarity (Jaro-Winkler, Levenshtein distances) or token overlap. Modern open-source Python libraries like **Valentine** execute a comprehensive suite of schema matching algorithms (including Cupid, Similarity Flooding, and Coma) against Pandas DataFrames.84  
However, for domain-specific scientific text, transformer-based neural embedding similarity yields vastly superior recall. By utilizing Hugging Face's sentence-transformers:

* **all-MiniLM-L6-v2**: Generates 384-dimensional dense vectors. It is highly performant, features extremely low latency, and effectively maps semantic proximity. At only \~80MB, it is highly suitable for client-side offline execution within a bundled desktop app.88  
* **SciBERT**: Generates 768-dimensional vectors. Pre-trained on vast scientific corpora, it performs exceptionally well with domain terminology (e.g., recognizing that "$\\delta^{13}$C\_VPDB" and "13C/12C Ratio" map to the exact same conceptual axis), though it incurs a higher latency penalty.89

### **Hierarchical Fallback Pipeline**

The optimal implementation for the schema matching engine operates as a sequential waterfall pipeline:

1. **Exact Normalised Match**: Strip all whitespace, convert to lowercase, and remove special characters.  
2. **User Preference Dictionary**: Query a local SQLite cache mapping previously resolved manual overrides. If a user previously mapped C/N\_ratio to atomic\_c\_n, apply this instantly.  
3. **Embedding Semantic Similarity**: Compute the cosine distance between the source column embedding and the target repository schema embeddings.89 If the similarity score exceeds a strict threshold (e.g., \> 0.85), suggest the match.  
4. **Value Distribution Profiling**: Analyze the underlying row values. For example, if a column contains numeric floating-point values clustered between ![][image7] and ![][image8] with a precision of 1 decimal place, it overwhelmingly probabilistically points to $\\delta^{13}$C. If values are positive integers clustering between 1,000 and 50,000, it strongly indicates an uncalibrated $^{14}$C BP age.

## **9\. Validation Engine Design**

To intercept submission failures before uploading data to public repositories, the standardisation tool requires a highly deterministic validation engine.

### **Python Validation Libraries**

Evaluating Python libraries for scientific tabular data validation reveals distinct architectural trade-offs 91:

* **Pydantic**: Excellent for JSON payloads and API boundaries, but computationally heavy and syntactically clumsy when applied row-by-row to million-row Pandas DataFrames.93  
* **Great Expectations (GE)**: A heavyweight framework designed for big data distributed pipelines (Spark, SQL). While capable of generating excellent "Data Docs" (human-readable HTML validation reports), the overhead of maintaining Expectation Suites is excessive for a localized desktop application.91  
* **Pandera**: The optimal choice for this tech stack. Pandera provides a lightweight, DataFrame-native schema validation API.91 It integrates natively with Pandas, allowing for inline unit-test style checks, fast vectorized execution, and the seamless integration of domain-specific paleoscientific logic.92

### **Validation Rule Categories and UX Patterns**

A comprehensive Pandera schema for IsoMap should evaluate multiple vectors of data integrity:

* *Schema Completeness*: Checking for missing mandatory fields (e.g., checking that Investigator Name is not null).83  
* *Data Type Correctness*: Ensuring numeric isotope values are cast as floats, rather than strings containing arbitrary characters like \< or \~.  
* *Cross-field Logical Consistency*: Implementing conditional logic (e.g., If "Material" \= "Bone Collagen", then "C:N Ratio" MUST NOT be Null, and MUST fall between 2.9 and 3.6).  
* *Scientific Value Ranges*: Bounding $\\delta^{15}$N biologically between biologically plausible limits (e.g., ![][image9] and ![][image10]).

**UX Pattern**: Surfacing thousands of individual row-level errors simultaneously overwhelms users. The tool should aggregate errors by type and column, providing a dashboard summary (e.g., "Column *C:N Ratio* contains 45 values outside the acceptable 2.9–3.6 range"). Users can then click through to a filtered DataFrame view of the offending rows. Severity levels must be implemented: a "Blocking Error" prevents repository submission, whereas a "Warning" allows submission but flags the data for curator review.

## **10\. Transformation Audit Log and Reproducibility**

Modern scientific reproducibility mandates that every programmatic step—from legacy data ingestion to the final generated submission format—is meticulously documented. The system must generate a transformation audit log.

### **Provenance Metadata Standards**

The dominant standard for tracking computational workflows in scientific data pipelines is **PROV-O** (the W3C Provenance Ontology).94 This is frequently packaged within an **RO-Crate** (Research Object Crate).96 An RO-Crate utilizes the JSON-LD format to encapsulate the final datasets alongside a machine-readable, semantically rich description of the actors, execution environments, and exact computational steps applied.95  
The architecture should automatically construct a JSON-based log that details:

* **Input**: Source file hash (SHA-256) and timestamp.  
* **Mapping**: A complete dictionary mapping legacy source columns to standard repository columns.  
* **Transformations**: Explicitly capturing mathematical normalisations (e.g., "Multiplied column X by 1000 to convert from ![][image11] to ![][image12]").  
* **Resolutions**: The output of the taxonomy engine (e.g., "Reassigned generic term 'Elephas primigenius' to accepted valid taxon 'Mammuthus primigenius' via GBIF UUID X").

This structured JSON log can be utilized to dynamically populate a prose snippet for methodology sections in formal data papers (e.g., for journals like *Earth System Science Data* or *Journal of Open Archaeology Data*). This fulfills stringent journal requirements for data transformation transparency, allowing peer reviewers to understand exactly how legacy data was massaged into a modern format.26

## **11\. Offline Capability and Deployment**

Paleontologists and archaeologists frequently operate in remote field locations, mobile laboratories, or regions with highly restricted network connectivity. This operational reality necessitates a robust offline deployment strategy for the standardisation tool.

### **Desktop Architecture and Bundling Authority Data**

The specified tech stack—utilizing Tauri paired with a React frontend and a Python sidecar, or a monolithic PySide6 application—must be bundled into standalone executables capable of cross-platform execution on Windows, macOS, and Linux. Tools like PyInstaller, cx\_Freeze, or PyOxidizer are optimal for freezing the Python runtime alongside the Pandas/Pandera validation engine and ML models.  
Full offline capability requires bundling vast taxonomic backbones natively. A raw download of the GBIF backbone or the complete ITIS database can easily exceed several gigabytes of raw text.48

* **Storage Approach**: The optimal engineering approach involves pre-processing these CSV/SQL dumps into a highly compressed, indexed **SQLite** or **DuckDB** file bundled directly within the application binaries. DuckDB is particularly well-suited for extremely fast analytical queries across millions of taxonomic rows natively within Pandas.  
* **Model Weights**: The all-MiniLM-L6-v2 embedding model requires approximately 80 MB of disk space 88, which is trivial to bundle into modern binary installers.  
* **Schema Registries**: The Neotoma and IsoArcH target schemas should be cached as local JSON validation files. To prevent the tool from becoming obsolete as repositories update their submission requirements, the application should poll a GitHub-hosted schema registry upon launch (when internet connectivity is detected) to dynamically pull JSON updates without requiring a full software recompilation.

## **12\. Emerging Features and Recommendations**

Beyond the core wrangling, mapping, and validation pipeline, several peripheral functionalities significantly enhance the tool's utility within the paleoscience ecosystem.

* **DOI Minting & Deduplication**: Repositories like PANGAEA and IsoArcH assign Digital Object Identifiers (DOIs) upon formal publication.14 If a user submits a multiproxy dataset to both Neotoma (for the pollen counts) and IsoArcH (for the stable isotopes), maintaining cross-referenced DOIs via metadata links is essential to prevent academic deduplication conflicts and ensure unified dataset discovery.  
* **Unit Normalisation**: Legacy data is notoriously inconsistent with units (e.g., parts per million \[ppm\] vs. ![][image13]g/g vs. weight percent \[wt%\]). Integrating a Python library like Pint allows for declarative, robust unit conversion prior to mapping to the strict target schema (such as Neotoma's VariableUnits table).  
* **ORCID Integration**: Embedding researcher ORCID identifiers directly into the metadata output maps perfectly to the submission requirements for modern repositories like PANGAEA and IsoBank, ensuring flawless downstream academic attribution and automated profile updates.  
* **Imputation of Uncertainty**: Where legacy datasets omit standard deviations (missing ![][image4]), repositories strictly mandate them.27 While mathematically imputing a missing analytical error is geochemically invalid, the tool can programmatically flag these missing fields and prompt the researcher to assign an estimated conservative equipment error bounds based on modern laboratory standards, documenting this assumption explicitly in the PROV-O audit log to maintain transparency.  
* **Image and Spectral Linkage**: Many modern isotopic submissions include supplementary evidence like SEM images, FTIR spectra, or XRD patterns. While databases like IsoArcH primarily handle tabular data, the tool should facilitate packing these auxiliary files into the RO-Crate payload, linking the image filenames explicitly to the corresponding tabular row IDs for unified repository ingestion.  
* **Collaborative Workflows**: Supporting shared project folders or cloud synchronisation (e.g., via a shared transformation log on GitHub or the Open Science Framework) allows multi-researcher teams to collaboratively map complex multi-site datasets without duplicating schema mapping efforts.

#### **Works cited**

1. neotoma Documentation, accessed May 29, 2026, [https://neotoma-manual.readthedocs.io/\_/downloads/en/latest/pdf/](https://neotoma-manual.readthedocs.io/_/downloads/en/latest/pdf/)  
2. Journal of Vertebrate Paleontology From card catalogs to computers \- Integrative Biology | \- University of California, Berkeley, accessed May 29, 2026, [https://ib.berkeley.edu/labs/barnosky/Uhen%20et%20al%20databases.pdf](https://ib.berkeley.edu/labs/barnosky/Uhen%20et%20al%20databases.pdf)  
3. NeotomaDB/DataBUS\_210Pb: The Neotoma Paleoecology ... \- GitHub, accessed May 29, 2026, [https://github.com/NeotomaDB/DataBUS\_210Pb](https://github.com/NeotomaDB/DataBUS_210Pb)  
4. Neotoma API 2.0-oas3, accessed May 29, 2026, [https://www.neotomadb.org/apps/api](https://www.neotomadb.org/apps/api)  
5. (PDF) neotoma: A Programmatic Interface to the Neotoma Paleoecological Database, accessed May 29, 2026, [https://www.researchgate.net/publication/273318179\_neotoma\_A\_Programmatic\_Interface\_to\_the\_Neotoma\_Paleoecological\_Database](https://www.researchgate.net/publication/273318179_neotoma_A_Programmatic_Interface_to_the_Neotoma_Paleoecological_Database)  
6. Full article: User-centered design and evaluation of the neotoma paleoecology open software ecosystem \- Taylor & Francis, accessed May 29, 2026, [https://www.tandfonline.com/doi/full/10.1080/17538947.2024.2378822](https://www.tandfonline.com/doi/full/10.1080/17538947.2024.2378822)  
7. Neotoma Tables — neotoma 1.0 documentation, accessed May 29, 2026, [https://neotoma-manual.readthedocs.io/en/latest/neotoma\_tables.html](https://neotoma-manual.readthedocs.io/en/latest/neotoma_tables.html)  
8. 7 Database Design Concepts | Neotoma Paleoecology Manual v2.0, accessed May 29, 2026, [https://open.neotomadb.org/manual/database-design-concepts.html](https://open.neotomadb.org/manual/database-design-concepts.html)  
9. Resources \- NeotomaDB, accessed May 29, 2026, [https://www.neotomadb.org/resources](https://www.neotomadb.org/resources)  
10. get\_datasets in neotoma2: Working with the Neotoma Paleoecology Database \- rdrr.io, accessed May 29, 2026, [https://rdrr.io/cran/neotoma2/man/get\_datasets.html](https://rdrr.io/cran/neotoma2/man/get_datasets.html)  
11. neotoma2: Working with the Neotoma Paleoecology Database \- CRAN, accessed May 29, 2026, [https://cran.r-project.org/web/packages/neotoma2/neotoma2.pdf](https://cran.r-project.org/web/packages/neotoma2/neotoma2.pdf)  
12. Updated chronologies for North American small mammal fossil localities in the Neotoma Paleoecology Database \- PMC, accessed May 29, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12873247/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12873247/)  
13. (PDF) Updated chronologies for North American small mammal fossil localities in the Neotoma Paleoecology Database \- ResearchGate, accessed May 29, 2026, [https://www.researchgate.net/publication/400456431\_Updated\_chronologies\_for\_North\_American\_small\_mammal\_fossil\_localities\_in\_the\_Neotoma\_Paleoecology\_Database](https://www.researchgate.net/publication/400456431_Updated_chronologies_for_North_American_small_mammal_fossil_localities_in_the_Neotoma_Paleoecology_Database)  
14. IsoArcH | The world's largest isotope database, accessed May 29, 2026, [https://isoarch.org/](https://isoarch.org/)  
15. IsoMemo – A Big isotopic Data initiative, accessed May 29, 2026, [https://isomemo.gea.mpg.de/](https://isomemo.gea.mpg.de/)  
16. The IsoArcH initiative: Working towards an open and collaborative isotope data culture in bioarchaeology \- PMC, accessed May 29, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9516382/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9516382/)  
17. Submit your dataset | IsoArcH, accessed May 29, 2026, [https://isoarch.org/submit](https://isoarch.org/submit)  
18. Frequently asked questions \- IsoArcH, accessed May 29, 2026, [https://isoarch.org/faq](https://isoarch.org/faq)  
19. IsoMedIta: A Stable Isotope Database for Medieval Italy in \- Brill, accessed May 29, 2026, [https://brill.com/view/journals/rdj/8/1/article-p1\_004.xml](https://brill.com/view/journals/rdj/8/1/article-p1_004.xml)  
20. Introducing Isotòpia: A stable isotope database for Classical Antiquity \- PMC \- NIH, accessed May 29, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11146721/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11146721/)  
21. An isotopic study of dietary diversity in formative period Ancachi/Quillagua, Atacama Desert, northern Chile \- Anthropology, accessed May 29, 2026, [https://anthropology.as.miami.edu/\_assets/pdf/pinder-et-al-2019.pdf](https://anthropology.as.miami.edu/_assets/pdf/pinder-et-al-2019.pdf)  
22. The Caribbean and Mesoamerica Biogeochemical Isotope Overview (CAMBIO) \- PMC \- NIH, accessed May 29, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11001905/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11001905/)  
23. Creating stable isotopic database of faunal remains ‒ Bronze Age Italy \- CEJSH, accessed May 29, 2026, [http://cejsh.icm.edu.pl/cejsh/element/bwmeta1.element.ojs-doi-10\_14746\_fpp\_2024\_29\_03/c/articles-60821224.pdf.pdf](http://cejsh.icm.edu.pl/cejsh/element/bwmeta1.element.ojs-doi-10_14746_fpp_2024_29_03/c/articles-60821224.pdf.pdf)  
24. Data Templates | U.S. Geological Survey \- USGS.gov, accessed May 29, 2026, [https://www.usgs.gov/data-management/data-templates](https://www.usgs.gov/data-management/data-templates)  
25. The Mediterranean archive of isotopic data, a dataset to explore lifeways from the Neolithic to the Iron Age \- MPG.PuRe, accessed May 29, 2026, [https://pure.mpg.de/rest/items/item\_3560898\_2/component/file\_3560907/content](https://pure.mpg.de/rest/items/item_3560898_2/component/file_3560907/content)  
26. Presenting the AfriArch Isotopic Database \- MPG.PuRe, accessed May 29, 2026, [https://pure.mpg.de/rest/items/item\_3511492/component/file\_3511493/content](https://pure.mpg.de/rest/items/item_3511492/component/file_3511493/content)  
27. Best practices for selecting samples, analyzing data, and publishing results in isotope archaeology, accessed May 29, 2026, [https://research-repository.griffith.edu.au/bitstreams/c96fd60a-838e-410f-9eb7-0eb8bdd44c61/download](https://research-repository.griffith.edu.au/bitstreams/c96fd60a-838e-410f-9eb7-0eb8bdd44c61/download)  
28. Advanced Isotopic Techniques to Investigate Cultural Heritage: The Research Activities at the iCONa Laboratory \- MDPI, accessed May 29, 2026, [https://www.mdpi.com/2571-9408/8/8/296](https://www.mdpi.com/2571-9408/8/8/296)  
29. Introducing Isomad, a Compilation of Isotopic Datasets for Madagascar \- PDXScholar, accessed May 29, 2026, [https://pdxscholar.library.pdx.edu/cgi/viewcontent.cgi?article=1291\&context=anth\_fac](https://pdxscholar.library.pdx.edu/cgi/viewcontent.cgi?article=1291&context=anth_fac)  
30. Introducing IsoMad, a compilation of isotopic datasets for Madagascar \- PMC, accessed May 29, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC11316086/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11316086/)  
31. Human Lifeways in Late Roman and Medieval Europe. A Multi-Scale and Multi-Proxy Stable Isotope Approach, accessed May 29, 2026, [https://edoc.ub.uni-muenchen.de/31683/1/Cocozza\_Carlo.pdf](https://edoc.ub.uni-muenchen.de/31683/1/Cocozza_Carlo.pdf)  
32. When big data initiatives meet: Data sharing between THANADOS and IsoArcH for early medieval cemeteries in Austria \- PMC, accessed May 29, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10293964/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10293964/)  
33. How to publish FAIR Data with PANGAEA. \- Data Publisher for Earth & Environmental Science \- YouTube, accessed May 29, 2026, [https://www.youtube.com/watch?v=5bJfSuAukTQ](https://www.youtube.com/watch?v=5bJfSuAukTQ)  
34. Paleo Data Search | Home | National Centers for Environmental Information (NCEI) \- NOAA, accessed May 29, 2026, [https://www.ncei.noaa.gov/access/paleo-search/](https://www.ncei.noaa.gov/access/paleo-search/)  
35. Authors Guides \- PANGAEA Wiki, accessed May 29, 2026, [https://wiki.pangaea.de/wiki/Authors\_Guides](https://wiki.pangaea.de/wiki/Authors_Guides)  
36. Format \- PANGAEA Wiki, accessed May 29, 2026, [https://wiki.pangaea.de/wiki/Format](https://wiki.pangaea.de/wiki/Format)  
37. PANGAEA \- Data Publisher for Earth & Environmental Science \- PMC \- NIH, accessed May 29, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10238520/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10238520/)  
38. Speleothem | National Centers for Environmental Information (NCEI) \- NOAA, accessed May 29, 2026, [https://www.ncei.noaa.gov/products/paleoclimatology/speleothem](https://www.ncei.noaa.gov/products/paleoclimatology/speleothem)  
39. Paleoclimatology | National Centers for Environmental Information (NCEI) \- NOAA, accessed May 29, 2026, [https://www.ncei.noaa.gov/products/paleoclimatology](https://www.ncei.noaa.gov/products/paleoclimatology)  
40. Coral and Sclerosponge | National Centers for Environmental Information (NCEI) \- NOAA, accessed May 29, 2026, [https://www.ncei.noaa.gov/products/paleoclimatology/coral-sclerosponge](https://www.ncei.noaa.gov/products/paleoclimatology/coral-sclerosponge)  
41. Paleo Data Search | API Documentation | National Centers for Environmental Information (NCEI) \- NOAA, accessed May 29, 2026, [https://www.ncei.noaa.gov/access/paleo-search/api](https://www.ncei.noaa.gov/access/paleo-search/api)  
42. Climate Data Store, accessed May 29, 2026, [https://cds.climate.copernicus.eu/](https://cds.climate.copernicus.eu/)  
43. ECMWF Reanalysis v5 (ERA5) \- Drought.gov, accessed May 29, 2026, [https://www.drought.gov/data-maps-tools/ecmwf-reanalysis-v5-era5](https://www.drought.gov/data-maps-tools/ecmwf-reanalysis-v5-era5)  
44. Interoperability between the StraboSpot graph database and GIS software– A Malpais Mesa Use Case \- KU ScholarWorks, accessed May 29, 2026, [https://kuscholarworks.ku.edu/bitstreams/4c19611c-d945-4ae7-9546-f5b7c3a31fc8/download](https://kuscholarworks.ku.edu/bitstreams/4c19611c-d945-4ae7-9546-f5b7c3a31fc8/download)  
45. A NEW GEOLOGIC DATA COLLECTION SYSTEM \- STRABOSPOT, accessed May 29, 2026, [https://strabospot.wordpress.com/wp-content/uploads/2018/08/mn\_poster\_v3.pdf](https://strabospot.wordpress.com/wp-content/uploads/2018/08/mn_poster_v3.pdf)  
46. The Digital Archaeological Record (tDAR) \- Core Trust Seal, accessed May 29, 2026, [https://www.coretrustseal.org/wp-content/uploads/2022/12/20221216-tDAR\_final.pdf](https://www.coretrustseal.org/wp-content/uploads/2022/12/20221216-tDAR_final.pdf)  
47. using tdar to manage legacy and new archaeological documents and data, the phoenix area office of, accessed May 29, 2026, [https://shesc.asu.edu/sites/g/files/litvpz441/files/2023-05/Using-tDAR-to-Manage-Legacy-and-New-Archaeological-Documents-and-Data-the-Phoenix-Area-Office-of-the-Bureau-of-Reclamation-.pdf](https://shesc.asu.edu/sites/g/files/litvpz441/files/2023-05/Using-tDAR-to-Manage-Legacy-and-New-Archaeological-Documents-and-Data-the-Phoenix-Area-Office-of-the-Bureau-of-Reclamation-.pdf)  
48. Integrated Taxonomic Information System (ITIS): ITIS.gov, accessed May 29, 2026, [https://itis.gov/](https://itis.gov/)  
49. (Almost) everything you want to know about the GBIF Species API, accessed May 29, 2026, [https://data-blog.gbif.org/post/gbif-species-api/](https://data-blog.gbif.org/post/gbif-species-api/)  
50. GBIF API beginners guide, accessed May 29, 2026, [https://data-blog.gbif.org/post/gbif-api-beginners-guide/](https://data-blog.gbif.org/post/gbif-api-beginners-guide/)  
51. gbif-api | Skills Marketplace · LobeHub, accessed May 29, 2026, [https://lobehub.com/de/skills/wentorai-research-plugins-gbif-api](https://lobehub.com/de/skills/wentorai-research-plugins-gbif-api)  
52. GBIF API Reference \- Technical Documentation, accessed May 29, 2026, [https://techdocs.gbif.org/en/openapi/](https://techdocs.gbif.org/en/openapi/)  
53. Web Service Description \- ITIS, accessed May 29, 2026, [https://www.itis.gov/ws\_description.html](https://www.itis.gov/ws_description.html)  
54. Integrated Taxonomic Information System \- Hierarchy APIs, accessed May 29, 2026, [https://itis.gov/ws\_hierApiDescription.html](https://itis.gov/ws_hierApiDescription.html)  
55. TSN Search APIs \- Integrated Taxonomic Information System (ITIS), accessed May 29, 2026, [https://itis.gov/ws\_tsnApiDescription.html](https://itis.gov/ws_tsnApiDescription.html)  
56. Solr Web Services Examples \- Integrated Taxonomic Information System (ITIS), accessed May 29, 2026, [https://www.itis.gov/solr\_examples.html](https://www.itis.gov/solr_examples.html)  
57. WoRMS rest API \- WoRMS \- World Register of Marine Species, accessed May 29, 2026, [https://www.marinespecies.org/rest/](https://www.marinespecies.org/rest/)  
58. Webservices \- WoRMS \- World Register of Marine Species, accessed May 29, 2026, [https://www.marinespecies.org/aphia.php?p=webservice](https://www.marinespecies.org/aphia.php?p=webservice)  
59. TaxonMatch: taxonomic integration and tree construction from heterogeneous biological databases \- bioRxiv, accessed May 29, 2026, [https://www.biorxiv.org/content/10.64898/2026.03.18.712418v1.full.pdf](https://www.biorxiv.org/content/10.64898/2026.03.18.712418v1.full.pdf)  
60. Paleobiology Database User Guide Version 2.0 \- ResearchGate, accessed May 29, 2026, [https://www.researchgate.net/publication/404972077\_Paleobiology\_Database\_User\_Guide\_Version\_20](https://www.researchgate.net/publication/404972077_Paleobiology_Database_User_Guide_Version_20)  
61. Inaugural Digital Data in Biodiversity Research Conference Concurrent Sessions Abstracts 5-6 June 2017 Co-sponsored by the Unive \- iDigBio, accessed May 29, 2026, [https://www.idigbio.org/wiki/images/8/87/Concurrent\_Sessions.pdf](https://www.idigbio.org/wiki/images/8/87/Concurrent_Sessions.pdf)  
62. IOC Ocean Data and Information System Catalogue, accessed May 29, 2026, [https://catalogue.odis.org/search/type=8](https://catalogue.odis.org/search/type=8)  
63. R packages by rOpenSci \- R-universe, accessed May 29, 2026, [https://ropensci.r-universe.dev/packages](https://ropensci.r-universe.dev/packages)  
64. ORAU \- OxCal \- Radiocarbon calibration, accessed May 29, 2026, [https://c14.arch.ox.ac.uk/calibration.html](https://c14.arch.ox.ac.uk/calibration.html)  
65. Calibrate radiocarbon dates — c14\_calibrate \- stratigraphr \- Joe Roe, accessed May 29, 2026, [https://stratigraphr.joeroe.io/reference/c14\_calibrate.html](https://stratigraphr.joeroe.io/reference/c14_calibrate.html)  
66. Using Bayesian radiocarbon chronology package Bchron, accessed May 29, 2026, [https://andrewcparnell.github.io/Bchron/articles/Bchron.html](https://andrewcparnell.github.io/Bchron/articles/Bchron.html)  
67. oxcAAR: Interface to 'OxCal' Radiocarbon Calibration \- CRAN \- R Project, accessed May 29, 2026, [https://cran.r-project.org/web/packages/oxcAAR/oxcAAR.pdf](https://cran.r-project.org/web/packages/oxcAAR/oxcAAR.pdf)  
68. OxCal input, accessed May 29, 2026, [https://c14.arch.ox.ac.uk/oxcalhelp/hlp\_input.html](https://c14.arch.ox.ac.uk/oxcalhelp/hlp_input.html)  
69. oxcAAR: Interface to 'OxCal' Radiocarbon Calibration version 1.1.1 from CRAN \- rdrr.io, accessed May 29, 2026, [https://rdrr.io/cran/oxcAAR/](https://rdrr.io/cran/oxcAAR/)  
70. Gotchas/FAQ \- pyproj 3.7.2 documentation \- GitHub Pages, accessed May 29, 2026, [https://pyproj4.github.io/pyproj/stable/gotchas.html](https://pyproj4.github.io/pyproj/stable/gotchas.html)  
71. 6 Reprojecting geographic data \- Geocomputation with Python \- geocompx, accessed May 29, 2026, [https://py.geocompx.org/06-reproj](https://py.geocompx.org/06-reproj)  
72. Transformer \- pyproj 3.7.2 documentation \- GitHub Pages, accessed May 29, 2026, [https://pyproj4.github.io/pyproj/stable/api/transformer.html](https://pyproj4.github.io/pyproj/stable/api/transformer.html)  
73. Transformer — pyproj 3.1.0 documentation \- GitHub Pages, accessed May 29, 2026, [https://pyproj4.github.io/pyproj/3.1.0/api/transformer.html](https://pyproj4.github.io/pyproj/3.1.0/api/transformer.html)  
74. Advanced Examples \- pyproj 3.7.2 documentation \- GitHub Pages, accessed May 29, 2026, [https://pyproj4.github.io/pyproj/stable/advanced\_examples.html](https://pyproj4.github.io/pyproj/stable/advanced_examples.html)  
75. Adding EPSG codes to Pyproj \- Geographic Information Systems Stack Exchange, accessed May 29, 2026, [https://gis.stackexchange.com/questions/366769/adding-epsg-codes-to-pyproj](https://gis.stackexchange.com/questions/366769/adding-epsg-codes-to-pyproj)  
76. Bone Collagen Quality Indicators for Palaeodietary and Radiocarbon Measurements, accessed May 29, 2026, [https://os.pennds.org/archaeobib\_filestore/pdf\_articles/biogeochemistry/1999\_26\_6\_vanKlinken.pdf](https://os.pennds.org/archaeobib_filestore/pdf_articles/biogeochemistry/1999_26_6_vanKlinken.pdf)  
77. and 18O stable isotope analysis of human bone tissue to identify transhumance, high altitude habitation and rec, accessed May 29, 2026, [https://edoc.ub.uni-muenchen.de/7327/1/McGlynn\_George.pdf.pdf](https://edoc.ub.uni-muenchen.de/7327/1/McGlynn_George.pdf.pdf)  
78. “Here we go again”: the inspection of collagen extraction protocols for 14C dating and palaeodietary analysis \- PMC, accessed May 29, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8300532/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8300532/)  
79. Isotope Analysis for Diet Studies (Chapter 6\) \- Archaeological Science, accessed May 29, 2026, [https://www.cambridge.org/core/books/archaeological-science/isotope-analysis-for-diet-studies/16A8C8460DD9845D0DB4B15344FF712A](https://www.cambridge.org/core/books/archaeological-science/isotope-analysis-for-diet-studies/16A8C8460DD9845D0DB4B15344FF712A)  
80. Preparation and characterization of bone and tooth collagen for isotopic analysis, accessed May 29, 2026, [https://experts.illinois.edu/en/publications/preparation-and-characterization-of-bone-and-tooth-collagen-for-i](https://experts.illinois.edu/en/publications/preparation-and-characterization-of-bone-and-tooth-collagen-for-i)  
81. Stable Carbon and Oxygen Isotope Spacing Between Bone and Tooth Collagen and Hydroxyapatite in Human Archaeological Remains \- Smithsonian Research Online, accessed May 29, 2026, [https://repository.si.edu/server/api/core/bitstreams/ad8402ce-c63f-42b6-a5fe-c10ce2d99abe/content](https://repository.si.edu/server/api/core/bitstreams/ad8402ce-c63f-42b6-a5fe-c10ce2d99abe/content)  
82. Biochemical Analysis of Dietary and Migratory Patterns in the Veneto, Italy: From Late Antiquity to the Early Medieval Period \- Digital Commons @ USF \- University of South Florida, accessed May 29, 2026, [https://digitalcommons.usf.edu/context/etd/article/9051/viewcontent/Maxwell\_usf\_0206D\_15367.pdf](https://digitalcommons.usf.edu/context/etd/article/9051/viewcontent/Maxwell_usf_0206D_15367.pdf)  
83. Design, development, and implementation of IsoBank: A centralized repository for isotopic data \- UU Research Portal, accessed May 29, 2026, [https://research-portal.uu.nl/ws/files/240416119/journal.pone.0295662.pdf](https://research-portal.uu.nl/ws/files/240416119/journal.pone.0295662.pdf)  
84. Valentine \- GitHub Pages, accessed May 29, 2026, [https://delftdata.github.io/valentine/](https://delftdata.github.io/valentine/)  
85. GitHub \- delftdata/valentine: A tool facilitating matching columns across tabular datasets. It also serves as an experiment suite for state-of-the-art schema matching methods., accessed May 29, 2026, [https://github.com/delftdata/valentine](https://github.com/delftdata/valentine)  
86. valentine/README.md at master · delftdata/valentine \- GitHub, accessed May 29, 2026, [https://github.com/delftdata/valentine/blob/master/README.md](https://github.com/delftdata/valentine/blob/master/README.md)  
87. Schema Matching with Valentine (pyJedAI intregrated), accessed May 29, 2026, [https://pyjedai.readthedocs.io/en/latest/tutorials/SchemaMatching.html](https://pyjedai.readthedocs.io/en/latest/tutorials/SchemaMatching.html)  
88. Build a semantic search engine for tabular columns with Transformers and Amazon OpenSearch Service | AWS Big Data Blog, accessed May 29, 2026, [https://aws.amazon.com/blogs/big-data/build-a-semantic-search-engine-for-tabular-columns-with-transformers-and-amazon-opensearch-service/](https://aws.amazon.com/blogs/big-data/build-a-semantic-search-engine-for-tabular-columns-with-transformers-and-amazon-opensearch-service/)  
89. Embedding Essentials: Cosine Similarity in SQL \- e6data, accessed May 29, 2026, [https://www.e6data.com/blog/embedding-essentials-cosine-similarity-sql-with-vectors](https://www.e6data.com/blog/embedding-essentials-cosine-similarity-sql-with-vectors)  
90. Mapping embeddings to Elasticsearch field types: semantic\_text, dense\_vector, sparse\_vector, accessed May 29, 2026, [https://www.elastic.co/search-labs/blog/mapping-embeddings-to-elasticsearch-field-types](https://www.elastic.co/search-labs/blog/mapping-embeddings-to-elasticsearch-field-types)  
91. 8 Great Expectations vs Pandera: Which Fits Your Python Stack? | by Bhagya Rana, accessed May 29, 2026, [https://medium.com/@bhagyarana80/8-great-expectations-vs-pandera-which-fits-your-python-stack-a115c9241dcb](https://medium.com/@bhagyarana80/8-great-expectations-vs-pandera-which-fits-your-python-stack-a115c9241dcb)  
92. Data validation in Python: a look into Pandera and Great Expectations \- endjin, accessed May 29, 2026, [https://endjin.com/blog/a-look-into-pandera-and-great-expectations-for-data-validation](https://endjin.com/blog/a-look-into-pandera-and-great-expectations-for-data-validation)  
93. The data validation landscape in 2025 \- Arthur Turrell, accessed May 29, 2026, [https://aeturrell.com/blog/posts/the-data-validation-landscape-in-2025/](https://aeturrell.com/blog/posts/the-data-validation-landscape-in-2025/)  
94. FAIR data pipeline: provenance-driven data management for traceable scientific workflows \- PMC, accessed May 29, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9376726/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9376726/)  
95. Packaging research artefacts with RO-Crate, accessed May 29, 2026, [https://www.researchobject.org/2021-packaging-research-artefacts-with-ro-crate/manuscript.html](https://www.researchobject.org/2021-packaging-research-artefacts-with-ro-crate/manuscript.html)  
96. Recording provenance of workflow runs with RO-Crate | PLOS One \- Research journals, accessed May 29, 2026, [https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0309210](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0309210)  
97. Recording provenance of workflow runs with RO-Crate \- arXiv, accessed May 29, 2026, [https://arxiv.org/html/2312.07852v1](https://arxiv.org/html/2312.07852v1)  
98. Design and Application of Provenance within Distributed Workflow Management Systems | Semantic Web Journal, accessed May 29, 2026, [https://www.semantic-web-journal.net/system/files/swj4011.pdf](https://www.semantic-web-journal.net/system/files/swj4011.pdf)  
99. DOI & Citation Policy \- IsoArcH, accessed May 29, 2026, [https://isoarch.org/doi-and-citation-policy](https://isoarch.org/doi-and-citation-policy)  
100. repository\_info\_v3.csv \- Zenodo, accessed May 29, 2026, [https://zenodo.org/records/7643637/files/repository\_info\_v3.csv?download=1](https://zenodo.org/records/7643637/files/repository_info_v3.csv?download=1)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAZCAYAAADe1WXtAAAAcElEQVR4XmNgGAWjYFCAdiCWRBekFEwG4mR0QUqBFRBfQBekBpAF4lx0QWqAO0C8EYh10SVAIBWId5OB7wHxfyBeDcTMDFQCIEMt0QUpASDDsHqbXGALxFvQBSkFM4A4AF2QUgBK+PzogqNgFNAIAADWvRUcqAhrOQAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACIAAAAaCAYAAADSbo4CAAABk0lEQVR4Xu2UPyhGURjGX6QoKQwikyQlFAaSQZKJxGLwN2WxGZQyyCillGyIBWWhDPKnRIkik5RkMJDBYLPwvL1fOT3O7ftc9V3D96vfcJ9zuue957zniqT4H5zAGg6TTSm85zAKJuEMh0GkwyP4CZ/gMayClzDNmReGW1jNoY9ieAY7YS4sg+PwAe4588KihcRlUWwXWnkAlMMKDn+J7qb2SFyuxApp4gGxQv5KMwdBXIgVotdL+8Qli567xXqnDRbAVXgIG505zAIHQYyJFaK+wA04AfPdSaAQ3sAd+A6vYb3Yju4681wy4DOHidAHt+W7sE1nbFqsiT/go5OPwGzn2WUZDnHoQ2+Lj1mxQu54QCxf4dCDHqvucA4P+BjmIEal2ILaD4zmAxx66BHb3YQY5CCGLhS0oOZFHHrQXuvl0Iee7Tk8gF2wBNbCU7guP2+Qoi+e59BDv9g7EmINZsIpsc5/g1uwXYJ/6XqUDRx60JvVwWGyyYOvYh8ZKaNwicMo2IctHEbBHAdRUcdBihRh+QIfKEZd81XViQAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACcAAAAaCAYAAAA0R0VGAAABHElEQVR4XmNgGAUjECSjCxAAzEDMhC5IK1CLLoAH6ALxJiBmQZegFahDF0ADAkD8H4h/A/EZKJtujqtHF0ADIIeYAzEnEPMw0NlxjegCeMCo45ABtR0nD8S3GSDq0PFLJHUoYAIDpmJ8eBFEGwog5DgtIH4KxHOg+A0DRP0eBkipEI9QShwgJ+TY0CWAYBkQ/2KAOBAZgBwLwmQBchzHjiauABXfiyYOCuHPQHwUTZxoQI7jONDE06DiFWji7lDxiWjiRANyHAcq85BBNVTcFU18MRB/Y8CMaqIBKY4zYoA4IhiIuZDE+YD4BgMk4YPEk4D4NRBPYiCyHqYkt37AIg/Cz5HUSALxEiC+xABxpBOS3CgYBaNgFIyCwQgASxBWUhGTBHYAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAaCAYAAADMp76xAAABj0lEQVR4Xu2WTSsFURjHHy8hUkoRWYiUwoKFsvOy8gl8BJSk7CQreSllZeHlE1gpKzsLYi9FiVJKkkTZ8v935pgzj4lxZnSvml/96s7zn/vMaebcZ65ITk5OQemG7zHOB/mVqr/CyiD7Cd2TLkTOEJlxMnobjeMph11ivnANO52sAl7Ae9gBy5wsCdXwTEzvZpVZ1uAjbIclKvsWLoqN14PjSXgKaz7P8KNFTN8pVa+HB7BP1ROzJKbxC6wVc2caI2f4sw+PVO0YDqrar2iTcC9tw6ZonIoxMX15DcKtxf2bmj0JF50lVWJ6zgXHy07mzQC8lHAyZI29EbuwVGVecEJwEvDHwca90Tg1dsENOvBhFPYEnzkVnuBGGGcCF3uiiz6MiBlpLivwWczeywoueFEXk8K31Sx8gDsqI61iLsBtwnkZx6aEj3lIZZphMefV6SAJfPz2QtYtJ5+Oyd+c3NIPz8X8SMdVZrmTr72oHW8FgS+cCV0sZg4l+4nyZ3Bb3OhiscI/Nau6mJOT88/5AMWRYizCZ9ZeAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAaCAYAAADMp76xAAABdElEQVR4Xu2VPS8EURSGj68QBQVRCA09iVaxifgFGhokSlmJRqHTaURB+A8+EhGFoPSRUIiEWrGJRCH+gAjvyZnZe+e44s7uXVlyn+TJ7px39pyZu7t3iCKRyK8zDD8can7KfZinr33YAhxw1E/kY27uSU7i116VMWvwBS7AQZXloR2Ok8w6hN1Wxn25fgf7rLoTPiG9s6LKuuCIqlVLOmsiOd6D2yb244ikyYVV4xW5tI5DcU4y6yw53odNJvZjksydM9zgFC6WzwjHLJlZm7A5G/vRBl/JXPAqXDdxUFrhM8msW5XlokDSZBc2qiwkvGNcw3cyC1QRQyQNenQQmCuS/8cOyTxe8Yrg32tVd+zBCuxM3o+SzJsqpzk5oNpe8DJ8ULUbeKxqXoxRdpfwoZ+y25OLDrgF3+CMyhrIrDJvbS3Z+HvSC7Xlx6UPG/BRFxN4p9F9p62cHxg6f7LymlHShXqHv84/xZwu1DNLuhCJRP4JnyQuYdaNlaOyAAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAZCAYAAACRiGY9AAACLUlEQVR4Xu2WT0hUURSHT6KkKNKmNoaiCG6iDIQUERUFF2HoJty0cWFBtqiFVqig0kIiFYlciIFgrUKIbCEqjdg/iKg2EdSu0KCgRasUsd+Zc1+ee5qpWcwbFd4HH8z93TPv3fvuzH2XKCJi31ME1+Bn+Bie8LvjHLIBGLRBEo7ACfgdLsMqvzv91JJM6Ay8CbfgL69CeAavwzZ4kWRw17yKxByF7+ECyeRG4QZs1UXp5AB8DftU1gm34WGVMW9cHrjpdydlEf4gf6X5AX1R7bRyhWSAD0zOA3lislemnQrdJNcfN3mHy0PhBu08eQ3/r2Ime2naqTBJcu0hk7e4PBQq4U94z+T8H5sy2Qt4l+Rn8xH2+N0JmScZ/FWTN7g8YzST3LDa5M9Jnng5PA5XYalX8Tdcw9fqNXm9yzPCaZKbPbId4KRp55HU2lwTI6mxu2Sdy3mjCpVi+BWuwFzTlwweWJcNFXOUeFIprxTvWKla5r6jeQufwgLb8Q94YMM2VEyT1AyYvMnloZJF8nLMVxm/rwLOwk+qHcADu2RDRfDKuGXydpeHygjMMdl99TlGiQfBWaMNFcdIamZMfsHlocBnMD4S8Q2s51Qdb/3vVLuQ5OhTozIm+K5eZd4U+PTBq8NUwG9w7E9FmuGfhZ1M4ClVx1yGD+EduA4/+N1xlkhWlc94mvMk17xNcmSahQe9il2EnzZPjlco2/T9jxLYT3IgDn0rj4iIiIjYE/wG4VeHGUgV6UsAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADUAAAAZCAYAAACRiGY9AAAB5UlEQVR4Xu2XyytFURSHFxMZMZAM1JXCREmZChkYKQyQZ5l4ZKSEAQMZeiVhYiAm5DGREkrJP6CYmMnAK4aKxG+199G6q32uO7g70vnqS+e31mGvc+/ddyOKiPg3NMCYDgWb8A7ewHVVS0QuXIBP8ARWxJf9MQU/YKsuWGrgNMyDZfAIFsiGEPLhFTwkM9wsfIP1sinVnMFPeG9/uobKgg8qy4E7KnPBw7/AbJGdw1tx7Y0DMkO16QKZtx3XNJy16FAwSKZnXuX84Fy/L+UkGuqS3IvgbFKHgmVy99TZ3DthQ6XBV1vTcLakQ8E+mZ5RlVfb3DthQ2Xa3LUIzrZ1KAg+ryMqr7K5d4Kh2lWebnPXIjjjLTqMUzI9YyqvtDm/C7wSDNWhC2R2r7ChtnQo2CX3UEm/Urx1JmuhvUcSDNWpC+Ca3IvgbEWHglUyPRMqr7W5d4KhunQB7JF7EZzxth3GEJmeGZU32tw7wVDdugAGyL0Izop1KCgl07Om8j6be+eCzB/i7xY+CmmGYZG4boZN4prh+9kekfGm8E7m1WFK4COc++7wQHBa0LrOZs9wkczxyPWkj8nseHzGk/SS6ed7edPZgBlxHb8IH2T74TgsV7WfiJG5j/8T8L6VR0RERET8Cb4AZUKHUNWkyqcAAAAASUVORK5CYII=>

[image9]: <data:image/png;base64,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>

[image10]: <data:image/png;base64,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>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD0AAAAaCAYAAAAEy1RnAAAC+ElEQVR4Xu2XWahOURTHl5kyP+BB+dwHIYoSRTIVD6YyRApleKDEAxLKkAxFxswyxQsPSkTKDS+GInmQ8UFCyJBcReL/b+3tW9865yTce/N9nV/969v/vfY5d6+z99r7iuTk1CdNoWferHTGQ6e8WemchKZ6s5JpCb2Dmjt/PvQN+gGNdn1lzwzouDdBG9EJU51cX1nTAXoDNfEdAU54nTfLnQXQPm8aOOnB3qwtukP3oc1QQ6g3dB26BW0T3W+rgnc1KIuu0A7oLrQWmgvdK4kocg0a7s1AM+g11Ci0e0EXoRNQixhkGAadgW5Ak6ADpd1JOAlmnZk9LDpZTn5g8HZBe6AuIZ7HCxPjmQa9h5ZDDaBzouOf2CDDc9G4NEZIca8zMedFE8/nj4xBouP5sT6ENmvBS9H3ZsKjYgJ0QTSQXz0yKHinjUc4mX7O49dk7ADjLQ3ebONZ+nrDcBvaCa2RYmIWQVN+RehH+CRa/bkyImflN5OOfIGeOm+16OB5xuNSr5HkF2LcA+fFL11wPunjDUNn0XHfoa3QHEkvduxj3H7jNYY+SnIuqXDwIedVB7+b8bgy0rJIb7tp8+WfoTvGs6z3hmGW6PO4hTaF39zLHtYN9nEPR1j4/N+SCQOnmzYvDV8luR/t0mGRahd+05sZfpMhweN+83CV+OdajklpYh+ZNhMSz+0XwS+ENlkZvHHGS6UtdNN5W0QHTzQeKyi9vdAlaKzp4/a4DLWS4sWCHpPnYXVf6M1AD9Gx3BoR1gsmiQWVezzCpMfEMpGsA2xXm5hMekLLnLdB9OLQ3nh8MF/MPW0rKGHRuwI9FD3aeIXkEePhEfRK9GKSBlcIK/QY442C3kJLJFlL4pHIIzcWzhUlEfUIX77Ym6LJSktGbbBb9L39fUddMFSS1ZhHSZXzyEHJPsL+lCNQa9PmZYbFjUW0zuHSi/8J8YUbRc9+D48dLu1Y/P4FJplHU8fQ5jMfi9aE/4qj0GRvVjqsqmn35pycnJy/5ieOeqcK74CaHAAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACcAAAAaCAYAAAA0R0VGAAAB6ElEQVR4Xu2UzSumYRTGj5kFI4mws7BC2Ch/gDDJYhYTdlIslI9Ssphm451sGJpZkEw2QyH5qLGlaeQjkULNLKhpCtlMTY0kZjFzXZ3zPm73+8RqWHh+9av3XM95Pu6vVyQiIiIi4sHJhwdwxOom+BkuwjzLyDI8hM0wBX6BP+EQfGY9PXALrsEi+A7uwVX4yXpewiW4AXfk+t5Q+CEd8C9cga/hU9EHfIdpMANmwhn4W/RlJBv+grNWT4neewb3YT/MsWu7sBOuw0rLONBu+51ADWwQnRV+XIlzbcCyXvgKpsILeAqfOH2b1vfc8mqrh50e8k10kC7tos++lSv4w8s4c3xJq9UcLeuJoEMkGV5aXmzZW6vr4k2i24OZzzws80Mf3jjmZeeWF1r9xurGoEOk3LIjJ9u2LL6chMvnfxxnkQO7E97I5fWzaafmfmSW62SDlrVZzQ9izUPh8tFylxYnq4KlzrWALNGmcau5VDG5uSyEPZSzQHj6TmBB0CHyXrSnwsm4j5ktOBn5Knp/TPRUh1Ivunn7RE8STx9PsA9fwNHOifZNys1ZJKPwWPSvJg73FJ/pbgdSK7p1eCCSvGsBH+ALPwzhjySetv8OR5ruhx5cOv5p3iuccn+jhtElt+yLiIiIx8w/oolvAFU12ukAAAAASUVORK5CYII=>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAaCAYAAACD+r1hAAAAq0lEQVR4XmNgGAXDAswH4h1oYl5A/ARNDAwUgPg/EO9HE18HFccAyxggEgZIYtZQsVVIYnDwGoqRQQ0DREMOmjgYgCQWoonthorroImDAUgiDYnPBcTfgfgxlJ+LJMfAygDRsBGI2YCYCYhPQcVAIScAVQMHDkB8HIgfMUCC8ARUQSUQ3wHii3CVUNAAxGHogvjAPiAWRxfEBdiB+Ce6ID7gC8S/0QVHARIAAEsrIrCS3WdPAAAAAElFTkSuQmCC>