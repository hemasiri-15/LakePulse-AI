import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { fmtDateShort } from '../../utils/helpers'

const PARAMS = [
  { key: 'dissolved_oxygen', label: 'DO (mg/L)',  color: '#00d2ff', safe: [5, 12] },
  { key: 'ph',               label: 'pH',          color: '#2ed573', safe: [6.5, 8.5] },
  { key: 'temperature',      label: 'Temp (°C)',   color: '#ffa502', safe: [20, 30] },
  { key: 'turbidity',        label: 'Turbidity (NTU)', color: '#a29bfe', safe: [0, 10] },
  { key: 'chlorophyll_a',    label: 'Chl-a (μg/L)',color: '#7bed9f', safe: [0, 25] },
]

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: 'rgba(4,14,26,.97)', border: '1px solid var(--border)', borderRadius: 8, padding: '8px 12px', fontSize: 10, fontFamily: 'var(--mono)' }}>
      <div style={{ color: 'var(--muted)', marginBottom: 4 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ color: p.color }}>{p.name}: {p.value?.toFixed(2)}</div>
      ))}
    </div>
  )
}

export default function SensorChart({ data = [], activeParam = 'dissolved_oxygen' }) {
  const param  = PARAMS.find(p => p.key === activeParam) || PARAMS[0]
  const chartData = data.map(r => ({
    date: fmtDateShort(r.timestamp || r.recorded_at),
    [param.label]: r[param.key],
  }))

  return (
    <div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <XAxis dataKey="date" tick={{ fill: 'rgba(180,230,248,0.35)', fontSize: 9 }} axisLine={false} tickLine={false}/>
          <YAxis tick={{ fill: 'rgba(180,230,248,0.35)', fontSize: 9 }} axisLine={false} tickLine={false} width={36}/>
          <Tooltip content={<CustomTooltip />} />
          {param.safe && <>
            <ReferenceLine y={param.safe[0]} stroke={`${param.color}30`} strokeDasharray="4 4"/>
            <ReferenceLine y={param.safe[1]} stroke={`${param.color}30`} strokeDasharray="4 4"/>
          </>}
          <Line type="monotone" dataKey={param.label} stroke={param.color} strokeWidth={2} dot={false} activeDot={{ r: 4, fill: param.color }}/>
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export { PARAMS }
