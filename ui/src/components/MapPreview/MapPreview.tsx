import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getSpatialPreview, SpatialPreview } from '../../api/sidecar';

// Fix leaflet icon path issues in React
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// Helper component to auto-zoom to bounds
const BoundsFitter = ({ bbox }: { bbox: SpatialPreview['bbox'] }) => {
  const map = useMap();
  
  useEffect(() => {
    if (bbox) {
      const bounds: L.LatLngBoundsExpression = [
        [bbox.min_lat, bbox.min_lon],
        [bbox.max_lat, bbox.max_lon]
      ];
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [bbox, map]);
  
  return null;
};

interface MapPreviewProps {
  filePath: string;
  latCol: string;
  lonCol: string;
  sheetName?: string;
}

export const MapPreview = ({ filePath, latCol, lonCol, sheetName }: MapPreviewProps) => {
  const [data, setData] = useState<SpatialPreview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMap = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await getSpatialPreview(filePath, latCol, lonCol, sheetName);
        setData(result);
      } catch (err: any) {
        setError(err.message || "Failed to load spatial data");
      } finally {
        setLoading(false);
      }
    };
    
    loadMap();
  }, [filePath, latCol, lonCol, sheetName]);

  if (loading) return <div>Parsing coordinates and generating GeoJSON...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;
  if (!data || !data.geojson) return <div>No spatial data found.</div>;

  return (
    <div className="map-preview" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', fontFamily: 'system-ui' }}>
      <h2>Spatial Verification Preview</h2>
      <p>Data mapped using inferred EPSG:4326 geometries from {latCol} and {lonCol}.</p>
      
      <div style={{ height: '400px', width: '100%', borderRadius: '8px', overflow: 'hidden', border: '1px solid #ccc' }}>
        <MapContainer 
          center={[0, 0]} 
          zoom={2} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <GeoJSON 
            data={data.geojson} 
            pointToLayer={(_feature, latlng) => {
              return L.circleMarker(latlng, {
                radius: 6,
                fillColor: "#ff7800",
                color: "#000",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
              });
            }}
          />
          <BoundsFitter bbox={data.bbox} />
        </MapContainer>
      </div>
      
      {data.bbox && (
        <div style={{ marginTop: '1rem', padding: '1rem', background: '#f5f5f5', borderRadius: '4px' }}>
          <strong>Bounding Box:</strong>
          <ul style={{ margin: '0.5rem 0', listStyle: 'none', padding: 0 }}>
            <li>Min Latitude: {data.bbox.min_lat.toFixed(6)}</li>
            <li>Max Latitude: {data.bbox.max_lat.toFixed(6)}</li>
            <li>Min Longitude: {data.bbox.min_lon.toFixed(6)}</li>
            <li>Max Longitude: {data.bbox.max_lon.toFixed(6)}</li>
          </ul>
        </div>
      )}
    </div>
  );
};
