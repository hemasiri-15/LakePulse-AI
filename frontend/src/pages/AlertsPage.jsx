import { useState } from 'react'
import { useAlerts } from '../hooks/useData'
import { alertsAPI } from '../api/client'
import { Card, SectionLabel, LoadingPane, ErrorPane, SevBadge, StatusBadge, EmptyState } from '../components/ui'
import { fmtDate } from '../utils/helpers'

export default function AlertsPage() {
  const [filter, setFilter] = useState('all')
  const { data: alerts, loading, error, refetch } = useAlerts(filter !== 'all' ? { status: filter } : {})
  const [busy, setBusy] = useState({})

  const act = async (fn, id) => {
    setBusy(b => ({ ...b, [id]: true }))
    try { await fn(id); await refetch() }
    catch {}
    finally { setBusy(b => ({ ...b, [id]: false })) }
  }

  const FILTERS = ['all','open','escalated','resolved']

  return (
    <div style={{ padding: 28 }}>
      <SectionLabel>🔔 Active Alerts</SectionLabel>
      <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 6 }}>Alert Management</h1>
      <p style={{ fontSize: 11, color: 'var(--muted)', marginBottom: 20 }}>
        AI-generated alerts from bloom risk, sensor anomalies, and satellite triggers.
      </p>

      {/* Satellite alerts inline */}
      <SatelliteAlertsBar />

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 18 }}>
        {FILTERS.map(f => (
          <button key={f} onClick={() => setFilter(f)}
            style={{ padding: '6px 14px', borderRadius: 20, border: `1px solid ${filter===f ? 'var(--cyan)' : 'var(--border)'}`, background: filter===f ? 'rgba(0,210,255,0.1)' : 'transparent', color: filter===f ? 'var(--cyan)' : 'var(--muted)', fontSize: 11, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
            {f.charAt(0).toUpperCase()+f.slice(1)}
          </button>
        ))}
      </div>

      {loading && <LoadingPane label="Loading alerts…"/>}
      {error   && <ErrorPane message={error}/>}
      {!loading && alerts?.length === 0 && <EmptyState icon="✅" title="No alerts" sub="All clear for the selected filter."/>}

      {alerts?.map(alert => (
        <Card key={alert.id} style={{ padding: '14px 16px', marginBottom: 10, borderLeft: `3px solid ${alert.severity==='critical'?'#ff4757':alert.severity==='high'?'#ffa502':'#a29bfe'}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 10 }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5, flexWrap: 'wrap' }}>
                <SevBadge level={alert.severity}/>
                <StatusBadge status={alert.status}/>
                {alert.lake_name && <span style={{ fontSize: 10, color: 'var(--muted)' }}>📍 {alert.lake_name}</span>}
              </div>
              <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 3 }}>{alert.message || alert.title}</div>
              <div style={{ fontSize: 10, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>{fmtDate(alert.created_at)}</div>
              {alert.parameter && <div style={{ fontSize: 10, color: 'rgba(180,230,248,0.5)', marginTop: 3 }}>Parameter: {alert.parameter} · Value: {alert.value}</div>}
            </div>
            <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
              {alert.status === 'open' && (
                <ActionBtn label="Escalate" color="#ff4757" loading={busy[alert.id]} onClick={() => act(alertsAPI.escalate, alert.id)}/>
              )}
              {alert.status !== 'resolved' && (
                <ActionBtn label="Resolve" color="#2ed573" loading={busy[alert.id]} onClick={() => act(alertsAPI.resolve, alert.id)}/>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

function ActionBtn({ label, color, loading, onClick }) {
  return (
    <button onClick={e => { e.stopPropagation(); onClick() }} disabled={loading}
      style={{ padding: '5px 12px', borderRadius: 7, border: `1px solid ${color}44`, background: `${color}10`, color, fontSize: 10, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', opacity: loading ? .5 : 1 }}>
      {loading ? '…' : label}
    </button>
  )
}

function SatelliteAlertsBar() {
  const { data } = useAlerts({ source: 'satellite' })
  if (!data?.length) return null
  return (
    <div style={{ background: 'rgba(255,165,2,0.07)', border: '1px solid rgba(255,165,2,0.2)', borderRadius: 10, padding: '10px 14px', marginBottom: 16 }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: '#ffa502', marginBottom: 6 }}>🛰️ SATELLITE ALERTS ({data.length})</div>
      {data.slice(0,3).map(a => (
        <div key={a.id} style={{ fontSize: 11, color: 'rgba(180,230,248,0.75)', marginBottom: 3 }}>• {a.message || a.title}</div>
      ))}
    </div>
  )
}
