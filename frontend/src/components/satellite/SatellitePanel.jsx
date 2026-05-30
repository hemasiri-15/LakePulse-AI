import { useSatelliteLatest, useSatelliteShrinkage } from '../../hooks/useData'
import { Card, SectionLabel, LoadingPane, ErrorPane, StatTile } from '../ui'
import { fmtDate, fmtNum } from '../../utils/helpers'

export default function SatellitePanel({ lakeId }) {
  const { data: latest,   loading: lL, error: lE } = useSatelliteLatest(lakeId)
  const { data: shrinkage,loading: sL, error: sE } = useSatelliteShrinkage(lakeId)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Card style={{ padding: 20 }}>
        <SectionLabel>🛰️ Latest Satellite Reading</SectionLabel>
        <div style={{ fontSize: 10, color: 'var(--muted)', marginBottom: 16 }}>Sentinel-2 derived indices · /api/satellite/{lakeId}/latest</div>
        {lL && <LoadingPane/>}
        {lE && <ErrorPane message={lE}/>}
        {latest && (
          <>
            <div style={{ fontSize: 9, color: 'var(--muted)', fontFamily: 'var(--mono)', marginBottom: 12 }}>
              Acquired: {fmtDate(latest.acquired_at || latest.date)}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(130px,1fr))', gap: 12 }}>
              {latest.ndwi       != null && <StatTile label="NDWI"             value={fmtNum(latest.ndwi, 3)}       color="#00d2ff" icon="💧"/>}
              {latest.surface_temp != null && <StatTile label="Surface Temp (°C)" value={fmtNum(latest.surface_temp)} color="#ffa502" icon="🌡️"/>}
              {latest.ndvi       != null && <StatTile label="Vegetation Index" value={fmtNum(latest.ndvi, 3)}       color="#2ed573" icon="🌿"/>}
              {latest.foam_index != null && <StatTile label="Foam Index"       value={fmtNum(latest.foam_index, 3)} color="#ff4757" icon="🫧"/>}
              {latest.turbidity  != null && <StatTile label="Turbidity (NTU)"  value={fmtNum(latest.turbidity)}     color="#a29bfe" icon="👁️"/>}
              {latest.algal_bloom_probability != null && <StatTile label="Bloom Probability" value={`${Math.round(latest.algal_bloom_probability*100)}%`} color="#ffd32a" icon="🌊"/>}
            </div>
          </>
        )}
      </Card>

      <Card style={{ padding: 20 }}>
        <SectionLabel>📉 Lake Surface Shrinkage</SectionLabel>
        <div style={{ fontSize: 10, color: 'var(--muted)', marginBottom: 16 }}>Long-term surface area change from satellite time series</div>
        {sL && <LoadingPane/>}
        {sE && <ErrorPane message={sE}/>}
        {shrinkage && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(140px,1fr))', gap: 12 }}>
            {shrinkage.current_area_km2   != null && <StatTile label="Current Area (km²)"    value={fmtNum(shrinkage.current_area_km2, 2)}  color="var(--cyan)"/>}
            {shrinkage.historical_area_km2 != null && <StatTile label="Historical Area (km²)" value={fmtNum(shrinkage.historical_area_km2, 2)} color="var(--muted)"/>}
            {shrinkage.shrinkage_pct      != null && <StatTile label="Shrinkage %"            value={`${fmtNum(shrinkage.shrinkage_pct, 1)}%`} color="#ff4757"/>}
            {shrinkage.trend              != null && <StatTile label="Trend"                  value={shrinkage.trend}                          color={shrinkage.trend==='shrinking'?'#ffa502':'#2ed573'}/>}
          </div>
        )}
        {!sL && !sE && !shrinkage && (
          <div style={{ color: 'var(--muted)', fontSize: 11, padding: '12px 0' }}>No shrinkage data available.</div>
        )}
      </Card>
    </div>
  )
}
