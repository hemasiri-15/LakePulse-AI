import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth'
import Sidebar from './components/ui/Sidebar'
import NationalGrid  from './pages/NationalGrid'
import LakeDetail    from './pages/LakeDetail'
import AlertsPage    from './pages/AlertsPage'
import SatellitePage from './pages/SatellitePage'
import ReportsPage   from './pages/ReportsPage'
import AdminPage     from './pages/AdminPage'
import LoginPage     from './pages/LoginPage'
import { Spinner }   from './components/ui'

function Layout() {
  const { user, loading } = useAuth()
  if (loading) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Spinner size={32}/>
    </div>
  )

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar/>
      <main style={{ flex: 1, marginLeft: 200, minHeight: '100vh', overflowY: 'auto' }}>
        <Routes>
          <Route path="/"            element={<NationalGrid/>}/>
          <Route path="/lake/:lakeId" element={<LakeDetail/>}/>
          <Route path="/alerts"       element={<AlertsPage/>}/>
          <Route path="/satellite"    element={<SatellitePage/>}/>
          <Route path="/reports"      element={<ReportsPage/>}/>
          <Route path="/admin"        element={user?.is_admin ? <AdminPage/> : <Navigate to="/"/>}/>
          <Route path="/login"        element={<Navigate to="/"/>}/>
          <Route path="*"             element={<Navigate to="/"/>}/>
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage/>}/>
          <Route path="/*"     element={<Layout/>}/>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
