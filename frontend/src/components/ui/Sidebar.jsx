import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const NAV = [
  { to: '/',           icon: '🗺️', label: 'National Grid' },
  { to: '/alerts',     icon: '🔔', label: 'Alerts' },
  { to: '/satellite',  icon: '🛰️', label: 'Satellite' },
  { to: '/reports',    icon: '📋', label: 'Reports' },
  { to: '/admin',      icon: '⚙️', label: 'Admin',  adminOnly: true },
]

export default function Sidebar() {
  const { user, logout } = useAuth()

  return (
    <aside style={{
      width: 200, flexShrink: 0,
      background: 'rgba(3,9,15,.98)',
      borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column',
      position: 'fixed', left: 0, top: 0, bottom: 0, zIndex: 100,
    }}>
      {/* Logo */}
      <div style={{ padding: '16px 18px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
          <div style={{ width: 30, height: 30, borderRadius: 7, background: 'linear-gradient(135deg,#007a87,#00d2ff)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15 }}>💧</div>
          <div>
            <div style={{ fontWeight: 800, fontSize: 13, background: 'linear-gradient(90deg,var(--cyan),var(--lime))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              LakePulse<span style={{ color: 'var(--gold)', WebkitTextFillColor: 'var(--gold)' }}>AI</span>
            </div>
            <div style={{ fontSize: 7, color: 'var(--muted)', letterSpacing: '.15em' }}>INDIA · NATIONAL GRID</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '10px 8px', overflowY: 'auto' }}>
        {NAV.filter(n => !n.adminOnly || user?.is_admin).map(n => (
          <NavLink key={n.to} to={n.to} end={n.to === '/'}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '9px 12px', borderRadius: 8, marginBottom: 2,
              textDecoration: 'none', fontSize: 12, fontWeight: 600,
              background: isActive ? 'rgba(0,210,255,0.1)' : 'transparent',
              color: isActive ? 'var(--cyan)' : 'var(--muted)',
              borderLeft: isActive ? '2px solid var(--cyan)' : '2px solid transparent',
              transition: 'all .15s',
            })}>
            <span>{n.icon}</span>
            <span>{n.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* User footer */}
      <div style={{ padding: '12px 14px', borderTop: '1px solid var(--border)' }}>
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700 }}>{user.username || user.email}</div>
              <div style={{ fontSize: 9, color: 'var(--muted)' }}>{user.is_admin ? 'Admin' : 'Analyst'}</div>
            </div>
            <button onClick={logout} style={{ background: 'none', border: '1px solid var(--border)', borderRadius: 6, padding: '4px 8px', cursor: 'pointer', fontSize: 10, color: 'var(--muted)', fontFamily: 'inherit' }}>
              Out
            </button>
          </div>
        ) : (
          <NavLink to="/login" style={{ fontSize: 11, color: 'var(--cyan)', textDecoration: 'none' }}>Sign in →</NavLink>
        )}
      </div>
    </aside>
  )
}
