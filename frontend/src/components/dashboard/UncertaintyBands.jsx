const PARAMS = [
  { key: 'do_t7',         label: 'Dissolved O₂', unit: 'mg/L',  okRange: [5, 12],  color: '#00d2ff', icon: '💧' },
  { key: 'ph_t7',         label: 'pH Level',      unit: 'pH',    okRange: [6.5, 8.5], color: '#2ed573', icon: '⚗️' },
  { key: 'temp_t7',       label: 'Temperature',   unit: '°C',    okRange: [20, 30], color: '#ffa502', icon: '🌡️' },
  { key: 'turbidity_t7',  label: 'Turbidity',     unit: 'NTU',   okRange: [0, 10],  color: '#1e90ff', icon: '👁️' },
  { key: 'chl_a_t7',      label: 'Chl-a',         unit: 'μg/L',  okRange: [0, 25],  color: '#7bed9f', icon: '🌿' },
]

export default function UncertaintyBands({ prediction }) {
  if (!prediction) return null

  return (
    <div>
      <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 4 }}>90% Confidence Intervals · Monte Carlo Dropout</div>
      <div style={{ fontSize: 10, color: 'var(--muted)', lineHeight: 1.7, marginBottom: 18, maxWidth: 560 }}>
        Mean prediction (marker), ±std, and 5th–95th percentile from 50 stochastic forward passes.
        <span style={{ color: 'rgba(46,213,115,0.8)' }}> Green zone</span> is the safe environmental range.
      </div>
      {PARAMS.map(({ key, label, unit, okRange, color, icon }) => {
        const b = prediction[key]
        if (!b || b.mean == null) return null
        const [lo, hi] = okRange
        const isOk = b.mean >= lo && b.mean <= hi
        const sc = isOk ? '#2ed573' : '#ff4757'
        const ciL = b.ci_low  ?? (b.mean - b.std * 1.6)
        const ciH = b.ci_high ?? (b.mean + b.std * 1.6)
        const trackLo = Math.min(ciL * 0.82, lo * 0.82)
        const trackHi = Math.max(ciH * 1.18, hi * 1.18)
        const tp = v => Math.min(Math.max(((v - trackLo) / (trackHi - trackLo)) * 100, 1), 99)

        return (
          <div key={key} style={{ marginBottom: 18 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontSize: 11, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}>
                <span>{icon}</span><span>{label}</span>
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 12, color, fontWeight: 700, fontFamily: 'var(--mono)' }}>{b.mean.toFixed(1)} {unit}</span>
                <span style={{ fontSize: 9, color: 'rgba(180,230,248,0.4)', fontFamily: 'var(--mono)' }}>±{b.std?.toFixed(2)}</span>
                <span style={{ fontSize: 9, fontWeight: 700, padding: '1px 7px', borderRadius: 10, background: `${sc}18`, color: sc, border: `1px solid ${sc}44` }}>
                  {isOk ? 'SAFE' : 'ALERT'}
                </span>
              </div>
            </div>
            <div style={{ position: 'relative', height: 16, borderRadius: 8, background: 'rgba(255,255,255,0.05)' }}>
              {/* Safe zone */}
              <div style={{ position: 'absolute', top: 0, bottom: 0, borderRadius: 8, left: `${tp(lo)}%`, width: `${tp(hi)-tp(lo)}%`, background: 'rgba(46,213,115,0.07)', border: '1px solid rgba(46,213,115,0.15)' }}/>
              {/* CI band */}
              <div style={{ position: 'absolute', top: 3, bottom: 3, borderRadius: 4, left: `${tp(ciL)}%`, width: `${tp(ciH)-tp(ciL)}%`, background: `${color}20`, border: `1px solid ${color}40` }}/>
              {/* Mean marker */}
              <div style={{ position: 'absolute', top: -2, bottom: -2, width: 3, borderRadius: 2, left: `calc(${tp(b.mean)}% - 1.5px)`, background: color, boxShadow: `0 0 6px ${color}80` }}/>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 3, fontSize: 9, fontFamily: 'var(--mono)', color: 'rgba(180,230,248,0.3)' }}>
              <span>CI: {ciL.toFixed(1)}</span>
              <span>Safe: {lo}–{hi} {unit}</span>
              <span>{ciH.toFixed(1)}</span>
            </div>
          </div>
        )
      })}
    </div>
  )
}
