import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { riskColor } from '../../utils/helpers'

// SVG coordinate mapping for known lakes (viewBox 0 0 520 620)
const COORDS = {
  bellandur:      { x: 270, y: 420 },
  hussain_sagar:  { x: 268, y: 393 },
  chilika:        { x: 340, y: 338 },
  dal:            { x: 215, y: 62  },
  wular:          { x: 204, y: 57  },
  loktak:         { x: 398, y: 218 },
  vembanad:       { x: 234, y: 466 },
  pulicat:        { x: 294, y: 428 },
  sambhar:        { x: 194, y: 193 },
  pangong:        { x: 240, y: 72  },
  lonar:          { x: 243, y: 328 },
  nagarjuna_sagar:{ x: 276, y: 403 },
  kolleru:        { x: 300, y: 398 },
  gobind_sagar:   { x: 218, y: 104 },
  deepor_beel:    { x: 383, y: 174 },
  harike:         { x: 205, y: 127 },
  indira_sagar:   { x: 233, y: 276 },
  ashtamudi:      { x: 227, y: 474 },
  tso_moriri:     { x: 226, y: 84  },
  pushkar:        { x: 188, y: 199 },
}

function getCoords(lake) {
  const key = (lake.id || lake.lake_id || '').toLowerCase().replace(/\s+/g,'_')
  return COORDS[key] || { x: 260 + Math.random()*100 - 50, y: 300 + Math.random()*100 - 50 }
}

