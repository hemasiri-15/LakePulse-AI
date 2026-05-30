import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../api/client'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('lp_token')
    if (!token) { setLoading(false); return }
    authAPI.me()
      .then(r => setUser(r.data))
      .catch(() => localStorage.removeItem('lp_token'))
      .finally(() => setLoading(false))
  }, [])

  const login = async (username, password) => {
    const r = await authAPI.login(username, password)
    localStorage.setItem('lp_token', r.data.access_token)
    const me = await authAPI.me()
    setUser(me.data)
  }

  const logout = () => {
    localStorage.removeItem('lp_token')
    setUser(null)
  }

  return (
    <Ctx.Provider value={{ user, loading, login, logout }}>
      {children}
    </Ctx.Provider>
  )
}

export const useAuth = () => useContext(Ctx)
