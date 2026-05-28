import { useState } from "react";
import { ImportWizard } from "./components/ImportWizard/ImportWizard";
import { ColumnMapper } from "./components/ColumnMapper/ColumnMapper";
import { MapPreview } from "./components/MapPreview/MapPreview";
import { ChronologyReview } from "./components/ChronologyReview/ChronologyReview";
import { ValidationReport } from "./components/ValidationReport/ValidationReport";
import { ExportPanel } from "./components/ExportPanel/ExportPanel";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState<'import' | 'map' | 'chronology' | 'spatial' | 'validate' | 'export'>('import');

  return (
    <main className="container">
      <h1>IsoMap</h1>
      <p>Isotopic and paleoecological data standardisation middleware</p>
      
      <div style={{ marginBottom: '1rem', borderBottom: '1px solid #ccc', paddingBottom: '0.5rem' }}>
        <button 
          onClick={() => setActiveTab('import')}
          style={{ marginRight: '1rem', fontWeight: activeTab === 'import' ? 'bold' : 'normal' }}
        >
          1. Import Engine
        </button>
        <button 
          onClick={() => setActiveTab('map')}
          style={{ marginRight: '1rem', fontWeight: activeTab === 'map' ? 'bold' : 'normal' }}
        >
          2. Column Mapping
        </button>
        <button 
          onClick={() => setActiveTab('chronology')}
          style={{ marginRight: '1rem', fontWeight: activeTab === 'chronology' ? 'bold' : 'normal' }}
        >
          2.5. Chronology
        </button>
        <button 
          onClick={() => setActiveTab('spatial')}
          style={{ marginRight: '1rem', fontWeight: activeTab === 'spatial' ? 'bold' : 'normal' }}
        >
          3. Spatial Verification
        </button>
        <button 
          onClick={() => setActiveTab('validate')}
          style={{ marginRight: '1rem', fontWeight: activeTab === 'validate' ? 'bold' : 'normal' }}
        >
          4. Validation
        </button>
        <button 
          onClick={() => setActiveTab('export')}
          style={{ fontWeight: activeTab === 'export' ? 'bold' : 'normal' }}
        >
          5. Export
        </button>
      </div>

      {activeTab === 'import' && <ImportWizard />}
      {activeTab === 'map' && <ColumnMapper />}
      {activeTab === 'chronology' && (
        <ChronologyReview
          filePath="tests/test_data/legacy_data.csv"
          mappings={{
            "Age": ["age", "14C_BP"]
          }}
        />
      )}
      {activeTab === 'spatial' && (
        <MapPreview
          filePath="tests/test_data/legacy_data.csv"
          latCol="lat"
          lonCol="lon"
        />
      )}
      {activeTab === 'validate' && (
        <ValidationReport
          filePath="tests/test_data/legacy_data.csv"
          schemaName="neotoma"
          appliedMappings={{
            "SiteName": "site",
            "Latitude": "lat",
            "Longitude": "lon",
            "Age": "age"
          }}
        />
      )}
      {activeTab === 'export' && (
        <ExportPanel
          filePath="tests/test_data/legacy_data.csv"
          schemaName="neotoma"
          appliedMappings={{
            "SiteName": "site",
            "Latitude": "lat",
            "Longitude": "lon",
            "Age": "age"
          }}
        />
      )}
    </main>
  );
}

export default App;
