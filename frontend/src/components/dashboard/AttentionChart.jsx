import { useEffect, useRef } from 'react'

function inferLabel(weights, idx) {
  const max  = Math.max(...weights)
  const norm = weights[idx] / max
  const dAgo = weights.length - 1 - idx
  if (norm < 0.75) return null
  if (norm > 0.92) return { text: '⚠ DO collapse',    color: '#ff4757' }
  if (norm > 0.82) return { text: dAgo>18 ? '⚠ Rainfall surge' : dAgo>8 ? '⚠ Sewage spike' : '⚠ Chl-a surge', color: '#ffa502' }
  return { text: '↑ High attention', color: '#ffd32a' }
}

export default function AttentionChart({ weights = [] }) {
  const canvasRef  = useRef(null)
  const wrapperRef = useRef(null)
  const animRef    = useRef(null)
  const tipRef     = useRef(null)

  useEffect(() => {
    if (!weights.length) return
    const canvas  = canvasRef.current
    const wrapper = wrapperRef.current
    if (!canvas) return

    if (animRef.current) { cancelAnimationFrame(animRef.current); animRef.current = null }
    wrapper.querySelectorAll('.ev-label').forEach(el => el.remove())

    canvas.width  = canvas.offsetWidth  * devicePixelRatio
    canvas.height = 190                 * devicePixelRatio
    const ctx = canvas.getContext('2d')
    ctx.scale(devicePixelRatio, devicePixelRatio)

    const W = canvas.offsetWidth, H = 190
    const PAD = { top: 44, right: 12, bottom: 34, left: 38 }
    const pW = W - PAD.left - PAD.right
    const pH = H - PAD.top  - PAD.bottom
    const n = weights.length, max = Math.max(...weights), bW = pW/n - 2

    function drawStatic() {
      ;[.25,.5,.75,1].forEach(f => {
        const y = PAD.top + pH*(1-f*.85)
        ctx.beginPath(); ctx.strokeStyle='rgba(0,210,255,0.06)'; ctx.lineWidth=.5
        ctx.moveTo(PAD.left,y); ctx.lineTo(W-PAD.right,y); ctx.stroke()
      })
      ctx.fillStyle='rgba(180,230,248,0.35)'; ctx.font='9px monospace'; ctx.textAlign='center'; ctx.textBaseline='top'
      ;[0,6,13,20,29].forEach(i => ctx.fillText(i===0?'−30d':i===29?'Today':`−${29-i}d`, PAD.left+i*(pW/n)+bW/2, PAD.top+pH+6))
      ctx.save(); ctx.translate(12,PAD.top+pH/2); ctx.rotate(-Math.PI/2)
      ctx.fillStyle='rgba(180,230,248,0.25)'; ctx.font='9px monospace'; ctx.textAlign='center'; ctx.textBaseline='middle'
      ctx.fillText('ATTENTION',0,0); ctx.restore()
    }

    const startTime = performance.now()
    const STAGGER = 18, RISE_MS = 340

    function frame(now) {
      ctx.clearRect(0,0,W,H); drawStatic()
      weights.forEach((w,i) => {
        const ease = 1-Math.pow(1-Math.min(Math.max(0,(now-startTime)-i*STAGGER)/RISE_MS,1),3)
        const norm = w/max, x = PAD.left+i*(pW/n)+1, bH = norm*pH*.85*ease, y = PAD.top+pH-bH
        const g = ctx.createLinearGradient(x,PAD.top+pH,x,PAD.top+pH-norm*pH*.85)
        g.addColorStop(0,'rgba(0,168,181,0.2)'); g.addColorStop(.55,norm>.7?'rgba(255,165,2,.8)':'rgba(0,210,255,.7)'); g.addColorStop(1,norm>.7?'#ffa502':'#00d2ff')
        ctx.fillStyle=g; ctx.beginPath()
        if (ctx.roundRect) ctx.roundRect(x,y,bW,bH,[2,2,0,0]); else ctx.rect(x,y,bW,bH)
        ctx.fill()
        if (norm>.75&&ease>=1) { ctx.fillStyle=norm>.9?'#ff4757':'#ffa502'; ctx.font='9px monospace'; ctx.textAlign='center'; ctx.textBaseline='bottom'; ctx.fillText('▲',x+bW/2,y-2) }
      })
      if (now-startTime < (n-1)*STAGGER+RISE_MS) animRef.current = requestAnimationFrame(frame)
      else { animRef.current=null; placeLabels() }
    }

    function placeLabels() {
      weights.forEach((w,i)=>{
        const ev=inferLabel(weights,i); if(!ev) return
        const norm=w/max, x=PAD.left+i*(pW/n)+bW/2, bH=norm*pH*.85, yTop=PAD.top+pH-bH
        const sx=canvas.offsetWidth/W, sy=(190)/(H)
        const el=document.createElement('div')
        el.className='ev-label'
        Object.assign(el.style,{position:'absolute',fontFamily:'monospace',fontSize:'8.5px',fontWeight:700,whiteSpace:'nowrap',pointerEvents:'none',padding:'2px 5px',borderRadius:'4px',transform:'translateX(-50%)',color:ev.color,background:`${ev.color}18`,border:`1px solid ${ev.color}44`,left:`${x*sx}px`,top:`${(yTop-22)*sy}px`,opacity:0,transition:'opacity .4s ease'})
        wrapper.appendChild(el)
        requestAnimationFrame(()=>requestAnimationFrame(()=>{el.style.opacity=1}))
      })
    }

    animRef.current = requestAnimationFrame(frame)

    // Tooltip
    canvas.onmousemove = e => {
      const rect=canvas.getBoundingClientRect(), mx=e.clientX-rect.left
      const i=Math.floor((mx-PAD.left)/(pW/n))
      const tip=tipRef.current; if(!tip) return
      if (i>=0&&i<n) {
        const norm=weights[i]/max, dAgo=n-1-i, ev=inferLabel(weights,i)
        tip.style.display='block'; tip.style.left=Math.min(mx+12,W-150)+'px'; tip.style.top='8px'
        tip.style.borderColor=norm>.75?'#ffa502':'rgba(0,210,255,0.25)'; tip.style.color=norm>.75?'#ffa502':'#00d2ff'
        tip.innerHTML=`<div style="font-weight:700">${dAgo===0?'Today':`${dAgo}d ago`}</div><div>${(weights[i]*100).toFixed(1)}%</div>${ev?`<div style="color:${ev.color}">${ev.text}</div>`:''}`
      } else tip.style.display='none'
    }
    canvas.onmouseleave=()=>{ if(tipRef.current) tipRef.current.style.display='none' }

    return () => { if(animRef.current) cancelAnimationFrame(animRef.current) }
  }, [weights])

  const max    = weights.length ? Math.max(...weights) : 0
  const topIdx = weights.indexOf(max)
  const dAgo   = weights.length - 1 - topIdx

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 4 }}>Which past days drove the forecast?</div>
          <div style={{ fontSize: 10, color: 'var(--muted)', lineHeight: 1.7, maxWidth: 520 }}>
            Attention-LSTM importance scores for each of the past 30 days.
            <span style={{ color: '#ffa502' }}> Amber bars</span> are days the model weighted most heavily.
          </div>
        </div>
        {max > 0 && (
          <div style={{ background: 'rgba(255,165,2,0.08)', border: '1px solid rgba(255,165,2,0.25)', borderRadius: 8, padding: '8px 14px', fontSize: 11 }}>
            <div style={{ fontSize: 9, color: 'var(--muted)', letterSpacing: '.1em', marginBottom: 4 }}>KEY DRIVER</div>
            <div style={{ fontWeight: 700, color: '#ffa502' }}>⚠ Day {topIdx+1} ({dAgo===0?'today':`${dAgo}d ago`})</div>
            <div style={{ fontSize: 9, color: 'rgba(180,230,248,0.5)', marginTop: 2 }}>Importance: {(max*100).toFixed(1)}%</div>
          </div>
        )}
      </div>
      <div ref={wrapperRef} style={{ position: 'relative' }}>
        <canvas ref={canvasRef} style={{ width: '100%', height: 190, borderRadius: 8, cursor: 'crosshair', display: 'block' }} />
        <div ref={tipRef} style={{ display: 'none', position: 'absolute', background: 'rgba(6,18,32,.95)', border: '1px solid var(--border)', borderRadius: 6, padding: '6px 10px', fontSize: 10, pointerEvents: 'none', zIndex: 10, fontFamily: 'var(--mono)' }} />
      </div>
      <div style={{ display: 'flex', gap: 18, marginTop: 10, fontSize: 10, color: 'rgba(180,230,248,0.4)', fontFamily: 'var(--mono)', flexWrap: 'wrap' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 12, height: 12, borderRadius: 2, background: '#00d2ff', display: 'inline-block' }}/>Normal</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 12, height: 12, borderRadius: 2, background: '#ffa502', display: 'inline-block' }}/>High attention ▲75%</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}><span style={{ width: 12, height: 12, borderRadius: 2, background: '#ff4757', display: 'inline-block' }}/>Critical ▲90%</span>
      </div>
    </div>
  )
}
