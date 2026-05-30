import { useNavigate } from 'react-router-dom'
import { useLakes } from '../hooks/useData'
import IndiaMap from '../components/map/IndiaMap'
import { Card, SectionLabel, StatTile, LoadingPane, ErrorPane, RiskBadge } from '../components/ui'
import { riskColor, fmtPct } from '../utils/helpers'

export default function NationalGrid() {
  const { data: lakes, loading, error } = useLakes()
  const navigate = useNavigate()
  
  const normalized = (lakes || []).map(l => ({...l, risk_score: 1 - ((l.health_score || 0) / 100)}))
  const sorted = lakes ? [...normalized].sort((a,b)=>(b.risk_score??0)-(a.risk_score??0)) : []
  const critical = sorted.filter(l=>(l.risk_score??0)>.8).length
  const high     = sorted.filter(l=>{const r=l.risk_score??0; return r>.6&&r<=.8}).length
  const bloom    = sorted.filter(l=>(l.risk_score??0)>.7).length

  return (
    <div style={{ padding: 28 }}>
      {/* Hero */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.22em', color: 'var(--cyan)', marginBottom: 6 }}>AI-POWERED ENVIRONMENTAL INTELLIGENCE</div>
        <h1 style={{ fontSize: 'clamp(20px,3vw,30px)', fontWeight: 800, lineHeight: 1.15, marginBottom: 6 }}>
          National Lake Monitoring Grid
          <span style={{ background: 'linear-gradient(90deg,var(--cyan),var(--lime))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}> · India</span>
        </h1>
        <p style={{ fontSize: 11, color: 'var(--muted)', lineHeight: 1.7, maxWidth: 540 }}>
          Attention-LSTM forecasting across India's critical water bodies. Click any lake for full AI analysis — uncertainty bands, attention weights, and government-actionable recommendations.
        </p>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(120px,1fr))', gap: 12, marginBottom: 24 }}>
        <StatTile label="Lakes Monitored" value={lakes?.length ?? '—'} color="var(--cyan)"/>
        <StatTile label="Critical Alerts"  value={critical}            color="#ff4757"/>
        <StatTile label="Bloom Risk >70%"  value={bloom}               color="#ffa502"/>
        <StatTile label="High Risk"         value={high}                color="#ffd32a"/>
        <StatTile label="Stable"            value={lakes ? sorted.filter(l=>(l.risk_score??0)<=.4).length : '—'} color="#2ed573"/>
      </div>

      {/* Map + Table */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 360px', gap: 20, alignItems: 'start' }}>
        <Card style={{ padding: 20 }}>
          <SectionLabel>Interactive Lake Map</SectionLabel>
          <div style={{ fontSize: 10, color: 'var(--muted)', marginBottom: 14 }}>Hover for AI risk preview · Click to open full dashboard</div>
          {loading && <LoadingPane label="Loading lakes…"/>}
          {error   && <ErrorPane message={error}/>}
          {lakes   && <IndiaMap lakes={lakes}/>}
        </Card>

        <Card style={{ overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)' }}>
            <div style={{ fontSize: 11, fontWeight: 700, marginBottom: 2 }}>Lakes Ranked by AI Risk</div>
            <div style={{ fontSize: 9, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>Click any row → full AI dashboard</div>
          </div>
          {loading && <LoadingPane/>}
          {error   && <ErrorPane message={error}/>}
          {sorted.length > 0 && (
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 90px 80px', gap: 8, padding: '8px 14px', fontSize: 8, fontWeight: 700, letterSpacing: '.1em', color: 'rgba(180,230,248,0.35)', borderBottom: '1px solid rgba(0,210,255,0.06)' }}>
                <span>LAKE / STATE</span><span>RISK</span><span>STATUS</span>
              </div>
              {sorted.map(lake => {
                const score = lake.risk_score ?? 0
                const col   = riskColor(score)
                return (
                  <div key={lake.id}
                    onClick={() => navigate(`/lake/${lake.id}`)}
                    style={{ display: 'grid', gridTemplateColumns: '1fr 90px 80px', gap: 8, padding: '10px 14px', borderBottom: '1px solid rgba(0,210,255,0.07)', cursor: 'pointer', transition: 'background .15s' }}
                    onMouseEnter={e=>e.currentTarget.style.background='rgba(0,210,255,0.04)'}
                    onMouseLeave={e=>e.currentTarget.style.background='transparent'}>
                    <div>
                      <div style={{ fontSize: 11, fontWeight: 700 }}>{lake.name}</div>
                      <div style={{ fontSize: 9, color: 'var(--muted)' }}>{lake.state || lake.region}</div>
                    </div>
                    <div style={{ fontSize: 13, fontWeight: 800, color: col, fontFamily: 'var(--mono)', alignSelf: 'center' }}>{fmtPct(score)}</div>
                    <div style={{ alignSelf: 'center' }}><RiskBadge score={score}/></div>
                  </div>
                )
              })}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
