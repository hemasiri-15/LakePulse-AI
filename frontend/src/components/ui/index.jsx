import { riskColor, riskLabel, riskBg, riskBorder, SEV_META, statusColors, fmtPct } from '../../utils/helpers'

export function Card({ children, className = '', style = {} }) {
  return (
    <div className={`card ${className}`} style={style}>
      {children}
    </div>
  )
}

export function Badge({ color, bg, border, children, style = {} }) {
  return (
    <span style={{
      fontSize: 9, fontWeight: 700, letterSpacing: '.1em',
      padding: '2px 8px', borderRadius: 10,
      color, background: bg || `${color}18`,
      border: `1px solid ${border || color + '44'}`,
      ...style,
    }}>
      {children}
    </span>
  )
}

export function RiskBadge({ score }) {
  const col = riskColor(score)
  return <Badge color={col} bg={riskBg(score)} border={riskBorder(score)}>{riskLabel(score)}</Badge>
}

export function SevBadge({ level }) {
  const m = SEV_META[level] ?? SEV_META.info
  return <Badge color={m.text} bg={m.bg} border={m.border}>{m.label}</Badge>
}

export function StatusBadge({ status }) {
  const col = statusColors[status] ?? '#64748b'
  return <Badge color={col}>{status?.toUpperCase()}</Badge>
}

export function Spinner({ size = 20 }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%',
      border: `2px solid rgba(0,210,255,0.15)`,
      borderTopColor: '#00d2ff',
      animation: 'spin .75s linear infinite',
      flexShrink: 0,
    }} />
  )
}

export function LoadingPane({ label = 'Loading…' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 48, gap: 12, color: 'var(--muted)' }}>
      <Spinner size={28} />
      <span style={{ fontSize: 11, fontFamily: 'var(--mono)' }}>{label}</span>
    </div>
  )
}

export function ErrorPane({ message }) {
  return (
    <div style={{ padding: 24, borderRadius: 10, background: 'rgba(255,71,87,.08)', border: '1px solid rgba(255,71,87,.25)', color: '#ff4757', fontSize: 12 }}>
      ⚠ {message}
    </div>
  )
}

export function EmptyState({ icon = '🔍', title, sub }) {
  return (
    <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--muted)' }}>
      <div style={{ fontSize: 32, marginBottom: 10 }}>{icon}</div>
      <div style={{ fontWeight: 700, marginBottom: 4 }}>{title}</div>
      {sub && <div style={{ fontSize: 11 }}>{sub}</div>}
    </div>
  )
}

export function SectionLabel({ children }) {
  return (
    <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.2em', textTransform: 'uppercase', color: 'var(--cyan)', marginBottom: 6 }}>
      {children}
    </div>
  )
}

export function StatTile({ label, value, color = 'var(--cyan)', icon, sub }) {
  return (
    <Card style={{ padding: '14px 16px', textAlign: 'center' }}>
      {icon && <div style={{ fontSize: 20, marginBottom: 4 }}>{icon}</div>}
      <div style={{ fontSize: 24, fontWeight: 800, color, fontFamily: 'var(--mono)', lineHeight: 1 }}>{value ?? '—'}</div>
      <div style={{ fontSize: 9, color: 'var(--muted)', marginTop: 4, letterSpacing: '.05em' }}>{label}</div>
      {sub && <div style={{ fontSize: 9, color, marginTop: 2 }}>{sub}</div>}
    </Card>
  )
}

export function RiskRing({ label, value, std, isRisk = true, isOk }) {
  const pct   = isRisk ? value : null
  const col   = isRisk
    ? (pct > .80 ? '#ff4757' : pct > .55 ? '#ffa502' : '#2ed573')
    : (isOk ? '#2ed573' : '#ff4757')
  const badgeLabel = isRisk
    ? (pct > .80 ? 'CRITICAL' : pct > .55 ? 'HIGH' : 'STABLE')
    : (isOk ? 'SAFE' : 'ALERT')
  const r = 30, sw = 6, circ = 2 * Math.PI * r
  const offset = isRisk ? circ * (1 - (value || 0)) : circ * (isOk ? 0.1 : 0.9)
  const display = isRisk ? fmtPct(value) : (value != null ? value.toFixed(1) : '—')

  return (
    <Card style={{ padding: '18px', textAlign: 'center' }}>
      <div style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: '.1em', marginBottom: 8 }}>{label}</div>
      <svg width="74" height="74" style={{ display: 'block', margin: '0 auto 8px', filter: `drop-shadow(0 0 10px ${col}55)` }}>
        <circle cx="37" cy="37" r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth={sw} />
        <circle cx="37" cy="37" r={r} fill="none" stroke={col} strokeWidth={sw}
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          transform="rotate(-90 37 37)" style={{ transition: 'stroke-dashoffset 1.1s ease' }} />
        <text x="37" y="33" textAnchor="middle" style={{ fill: col, fontSize: 13, fontWeight: 800, fontFamily: 'var(--mono)' }}>{display}</text>
        {std != null && (
          <text x="37" y="47" textAnchor="middle" style={{ fill: 'rgba(180,230,248,0.35)', fontSize: 9, fontFamily: 'var(--mono)' }}>
            ±{isRisk ? Math.round(std * 100) + '%' : std.toFixed(2)}
          </text>
        )}
      </svg>
      <Badge color={col} bg={`${col}18`} border={`${col}33`}>{badgeLabel}</Badge>
    </Card>
  )
}
