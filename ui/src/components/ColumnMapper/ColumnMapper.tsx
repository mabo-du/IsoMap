import { useState, useEffect } from 'react';
import { mapColumns, saveOverride, MappingSuggestion } from '../../api/sidecar';

interface ColumnMapperProps {
  filePath: string;
  sheetName?: string;
  schemaName: string;
}

export const ColumnMapper = ({ filePath, sheetName, schemaName }: ColumnMapperProps) => {
  const [mappings, setMappings] = useState<Record<string, MappingSuggestion[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Store the user's selected target field for each source column
  const [selections, setSelections] = useState<Record<string, string>>({});

  useEffect(() => {
    const loadMappings = async () => {
      setLoading(true);
      try {
        const result = await mapColumns(filePath, schemaName, sheetName);
        setMappings(result);
        
        // Auto-select the top suggestion
        const initialSelections: Record<string, string> = {};
        for (const [col, suggestions] of Object.entries(result)) {
          if (suggestions.length > 0) {
            initialSelections[col] = suggestions[0].target;
          }
        }
        setSelections(initialSelections);
      } catch (err: any) {
        setError(err.message || "Failed to load column mappings");
      } finally {
        setLoading(false);
      }
    };
    
    loadMappings();
  }, [filePath, schemaName, sheetName]);

  const handleSelectionChange = async (sourceColumn: string, targetField: string) => {
    setSelections(prev => ({ ...prev, [sourceColumn]: targetField }));
    
    // Save override to preferences database via sidecar
    try {
      await saveOverride(sourceColumn, targetField, schemaName);
    } catch (err) {
      console.error("Failed to save override", err);
    }
  };

  if (loading) return <div>Analyzing column semantics and running schema matching pipeline...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div className="column-mapper" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', fontFamily: 'system-ui' }}>
      <h2>Map Columns to {schemaName} Schema</h2>
      <p>IsoMap has suggested mappings based on exact matches, your past preferences, fuzzy text similarity, semantic embeddings, and value distributions.</p>

      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
        <thead>
          <tr style={{ background: '#f5f5f5', textAlign: 'left' }}>
            <th style={{ padding: '8px', border: '1px solid #ccc' }}>Your Column (Source)</th>
            <th style={{ padding: '8px', border: '1px solid #ccc' }}>Target Field (Schema)</th>
            <th style={{ padding: '8px', border: '1px solid #ccc' }}>Confidence</th>
            <th style={{ padding: '8px', border: '1px solid #ccc' }}>Method</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(mappings).map(([sourceCol, suggestions]) => {
            const currentSelection = selections[sourceCol] || '';
            const activeSuggestion = suggestions.find(s => s.target === currentSelection);
            
            return (
              <tr key={sourceCol}>
                <td style={{ padding: '8px', border: '1px solid #eee', fontWeight: 'bold' }}>{sourceCol}</td>
                <td style={{ padding: '8px', border: '1px solid #eee' }}>
                  <select 
                    value={currentSelection} 
                    onChange={(e) => handleSelectionChange(sourceCol, e.target.value)}
                    style={{ width: '100%', padding: '4px' }}
                  >
                    <option value="">-- Ignore Column --</option>
                    {suggestions.map((s, idx) => (
                      <option key={idx} value={s.target}>
                        {s.target} ({Math.round(s.confidence * 100)}%)
                      </option>
                    ))}
                  </select>
                </td>
                <td style={{ padding: '8px', border: '1px solid #eee' }}>
                  {activeSuggestion ? `${Math.round(activeSuggestion.confidence * 100)}%` : '-'}
                  {activeSuggestion && (
                    <div style={{
                      width: '100%',
                      background: '#eee',
                      height: '4px',
                      marginTop: '4px',
                      borderRadius: '2px'
                    }}>
                      <div style={{
                        width: `${activeSuggestion.confidence * 100}%`,
                        background: activeSuggestion.confidence > 0.8 ? 'green' : activeSuggestion.confidence > 0.5 ? 'orange' : 'red',
                        height: '100%',
                        borderRadius: '2px'
                      }} />
                    </div>
                  )}
                </td>
                <td style={{ padding: '8px', border: '1px solid #eee', fontSize: '0.85em', color: '#666' }}>
                  {activeSuggestion ? activeSuggestion.method : 'manual'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
