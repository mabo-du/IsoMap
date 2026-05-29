import { useState } from 'react';
import { save } from '@tauri-apps/plugin-dialog';
import { exportDataset } from '../../api/sidecar';

interface ExportPanelProps {
  filePath: string;
  schemaName: string;
  appliedMappings: Record<string, string>;
  sheetName?: string;
}

export const ExportPanel = ({ filePath, schemaName, appliedMappings, sheetName }: ExportPanelProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [datasetName, setDatasetName] = useState("IsoMap_Export");

  const handleExport = async (format: 'csv' | 'xlsx' | 'geojson' | 'isoarch_json' | 'lipd') => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      // Setup default extensions and filters based on format
      let filters = [];
      let defaultPath = `export_${schemaName}`;
      
      switch (format) {
        case 'csv':
          filters.push({ name: 'CSV', extensions: ['csv'] });
          defaultPath += '.csv';
          break;
        case 'xlsx':
          filters.push({ name: 'Excel', extensions: ['xlsx'] });
          defaultPath += '.xlsx';
          break;
        case 'geojson':
          filters.push({ name: 'GeoJSON', extensions: ['geojson'] });
          defaultPath += '.geojson';
          break;
        case 'isoarch_json':
          filters.push({ name: 'JSON', extensions: ['json'] });
          defaultPath += '.json';
          break;
        case 'lipd':
          filters.push({ name: 'LiPD Archive', extensions: ['lpd'] });
          defaultPath = `${datasetName}.lpd`;
          break;
      }

      const outputPath = await save({
        defaultPath,
        filters
      });

      if (outputPath) {
        await exportDataset(filePath, schemaName, appliedMappings, format, outputPath, sheetName, datasetName);
        setSuccess(`Successfully exported to: ${outputPath}`);
      }
    } catch (err: any) {
      setError(err.message || `Failed to export as ${format.toUpperCase()}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="export-panel" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', fontFamily: 'system-ui' }}>
      <h2>Export Dataset</h2>
      <p>Your dataset is fully mapped and validated against the <strong>{schemaName}</strong> schema. You can now export the standardised data.</p>
      
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Dataset Name (for LiPD):</label>
        <input 
          type="text" 
          value={datasetName}
          onChange={(e) => setDatasetName(e.target.value)}
          style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '2rem' }}>
        <button 
          onClick={() => handleExport('csv')} 
          disabled={loading}
          style={{ padding: '1rem', background: '#0066cc', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Export to CSV
        </button>
        <button 
          onClick={() => handleExport('xlsx')} 
          disabled={loading}
          style={{ padding: '1rem', background: '#207245', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Export to Excel
        </button>
        <button 
          onClick={() => handleExport('geojson')} 
          disabled={loading}
          style={{ padding: '1rem', background: '#455a64', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Export to GeoJSON (Neotoma Format)
        </button>
        <button 
          onClick={() => handleExport('isoarch_json')} 
          disabled={loading}
          style={{ padding: '1rem', background: '#673ab7', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Export to JSON (IsoArcH API)
        </button>
        <button 
          onClick={() => handleExport('lipd')} 
          disabled={loading}
          style={{ padding: '1rem', background: '#e65100', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', gridColumn: 'span 2' }}
        >
          Export to LiPD (Linked Paleo Data)
        </button>
      </div>

      {loading && <div style={{ marginTop: '1rem', color: '#666' }}>Processing export...</div>}
      {error && <div style={{ marginTop: '1rem', color: '#d32f2f', padding: '1rem', background: '#ffebee', borderRadius: '4px' }}>{error}</div>}
      {success && <div style={{ marginTop: '1rem', color: '#2e7d32', padding: '1rem', background: '#e8f5e9', borderRadius: '4px' }}>{success}</div>}
    </div>
  );
};
