import { useState, useEffect } from 'react';
import { validateDataset, ValidationReportData } from '../../api/sidecar';

interface ValidationReportProps {
  filePath: string;
  schemaName: string;
  appliedMappings: Record<string, string>;
  sheetName?: string;
}

export const ValidationReport = ({ filePath, schemaName, appliedMappings, sheetName }: ValidationReportProps) => {
  const [report, setReport] = useState<ValidationReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const runValidation = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await validateDataset(filePath, schemaName, appliedMappings, sheetName);
        setReport(result);
      } catch (err: any) {
        setError(err.message || "Failed to run validation");
      } finally {
        setLoading(false);
      }
    };
    
    runValidation();
  }, [filePath, schemaName, appliedMappings, sheetName]);

  if (loading) return <div>Running dataset validation against {schemaName} schema...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;
  if (!report) return null;

  return (
    <div className="validation-report" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', fontFamily: 'system-ui' }}>
      <h2>Validation Report</h2>
      
      <div style={{
        padding: '1rem',
        borderRadius: '4px',
        background: report.valid ? '#e8f5e9' : '#ffebee',
        color: report.valid ? '#2e7d32' : '#c62828',
        marginBottom: '1rem',
        border: `1px solid ${report.valid ? '#a5d6a7' : '#ffcdd2'}`
      }}>
        <h3 style={{ margin: '0 0 0.5rem 0' }}>
          {report.valid ? '✅ Dataset is Valid' : '❌ Schema Violations Detected'}
        </h3>
        {report.message && <p>{report.message}</p>}
        {!report.valid && <p>Found {report.errors.length} violations across {Object.keys(report.row_errors).length} rows.</p>}
      </div>

      {!report.valid && report.errors.length > 0 && (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f5f5f5', textAlign: 'left' }}>
                <th style={{ padding: '8px', border: '1px solid #ccc' }}>Row</th>
                <th style={{ padding: '8px', border: '1px solid #ccc' }}>Column</th>
                <th style={{ padding: '8px', border: '1px solid #ccc' }}>Value</th>
                <th style={{ padding: '8px', border: '1px solid #ccc' }}>Constraint Failed</th>
              </tr>
            </thead>
            <tbody>
              {report.errors.map((err, idx) => (
                <tr key={idx}>
                  <td style={{ padding: '8px', border: '1px solid #eee' }}>{err.row}</td>
                  <td style={{ padding: '8px', border: '1px solid #eee', fontWeight: 'bold' }}>{err.column}</td>
                  <td style={{ padding: '8px', border: '1px solid #eee' }}>{String(err.value)}</td>
                  <td style={{ padding: '8px', border: '1px solid #eee', color: '#d32f2f' }}>{err.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