export default function IndiaMap({ lakes = [] }) {
  const navigate  = useNavigate()
  const [tooltip, setTooltip] = useState(null)  // { lake, mx, my }

  return (
    <div style={{ position: 'relative' }}>
      <svg viewBox="0 0 520 620" style={{ width: '100%', maxHeight: 520 }}>
        <defs>
          <radialGradient id="mg-red"   cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor="#ff4757" stopOpacity=".5"/><stop offset="100%" stopColor="#ff4757" stopOpacity="0"/></radialGradient>
          <radialGradient id="mg-amber" cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor="#ffa502" stopOpacity=".4"/><stop offset="100%" stopColor="#ffa502" stopOpacity="0"/></radialGradient>
          <radialGradient id="mg-lime"  cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor="#2ed573" stopOpacity=".35"/><stop offset="100%" stopColor="#2ed573" stopOpacity="0"/></radialGradient>
          <radialGradient id="mg-gold"  cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor="#ffd32a" stopOpacity=".4"/><stop offset="100%" stopColor="#ffd32a" stopOpacity="0"/></radialGradient>
        </defs>

        {/* India outline */}
        <path d="M180,28 L195,22 L215,18 L238,20 L258,16 L278,20 L295,18 L315,22 L330,28
                 L345,40 L358,55 L368,72 L372,90 L378,108 L388,122 L398,138 L408,155
                 L415,172 L418,190 L422,210 L426,228 L428,248 L430,268 L428,288 L424,308
                 L418,325 L410,340 L400,352 L388,362 L376,370 L365,380 L355,392 L348,405
                 L342,418 L338,432 L335,446 L332,460 L328,472 L322,482 L314,490 L304,496
                 L293,500 L282,502 L271,498 L262,490 L255,480 L250,468 L246,456 L242,444
                 L238,432 L232,420 L225,408 L217,398 L208,390 L198,382 L188,372 L179,360
                 L170,348 L162,335 L155,320 L149,305 L143,290 L138,274 L134,258 L130,242
                 L127,225 L125,208 L124,191 L124,174 L126,157 L129,140 L133,124 L138,108
                 L144,93 L151,79 L160,66 L170,53 Z"
              fill="rgba(0,180,220,0.04)" stroke="rgba(0,210,255,0.22)" strokeWidth="1.2"/>
        <path d="M215,18 L205,12 L195,8 L185,10 L178,18 L180,28 L195,22 Z"
              fill="rgba(0,180,220,0.04)" stroke="rgba(0,210,255,0.18)" strokeWidth="1"/>
        <path d="M395,155 L408,148 L422,145 L432,150 L438,162 L435,175 L425,180 L415,172 L408,155 Z"
              fill="rgba(0,180,220,0.04)" stroke="rgba(0,210,255,0.18)" strokeWidth="1"/>
        {/* Grid */}
        {[150,250,350].map(y=><line key={y} x1="120" y1={y} x2="440" y2={y} stroke="rgba(0,210,255,0.04)" strokeWidth=".5"/>)}
        {[200,300,390].map(x=><line key={x} x1={x} y1="20"  x2={x} y2="510" stroke="rgba(0,210,255,0.04)" strokeWidth=".5"/>)}

        {/* Lake nodes */}
        {lakes.map(lake => {
          const { x, y } = getCoords(lake)
          const score = lake.risk_score ?? lake.bloom_risk ?? (1 - ((lake.health_score || 0) / 100))
          const col   = riskColor(score)
          const glowId = score>.7?'mg-red':score>.6?'mg-amber':score>.4?'mg-gold':'mg-lime'
          const r = score>.7?7:score>.4?6:5
          return (
            <g key={lake.id || lake.lake_id}
               style={{ cursor: 'pointer' }}
               onClick={() => navigate(`/lake/${lake.id || lake.lake_id}`)}
               onMouseEnter={e => setTooltip({ lake, mx: e.clientX, my: e.clientY })}
               onMouseMove={e  => setTooltip(t => t ? { ...t, mx: e.clientX, my: e.clientY } : null)}
               onMouseLeave={()=> setTooltip(null)}>
              <circle cx={x} cy={y} r={r+14} fill={`url(#${glowId})`} opacity=".7"/>
              <circle cx={x} cy={y} r={r+5}  fill="none" stroke={col} strokeWidth="1" opacity=".4"
                style={score>.7?{animation:'pulse 1.8s infinite'}:{}}/>
              <circle cx={x} cy={y} r={r}    fill={col} opacity=".93" stroke="rgba(3,9,15,.6)" strokeWidth="1.2"/>
            </g>
          )
        })}
      </svg>

      {/* Floating tooltip */}
      {tooltip && (
        <div style={{
          position: 'fixed', left: tooltip.mx+14, top: tooltip.my-10,
          background: 'rgba(4,14,26,.97)', border: '1px solid var(--border)',
          borderRadius: 8, padding: '10px 14px', zIndex: 9999,
          minWidth: 170, boxShadow: '0 8px 32px rgba(0,0,0,.5)',
          pointerEvents: 'none',
        }}>
          {(() => {
            const { lake } = tooltip
            const score = lake.risk_score ?? lake.bloom_risk ?? 0
            const col   = riskColor(score)
            return <>
              <div style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: '.1em', marginBottom: 4 }}>
                {(lake.state || lake.region || '').toUpperCase()}
              </div>
              <div style={{ fontSize: 13, fontWeight: 800, marginBottom: 6 }}>{lake.name}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span style={{ fontSize: 18, fontWeight: 800, color: col, fontFamily: 'var(--mono)' }}>
                  {Math.round(score * 100)}%
                </span>
                <span style={{ fontSize: 9, fontWeight: 700, color: col, background: `${col}18`, border: `1px solid ${col}33`, borderRadius: 8, padding: '2px 7px' }}>
                  {score>.8?'CRITICAL':score>.6?'HIGH':score>.4?'MODERATE':'STABLE'}
                </span>
              </div>
              <div style={{ fontSize: 9, color: 'rgba(180,230,248,0.5)' }}>Click to open full AI analysis →</div>
            </>
          })()}
        </div>
      )}

      {/* Legend */}
      <div style={{ display: 'flex', gap: 16, marginTop: 10, fontSize: 9, fontFamily: 'var(--mono)', color: 'rgba(180,230,248,0.4)', flexWrap: 'wrap' }}>
        {[['#ff4757','Critical'],['#ffa502','High'],['#ffd32a','Moderate'],['#2ed573','Stable']].map(([c,l])=>(
          <span key={l} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: c, display: 'inline-block' }}/>
            {l}
          </span>
        ))}
      </div>
    </div>
  )
}
