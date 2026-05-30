import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useLake, usePrediction, useSensorHistory, useSatelliteLatest } from '../hooks/useData'
import { Card, SectionLabel, LoadingPane, ErrorPane, RiskRing } from '../components/ui'
import AttentionChart from '../components/dashboard/AttentionChart'
import UncertaintyBands from '../components/dashboard/UncertaintyBands'
import RecommendationCards from '../components/dashboard/RecommendationCards'
import SensorChart, { PARAMS as SENSOR_PARAMS } from '../components/dashboard/SensorChart'
import SatellitePanel from '../components/satellite/SatellitePanel'

const TABS = [
  { id: 'attention',    label: '🧠 Attention' },
  { id: 'uncertainty',  label: '📊 Uncertainty' },
  { id: 'actions',      label: '⚡ Actions'  },
  { id: 'sensors',      label: '📡 Sensors'  },
  { id: 'satellite',    label: '🛰️ Satellite' },
]

export default function LakeDetail() {
  const { lakeId }         = useParams()
  const [tab, setTab]      = useState('attention')
  const [sensorParam, setSensorParam] = useState('dissolved_oxygen')

  const { data: lake,       loading: lL, error: lE  } = useLake(lakeId)
  const { data: prediction, loading: pL, error: pE  } = usePrediction(lakeId)
  const { data: sensorHist, loading: sHL             } = useSensorHistory(lakeId, { limit: 30 })
  const { data: satellite                             } = useSatelliteLatest(lakeId)

  const weights = prediction?.attention_weights || []
  const recs    = prediction?.recommendations   || []

  const loading = lL || pL
  const error   = lE || pE

  if (loading) return <div style={{ padding: 32 }}><LoadingPane label={`Loading ${lakeId}…`}/></div>
  if (error)   return <div style={{ padding: 32 }}><ErrorPane message={error}/></div>

  return (
    <div style={{ padding: 28 }}>
      {/* Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 22, flexWrap: 'wrap' }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 7, background: 'rgba(0,210,255,0.06)', border: '1px solid var(--border)', borderRadius: 8, padding: '7px 14px', textDecoration: 'none', fontSize: 11, fontWeight: 700, color: 'var(--cyan)' }}>
          ← National Grid
        </Link>
        <div style={{ fontSize: 10, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>
          LakePulse AI / <span style={{ color: 'var(--cyan)' }}>{lake?.name || lakeId}</span>
        </div>
        {lake?.state && <span style={{ fontSize: 9, padding: '2px 9px', borderRadius: 10, background: 'rgba(0,210,255,0.07)', border: '1px solid rgba(0,210,255,0.15)', color: 'rgba(0,210,255,0.7)', fontWeight: 700 }}>{lake.state}</span>}
      </div>

      {/* Title */}
      <div style={{ marginBottom: 20 }}>
        <SectionLabel>Lake Detail — 7-Day AI Forecast</SectionLabel>
        <div style={{ fontSize: 22, fontWeight: 800 }}>{lake?.name || lakeId}</div>
        {lake?.description && <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 4, maxWidth: 560 }}>{lake.description}</div>}
      </div>

      {/* Risk Rings */}
      {prediction && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(190px,1fr))', gap: 14, marginBottom: 24 }}>
          <RiskRing label="Bloom Risk (7d)"    value={prediction.bloom_risk?.mean}    std={prediction.bloom_risk?.std}    isRisk/>
          <RiskRing label="Mosquito Risk (7d)" value={prediction.mosquito_risk?.mean} std={prediction.mosquito_risk?.std} isRisk/>
          <RiskRing label="Dissolved O₂"       value={prediction.do_t7?.mean}         std={prediction.do_t7?.std}         isOk={(prediction.do_t7?.mean ?? 0) >= 5}/>
          <RiskRing label="Chlorophyll-a"      value={prediction.chl_a_t7?.mean}      std={prediction.chl_a_t7?.std}      isOk={(prediction.chl_a_t7?.mean ?? 99) <= 25} unit="μg/L"/>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 18, borderBottom: '1px solid rgba(0,210,255,0.1)', paddingBottom: 10, overflowX: 'auto' }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            style={{ padding: '7px 14px', borderRadius: 7, border: 'none', cursor: 'pointer', fontSize: 11, fontWeight: 700, fontFamily: 'inherit', whiteSpace: 'nowrap', transition: 'all .15s',
              background: tab===t.id ? 'linear-gradient(135deg,#007a87,#00d2ff)' : 'transparent',
              color: tab===t.id ? '#03090f' : 'var(--muted)' }}>
            {t.label}{t.id==='actions' && recs.length>0 ? ` (${recs.length})` : ''}
          </button>
        ))}
      </div>

      {/* Tab panels */}
      {tab === 'attention' && (
        <Card style={{ padding: 20 }}>
          {weights.length > 0 ? <AttentionChart weights={weights}/> : <ErrorPane message="No attention weights in prediction response."/>}
        </Card>
      )}

      {tab === 'uncertainty' && (
        <Card style={{ padding: 20 }}>
          {prediction ? <UncertaintyBands prediction={prediction}/> : <ErrorPane message="No prediction data."/>}
        </Card>
      )}

      {tab === 'actions' && (
        <div>
          <Card style={{ padding: '14px 18px', marginBottom: 16, borderLeft: '3px solid var(--lime)' }}>
            <div style={{ fontSize: 11, fontWeight: 700, marginBottom: 3 }}>
              AI-Generated Action Plan
              <span style={{ marginLeft: 8, fontSize: 9, fontWeight: 700, padding: '2px 7px', borderRadius: 10, background: 'rgba(46,213,115,0.08)', border: '1px solid rgba(46,213,115,0.2)', color: 'var(--lime)' }}>LIVE API</span>
            </div>
            <div style={{ fontSize: 10, color: 'var(--muted)', lineHeight: 1.7 }}>
              Ranked by severity from the 7-day LSTM forecast. Expand any card for rationale, agency, and timeline.
            </div>
          </Card>
          <RecommendationCards recs={recs}/>
        </div>
      )}

      {tab === 'sensors' && (
        <Card style={{ padding: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 4 }}>30-Day Sensor History</div>
          <div style={{ fontSize: 10, color: 'var(--muted)', marginBottom: 16 }}>Live readings from field sensors · /api/sensors/{lakeId}/history</div>
          <div style={{ display: 'flex', gap: 6, marginBottom: 16, flexWrap: 'wrap' }}>
            {SENSOR_PARAMS.map(p => (
              <button key={p.key} onClick={() => setSensorParam(p.key)}
                style={{ padding: '5px 11px', borderRadius: 20, border: `1px solid ${sensorParam===p.key ? p.color : 'var(--border)'}`, background: sensorParam===p.key ? `${p.color}15` : 'transparent', color: sensorParam===p.key ? p.color : 'var(--muted)', fontSize: 11, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
                {p.label}
              </button>
            ))}
          </div>
          {sHL ? <LoadingPane/> : sensorHist?.length > 0
            ? <SensorChart data={sensorHist} activeParam={sensorParam}/>
            : <ErrorPane message="No sensor history available for this lake."/>}
        </Card>
      )}

      {tab === 'satellite' && (
        <SatellitePanel lakeId={lakeId} data={satellite}/>
      )}
    </div>
  )
}
