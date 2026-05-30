import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function LoginPage() {
  const { login }    = useAuth()
  const navigate     = useNavigate()
  const [u, setU]    = useState('')
  const [p, setP]    = useState('')
  const [err, setErr]= useState('')
  const [busy, setBusy] = useState(false)

  const submit = async e => {
    e.preventDefault(); setBusy(true); setErr('')
    try { await login(u, p); navigate('/') }
    catch { setErr('Invalid credentials — check username and password.') }
    finally { setBusy(false) }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div style={{ width: '100%', maxWidth: 360 }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: 'linear-gradient(135deg,#007a87,#00d2ff)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, margin: '0 auto 12px' }}>💧</div>
          <div style={{ fontWeight: 800, fontSize: 22, background: 'linear-gradient(90deg,var(--cyan),var(--lime))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>LakePulse AI</div>
          <div style={{ fontSize: 10, color: 'var(--muted)', letterSpacing: '.18em', marginTop: 2 }}>NATIONAL LAKE INTELLIGENCE PLATFORM</div>
        </div>

        <div className="card" style={{ padding: 28 }}>
          <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div>
              <label style={{ fontSize: 10, color: 'var(--muted)', letterSpacing: '.1em', display: 'block', marginBottom: 5 }}>USERNAME</label>
              <input value={u} onChange={e=>setU(e.target.value)} required
                style={{ width: '100%', background: 'rgba(0,0,0,0.35)', border: '1px solid var(--border)', borderRadius: 7, padding: '9px 12px', color: '#d8f0f8', fontFamily: 'var(--mono)', fontSize: 12, outline: 'none' }}/>
            </div>
            <div>
              <label style={{ fontSize: 10, color: 'var(--muted)', letterSpacing: '.1em', display: 'block', marginBottom: 5 }}>PASSWORD</label>
              <input type="password" value={p} onChange={e=>setP(e.target.value)} required
                style={{ width: '100%', background: 'rgba(0,0,0,0.35)', border: '1px solid var(--border)', borderRadius: 7, padding: '9px 12px', color: '#d8f0f8', fontFamily: 'var(--mono)', fontSize: 12, outline: 'none' }}/>
            </div>
            {err && <div style={{ fontSize: 11, color: '#ff4757', background: 'rgba(255,71,87,.08)', borderRadius: 6, padding: '8px 10px' }}>{err}</div>}
            <button type="submit" disabled={busy}
              style={{ padding: '10px', borderRadius: 8, border: 'none', cursor: 'pointer', background: 'linear-gradient(135deg,#007a87,#00d2ff)', color: '#03090f', fontWeight: 800, fontSize: 13, fontFamily: 'inherit', opacity: busy ? .6 : 1 }}>
              {busy ? 'Signing in…' : 'Sign In →'}
            </button>
          </form>
        </div>
        <div style={{ textAlign: 'center', marginTop: 12, fontSize: 10, color: 'var(--muted)' }}>
          Use your LakePulse admin credentials
        </div>
      </div>
    </div>
  )
}
