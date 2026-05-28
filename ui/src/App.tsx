import { useState } from "react";
import { ImportWizard } from "./components/ImportWizard/ImportWizard";
import { ColumnMapper } from "./components/ColumnMapper/ColumnMapper";
import { MapPreview } from "./components/MapPreview/MapPreview";
import { ValidationReport } from "./components/ValidationReport/ValidationReport";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState<'import' | 'map' | 'spatial' | 'validate'>('import');

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
          onClick={() => setActiveTab('spatial')}
          style={{ marginRight: '1rem', fontWeight: activeTab === 'spatial' ? 'bold' : 'normal' }}
        >
          3. Spatial Verification
        </button>
        <button 
          onClick={() => setActiveTab('validate')}
          style={{ fontWeight: activeTab === 'validate' ? 'bold' : 'normal' }}
        >
          4. Validation
        </button>
      </div>

      {activeTab === 'import' && <ImportWizard />}
      {activeTab === 'map' && (
        <ColumnMapper 
          filePath="tests/test_data/legacy_data.csv" 
          schemaName="neotoma" 
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
            "Age": "age"
          }}
        />
      )}
    </main>
  );
}

export default App;
