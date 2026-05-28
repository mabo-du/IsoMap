import { useState } from 'react';
import { open } from '@tauri-apps/plugin-dialog';
import { getSheetNames, importDataset, ImportResult } from '../../api/sidecar';

export const ImportWizard = () => {
  const [filePath, setFilePath] = useState<string | null>(null);
  const [sheets, setSheets] = useState<string[]>([]);
  const [selectedSheet, setSelectedSheet] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelectFile = async () => {
    try {
      const selected = await open({
        filters: [{
          name: 'Spreadsheets',
          extensions: ['csv', 'xlsx', 'xls']
        }]
      });
      if (selected && typeof selected === 'string') {
        setFilePath(selected);
        setError(null);
        setImportResult(null);
        
        if (selected.endsWith('.xlsx') || selected.endsWith('.xls')) {
          setLoading(true);
          const sheetNames = await getSheetNames(selected);
          setSheets(sheetNames);
          setSelectedSheet(sheetNames[0] || null);
          setLoading(false);
        } else {
          setSheets([]);
          setSelectedSheet(null);
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to open file");
    }
  };

  const handleImport = async () => {
    if (!filePath) return;
    
    setLoading(true);
    setError(null);
    try {
      const result = await importDataset(filePath, selectedSheet || undefined);
      setImportResult(result);
    } catch (err: any) {
      setError(err.message || "Failed to import dataset");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="import-wizard" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', fontFamily: 'system-ui' }}>
      <h2>Import Dataset</h2>
      
      <div style={{ marginBottom: '1rem' }}>
        <button onClick={handleSelectFile} disabled={loading}>
          Select File (CSV, XLSX, XLS)
        </button>
        {filePath && <span style={{ marginLeft: '1rem' }}>{filePath}</span>}
      </div>

      {sheets.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          <label>Select Sheet: </label>
          <select value={selectedSheet || ''} onChange={(e) => setSelectedSheet(e.target.value)}>
            {sheets.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      )}

      {filePath && (
        <div style={{ marginBottom: '2rem' }}>
          <button onClick={handleImport} disabled={loading} style={{ background: '#0066cc', color: 'white' }}>
            {loading ? 'Importing...' : 'Load Dataset'}
          </button>
        </div>
      )}

      {error && <div style={{ color: 'red', marginBottom: '1rem' }}>Error: {error}</div>}

      {importResult && (
        <div className="import-results">
          <h3>Preview ({importResult.total_rows} total rows)</h3>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '0.9rem' }}>
              <thead>
                <tr>
                  {importResult.columns.map(col => {
                    const info = importResult.inferred_types[col];
                    return (
                      <th key={col} style={{ border: '1px solid #ccc', padding: '8px', background: '#f5f5f5' }}>
                        <div>{col}</div>
                        <div style={{ fontSize: '0.7rem', color: '#666', fontWeight: 'normal' }}>
                          {info.type !== 'unknown' ? `(${info.type}, ${info.confidence})` : '(unknown)'}
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {importResult.preview.map((row, i) => (
                  <tr key={i}>
                    {importResult.columns.map(col => (
                      <td key={col} style={{ border: '1px solid #eee', padding: '4px 8px' }}>
                        {row[col] !== null ? String(row[col]) : ''}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
