import { useState } from 'react'
import { SEV_META } from '../../utils/helpers'

export default function RecommendationCards({ recs = [] }) {
  const [expanded, setExpanded] = useState({})
  const toggle = id => setExpanded(e => ({ ...e, [id]: !e[id] }))

  if (!recs.length) return (
    <div style={{ textAlign: 'center', padding: 40, color: 'rgba(180,230,248,0.4)', fontSize: 12 }}>
      ✅ No critical actions triggered for this forecast.
    </div>
  )

  return (
    <div>
      {recs.map((r, idx) => {
        const sevKey = r.severity || r.sev || 'moderate'
        const s      = SEV_META[sevKey] ?? SEV_META.moderate
        const isExp  = expanded[r.id || idx]

        return (
          <div key={r.id || idx}
            onClick={() => toggle(r.id || idx)}
            style={{ background: s.bg, border: `1px solid ${s.border}`, borderLeft: `3px solid ${s.text}`, borderRadius: 10, padding: '12px 14px', marginBottom: 8, cursor: 'pointer', transition: 'background .15s' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', flex: 1 }}>
                <div style={{ width: 28, height: 28, borderRadius: 7, background: `${s.text}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, flexShrink: 0 }}>
                  {r.icon || '⚠'}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4, flexWrap: 'wrap' }}>
                    <span style={{ fontSize: 9, fontWeight: 700, color: s.text, letterSpacing: '.1em' }}>
                      #{(r.rank || idx+1)} · {s.label}
                    </span>
                    {(r.category || r.cat) && (
                      <span style={{ fontSize: 9, background: 'rgba(0,210,255,0.08)', border: '1px solid rgba(0,210,255,0.15)', borderRadius: 4, padding: '1px 6px', color: 'rgba(0,210,255,0.7)' }}>
                        {r.category || r.cat}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 700, lineHeight: 1.45 }}>{r.action}</div>
                </div>
              </div>
              <div style={{ fontSize: 14, color: 'rgba(180,230,248,0.3)', flexShrink: 0, transform: isExp ? 'rotate(180deg)' : 'none', transition: 'transform .2s' }}>▾</div>
            </div>

            {isExp && (
              <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.07)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 8 }}>
                <div>
                  <div style={{ fontSize: 9, color: 'rgba(180,230,248,0.4)', marginBottom: 3, letterSpacing: '.1em' }}>RATIONALE</div>
                  <div style={{ fontSize: 10, color: 'rgba(180,230,248,0.75)', lineHeight: 1.65 }}>{r.rationale}</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 7, padding: '9px 11px', border: '1px solid rgba(255,255,255,0.07)' }}>
                  <div style={{ fontSize: 9, color: 'rgba(180,230,248,0.4)', marginBottom: 4 }}>ESCALATE TO</div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: s.text, marginBottom: 6 }}>🏛️ {r.agency}</div>
                  <div style={{ fontSize: 9, color: 'rgba(180,230,248,0.4)', marginBottom: 2 }}>TIMELINE</div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: '#ffd32a' }}>⏱ {r.timeline}</div>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
