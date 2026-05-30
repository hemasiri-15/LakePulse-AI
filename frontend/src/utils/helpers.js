export const riskColor = r => {
  if (r == null) return '#64748b'
  if (r > 0.80) return '#ff4757'
  if (r > 0.60) return '#ffa502'
  if (r > 0.40) return '#ffd32a'
  return '#2ed573'
}

export const riskLabel = r => {
  if (r == null) return 'UNKNOWN'
  if (r > 0.80) return 'CRITICAL'
  if (r > 0.60) return 'HIGH'
  if (r > 0.40) return 'MODERATE'
  return 'STABLE'
}

export const riskBg = r => `${riskColor(r)}18`
export const riskBorder = r => `${riskColor(r)}44`

export const fmtPct  = v => v != null ? `${Math.round(v * 100)}%` : '—'
export const fmtNum  = (v, d = 1) => v != null ? v.toFixed(d) : '—'
export const fmtDate = s => s ? new Date(s).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : '—'
export const fmtDateShort = s => s ? new Date(s).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }) : '—'

export const SEV_META = {
  critical: { bg: 'rgba(255,71,87,.12)',   border: 'rgba(255,71,87,.35)',   text: '#ff4757', label: 'CRITICAL' },
  high:     { bg: 'rgba(255,165,2,.1)',    border: 'rgba(255,165,2,.3)',    text: '#ffa502', label: 'HIGH'     },
  moderate: { bg: 'rgba(162,155,254,.1)',  border: 'rgba(162,155,254,.28)', text: '#a29bfe', label: 'MODERATE' },
  low:      { bg: 'rgba(46,213,115,.08)',  border: 'rgba(46,213,115,.22)',  text: '#2ed573', label: 'LOW'      },
  info:     { bg: 'rgba(0,210,255,.06)',   border: 'rgba(0,210,255,.2)',    text: '#00d2ff', label: 'INFO'     },
}

export const statusColors = {
  open:       '#ffa502',
  escalated:  '#ff4757',
  resolved:   '#2ed573',
  pending:    '#a29bfe',
  active:     '#00d2ff',
}
