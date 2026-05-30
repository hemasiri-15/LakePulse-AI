import { useState, useEffect, useCallback } from 'react'
import {
  lakesAPI, sensorsAPI, predictionsAPI,
  alertsAPI, reportsAPI, satelliteAPI, adminAPI,
} from '../api/client'

// Generic fetch hook
function useFetch(fetcher, deps = []) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  const run = useCallback(async () => {
    setLoading(true); setError(null)
    try   { const r = await fetcher(); setData(r.data) }
    catch (e) { setError(e.response?.data?.detail || e.message) }
    finally   { setLoading(false) }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => { run() }, [run])
  return { data, loading, error, refetch: run }
}

// ── Lakes ──────────────────────────────────────────────────────────────────────
export const useLakes      = ()     => useFetch(() => lakesAPI.list())
export const useLake       = id     => useFetch(() => lakesAPI.get(id), [id])

// ── Sensors ───────────────────────────────────────────────────────────────────
export const useSensorLatest  = id  => useFetch(() => sensorsAPI.latest(id), [id])
export const useSensorHistory = (id, params) =>
  useFetch(() => sensorsAPI.history(id, params), [id, JSON.stringify(params)])

// ── Predictions ───────────────────────────────────────────────────────────────
export const usePrediction = id => useFetch(() => predictionsAPI.latest(id), [id])

// ── Alerts ────────────────────────────────────────────────────────────────────
export const useAlerts     = (params) => useFetch(() => alertsAPI.list(params), [JSON.stringify(params)])

// ── Reports ───────────────────────────────────────────────────────────────────
export const useReports    = (params) => useFetch(() => reportsAPI.list(params), [JSON.stringify(params)])

// ── Satellite ─────────────────────────────────────────────────────────────────
export const useSatelliteLatest   = id => useFetch(() => satelliteAPI.latest(id), [id])
export const useSatelliteShrinkage = id => useFetch(() => satelliteAPI.shrinkage(id), [id])
export const useSatelliteAlerts   = () => useFetch(() => satelliteAPI.alerts())

// ── Admin ─────────────────────────────────────────────────────────────────────
export const useAdminStats = () => useFetch(() => adminAPI.stats())
