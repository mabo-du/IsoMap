import { useState, useEffect } from 'react';
import { normaliseChronology } from '../../api/sidecar';

interface ChronologyReviewProps {
  filePath: string;
  mappings: Record<string, [string, string]>; // Target Field -> [Source Column, Detected Format]
  sheetName?: string;
}

export const ChronologyReview = ({ filePath, mappings, sheetName }: ChronologyReviewProps) => {
  const [preview, setPreview] = useState<Record<string, any>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const runNormalisation = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await normaliseChronology(filePath, mappings, sheetName);
        setPreview(result);
      } catch (err: any) {
        setError(err.message || "Failed to normalise chronology");
      } finally {
        setLoading(false);
      }
    };
    
    runNormalisation();
  }, [filePath, mappings, sheetName]);

  if (loading) return <div>Normalising dates...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  const columns = Object.keys(mappings);

  return (
    <div className="chronology-review" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', fontFamily: 'system-ui' }}>
      <h2>Chronology Normalisation</h2>
      <p>The system has converted the source date formats into a standardised `cal_BP` scale based on the 1950 CE anchor.</p>
      
      <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f5f5f5', textAlign: 'left' }}>
              {columns.map(col => (
                <th key={col} style={{ padding: '8px', border: '1px solid #ccc' }}>
                  {col} <br/>
                  <small style={{ fontWeight: 'normal', color: '#666' }}>({mappings[col][1]} → cal_BP)</small>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {preview.map((row, idx) => (
              <tr key={idx}>
                {columns.map(col => (
                  <td key={col} style={{ padding: '8px', border: '1px solid #eee' }}>
                    {row[col] !== null ? row[col] : 'null'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
