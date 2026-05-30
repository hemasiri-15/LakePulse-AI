import { useState } from 'react'
import { useAdminStats } from '../hooks/useData'
import { adminAPI } from '../api/client'
import { Card, SectionLabel, StatTile, LoadingPane, ErrorPane } from '../components/ui'
import { fmtDate } from '../utils/helpers'

export default function AdminPage() {
  const { data: stats, loading, error, refetch } = useAdminStats()
  const [busy, setBusy] = useState({})
  const [msg,  setMsg]  = useState('')

  const run = async (key, fn, label) => {
    setBusy(b => ({ ...b, [key]: true })); setMsg('')
    try { await fn(); setMsg(`✅ ${label} complete`); refetch() }
    catch(e) { setMsg(`❌ ${e.response?.data?.detail || e.message}`) }
    finally   { setBusy(b => ({ ...b, [key]: false })) }
  }

  return (
    <div style={{ padding: 28 }}>
      <SectionLabel>⚙️ Admin</SectionLabel>
      <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 20 }}>Platform Administration</h1>

      {loading && <LoadingPane label="Loading stats…"/>}
      {error   && <ErrorPane message={error}/>}

      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(130px,1fr))', gap: 12, marginBottom: 24 }}>
          <StatTile label="Total Lakes"   value={stats.total_lakes}   color="var(--cyan)"/>
          <StatTile label="Total Sensors" value={stats.total_sensors} color="#a29bfe"/>
          <StatTile label="Total Alerts"  value={stats.total_alerts}  color="#ff4757"/>
          <StatTile label="Total Reports" value={stats.total_reports} color="#ffa502"/>
          <StatTile label="Predictions"   value={stats.total_predictions} color="#2ed573"/>
          {stats.last_updated && <StatTile label="Last Updated" value={fmtDate(stats.last_updated)} color="var(--muted)"/>}
        </div>
      )}

      <Card style={{ padding: 20 }}>
        <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 16 }}>Admin Actions</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <AdminAction icon="🌱" label="Seed Database" desc="Populate lake and sensor data with sample records" busy={busy.seed}     onClick={() => run('seed',         adminAPI.seed,         'Seed')}/>
          <AdminAction icon="📊" label="Seed Readings" desc="Generate synthetic sensor readings for all lakes"   busy={busy.readings} onClick={() => run('readings',     adminAPI.seedReadings,  'Readings seeded')}/>
          <AdminAction icon="🔄" label="Score All Lakes" desc="Re-run AI risk scoring across all lake records"   busy={busy.score}    onClick={() => run('score',        adminAPI.scoreAll,      'All lakes scored')}/>
        </div>
        {msg && <div style={{ marginTop: 14, fontSize: 11, color: msg.startsWith('✅') ? '#2ed573' : '#ff4757', fontFamily: 'var(--mono)', background: 'rgba(255,255,255,0.03)', borderRadius: 7, padding: '8px 12px' }}>{msg}</div>}
      </Card>
    </div>
  )
}

function AdminAction({ icon, label, desc, busy, onClick }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: 8, border: '1px solid var(--border)', gap: 12, flexWrap: 'wrap' }}>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flex: 1 }}>
        <span style={{ fontSize: 20 }}>{icon}</span>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700 }}>{label}</div>
          <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 2 }}>{desc}</div>
        </div>
      </div>
      <button onClick={onClick} disabled={busy}
        style={{ padding: '7px 16px', borderRadius: 7, border: '1px solid var(--border)', background: 'rgba(0,210,255,0.07)', color: 'var(--cyan)', fontSize: 11, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit', opacity: busy ? .5 : 1, flexShrink: 0 }}>
        {busy ? 'Running…' : 'Run'}
      </button>
    </div>
  )
}
