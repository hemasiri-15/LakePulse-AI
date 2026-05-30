import { useState } from 'react'
import { useReports } from '../hooks/useData'
import { reportsAPI } from '../api/client'
import { Card, SectionLabel, LoadingPane, ErrorPane, StatusBadge, EmptyState } from '../components/ui'
import { fmtDate } from '../utils/helpers'

export default function ReportsPage() {
  const { data: reports, loading, error, refetch } = useReports()
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({ title: '', lake_id: '', report_type: 'weekly' })

  const create = async e => {
    e.preventDefault(); setCreating(true)
    try { await reportsAPI.create(form); await refetch(); setForm({ title: '', lake_id: '', report_type: 'weekly' }) }
    catch {}
    finally { setCreating(false) }
  }

  const updateStatus = async (id, status) => {
    try { await reportsAPI.updateStatus(id, status); await refetch() }
    catch {}
  }

  return (
    <div style={{ padding: 28 }}>
      <SectionLabel>📋 Reports</SectionLabel>
      <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 20 }}>Report Management</h1>

      {/* New report form */}
      <Card style={{ padding: 20, marginBottom: 20 }}>
        <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 14 }}>Generate New Report</div>
        <form onSubmit={create} style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ flex: 2, minWidth: 160 }}>
            <label style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: '.1em', display: 'block', marginBottom: 4 }}>TITLE</label>
            <input value={form.title} onChange={e=>setForm(f=>({...f,title:e.target.value}))} required placeholder="Weekly report…"
              style={{ width: '100%', background: 'rgba(0,0,0,0.35)', border: '1px solid var(--border)', borderRadius: 7, padding: '7px 11px', color: '#d8f0f8', fontFamily: 'var(--mono)', fontSize: 11, outline: 'none' }}/>
          </div>
          <div style={{ flex: 1, minWidth: 120 }}>
            <label style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: '.1em', display: 'block', marginBottom: 4 }}>LAKE ID</label>
            <input value={form.lake_id} onChange={e=>setForm(f=>({...f,lake_id:e.target.value}))} placeholder="bellandur"
              style={{ width: '100%', background: 'rgba(0,0,0,0.35)', border: '1px solid var(--border)', borderRadius: 7, padding: '7px 11px', color: '#d8f0f8', fontFamily: 'var(--mono)', fontSize: 11, outline: 'none' }}/>
          </div>
          <div style={{ flex: 1, minWidth: 110 }}>
            <label style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: '.1em', display: 'block', marginBottom: 4 }}>TYPE</label>
            <select value={form.report_type} onChange={e=>setForm(f=>({...f,report_type:e.target.value}))}
              style={{ width: '100%', background: 'rgba(0,0,0,0.55)', border: '1px solid var(--border)', borderRadius: 7, padding: '7px 11px', color: '#d8f0f8', fontFamily: 'var(--mono)', fontSize: 11, outline: 'none' }}>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="incident">Incident</option>
              <option value="satellite">Satellite</option>
            </select>
          </div>
          <button type="submit" disabled={creating}
            style={{ padding: '8px 16px', borderRadius: 7, border: 'none', cursor: 'pointer', background: 'linear-gradient(135deg,#007a87,#00d2ff)', color: '#03090f', fontWeight: 800, fontSize: 11, fontFamily: 'inherit', opacity: creating?.6:1 }}>
            {creating ? '…' : '+ Create'}
          </button>
        </form>
      </Card>

      {loading && <LoadingPane label="Loading reports…"/>}
      {error   && <ErrorPane message={error}/>}
      {!loading && reports?.length === 0 && <EmptyState icon="📋" title="No reports yet" sub="Generate your first report above."/>}

      {reports?.map(r => (
        <Card key={r.id} style={{ padding: '13px 16px', marginBottom: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
                <StatusBadge status={r.status}/>
                <span style={{ fontSize: 9, background: 'rgba(0,210,255,0.08)', border: '1px solid rgba(0,210,255,0.15)', borderRadius: 4, padding: '1px 6px', color: 'rgba(0,210,255,0.7)' }}>{r.report_type}</span>
                {r.lake_id && <span style={{ fontSize: 9, color: 'var(--muted)' }}>📍 {r.lake_id}</span>}
              </div>
              <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 3 }}>{r.title}</div>
              <div style={{ fontSize: 10, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>{fmtDate(r.created_at)}</div>
            </div>
            <div style={{ display: 'flex', gap: 6 }}>
              {r.status === 'pending' && <SmBtn label="Approve" color="#2ed573" onClick={() => updateStatus(r.id, 'approved')}/>}
              {r.status !== 'archived' && <SmBtn label="Archive" color="var(--muted)" onClick={() => updateStatus(r.id, 'archived')}/>}
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

function SmBtn({ label, color, onClick }) {
  return (
    <button onClick={onClick}
      style={{ padding: '4px 10px', borderRadius: 6, border: `1px solid ${color}44`, background: `${color}10`, color, fontSize: 10, fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit' }}>
      {label}
    </button>
  )
}
