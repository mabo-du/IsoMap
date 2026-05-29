import { useState } from 'react';
import { save } from '@tauri-apps/plugin-dialog';
import { exportDataset, generateDataPaper } from '../../api/sidecar';

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

  const handleExport = async (format: 'csv' | 'xlsx' | 'geojson' | 'isoarch_json' | 'lipd' | 'pangaea' | 'noaa' | 'rocrate' | 'datapaper') => {
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
        case 'pangaea':
          filters.push({ name: 'PANGAEA Submission (TXT)', extensions: ['txt'] });
          defaultPath += '.txt';
          break;
        case 'noaa':
          filters.push({ name: 'NOAA NCEI Submission (Excel)', extensions: ['xlsx'] });
          defaultPath += '_noaa.xlsx';
          break;
        case 'rocrate':
          filters.push({ name: 'Semantic Web RO-Crate (ZIP)', extensions: ['zip'] });
          defaultPath += '_rocrate.zip';
          break;
        case 'datapaper':
          filters.push({ name: 'ESSD LaTeX Data Paper', extensions: ['tex'] });
          defaultPath = 'manuscript.tex';
          break;
      }

      const outputPath = await save({
        defaultPath,
        filters
      });

      if (outputPath) {
        if (format === 'datapaper') {
          await generateDataPaper(filePath, schemaName, outputPath, sheetName);
        } else {
          await exportDataset(filePath, schemaName, appliedMappings, format as any, outputPath, sheetName, datasetName);
        }
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
        {[
          { format: 'csv', label: 'Export to CSV', bg: '#0066cc', span: 1 },
          { format: 'xlsx', label: 'Export to Excel', bg: '#207245', span: 1 },
          { format: 'geojson', label: 'Export to GeoJSON (Neotoma Format)', bg: '#455a64', span: 1 },
          { format: 'isoarch_json', label: 'Export to JSON (IsoArcH API)', bg: '#673ab7', span: 1 },
          { format: 'lipd', label: 'Export to LiPD (Linked Paleo Data)', bg: '#e65100', span: 2 },
          { format: 'pangaea', label: 'Export for PANGAEA Submission', bg: '#0288d1', span: 1 },
          { format: 'noaa', label: 'Export for NOAA NCEI Submission', bg: '#00796b', span: 1 },
          { format: 'rocrate', label: 'Export to Semantic Web RO-Crate', bg: '#4a148c', span: 1 },
          { format: 'datapaper', label: 'Generate LaTeX Data Paper (ESSD)', bg: '#bf360c', span: 1 }
        ].map(btn => (
          <button 
            key={btn.format}
            onClick={() => handleExport(btn.format as any)} 
            disabled={loading}
            style={{ 
              padding: '1rem', 
              background: btn.bg, 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer',
              gridColumn: btn.span === 2 ? 'span 2' : undefined
            }}
          >
            {btn.label}
          </button>
        ))}
      </div>

      {loading && <div style={{ marginTop: '1rem', color: '#666' }}>Processing export...</div>}
      {error && <div style={{ marginTop: '1rem', color: '#d32f2f', padding: '1rem', background: '#ffebee', borderRadius: '4px' }}>{error}</div>}
      {success && <div style={{ marginTop: '1rem', color: '#2e7d32', padding: '1rem', background: '#e8f5e9', borderRadius: '4px' }}>{success}</div>}
    </div>
  );
};
