import { useSatelliteAlerts } from '../hooks/useData'
import { Card, SectionLabel, LoadingPane, ErrorPane, EmptyState, SevBadge } from '../components/ui'
import { fmtDate } from '../utils/helpers'

export default function SatellitePage() {
  const { data: alerts, loading, error } = useSatelliteAlerts()

  return (
    <div style={{ padding: 28 }}>
      <SectionLabel>🛰️ Satellite Intelligence</SectionLabel>
      <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 6 }}>Satellite Monitoring</h1>
      <p style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 20, maxWidth: 540 }}>
        Sentinel-2 derived indices — NDWI, surface temperature, vegetation, algal bloom probability.
        Navigate to any lake for per-lake satellite data and shrinkage analysis.
      </p>

      <Card style={{ padding: 20, marginBottom: 20 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))', gap: 14 }}>
          {[
            { icon: '💧', label: 'NDWI',              desc: 'Normalized Difference Water Index — detects water body extent changes' },
            { icon: '🌡️', label: 'Surface Temperature',desc: 'Thermal band analysis for warm water plumes and evaporation' },
            { icon: '🌿', label: 'Vegetation Index',   desc: 'NDVI around lake perimeter — encroachment detection' },
            { icon: '🫧', label: 'Foam Index',         desc: 'Detects surface foam bands typical of cyanobacterial blooms' },
          ].map(item => (
            <div key={item.label} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <span style={{ fontSize: 22 }}>{item.icon}</span>
              <div>
                <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 3 }}>{item.label}</div>
                <div style={{ fontSize: 10, color: 'var(--muted)', lineHeight: 1.6 }}>{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <SectionLabel>Platform-Wide Satellite Alerts</SectionLabel>
      {loading && <LoadingPane label="Loading satellite alerts…"/>}
      {error   && <ErrorPane message={error}/>}
      {!loading && alerts?.length === 0 && <EmptyState icon="🛰️" title="No satellite alerts" sub="All water bodies within normal parameters."/>}
      {alerts?.map(a => (
        <Card key={a.id} style={{ padding: '12px 16px', marginBottom: 10, borderLeft: '3px solid #ffa502' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
            <div>
              <div style={{ display: 'flex', gap: 8, marginBottom: 5, flexWrap: 'wrap', alignItems: 'center' }}>
                <SevBadge level={a.severity || 'moderate'}/>
                {a.lake_name && <span style={{ fontSize: 10, color: 'var(--muted)' }}>📍 {a.lake_name}</span>}
              </div>
              <div style={{ fontSize: 12, fontWeight: 700 }}>{a.message || a.title}</div>
              {a.index && <div style={{ fontSize: 10, color: 'rgba(180,230,248,0.5)', marginTop: 3 }}>Index: {a.index} · Value: {a.value}</div>}
            </div>
            <div style={{ fontSize: 10, color: 'var(--muted)', fontFamily: 'var(--mono)', flexShrink: 0 }}>{fmtDate(a.created_at)}</div>
          </div>
        </Card>
      ))}
    </div>
  )
}
