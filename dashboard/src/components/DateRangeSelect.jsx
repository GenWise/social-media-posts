import { useState, useRef, useEffect } from 'react'
import { ChevronDown, Check } from 'lucide-react'

const PRESETS = [
  { value: '7d',    label: 'Last 7 days' },
  { value: '30d',   label: 'Last 30 days' },
  { value: 'month', label: 'This month' },
  { value: 'custom',label: 'Custom range' },
]

function toISO(d) { return d.toISOString().slice(0, 10) }

export function computeDateRange(preset, customFrom, customTo) {
  const today = new Date()
  if (preset === '7d') {
    const from = new Date(today); from.setDate(from.getDate() - 6)
    return { from: toISO(from), to: toISO(today) }
  }
  if (preset === '30d') {
    const from = new Date(today); from.setDate(from.getDate() - 29)
    return { from: toISO(from), to: toISO(today) }
  }
  if (preset === 'month') {
    const from = new Date(today.getFullYear(), today.getMonth(), 1)
    return { from: toISO(from), to: toISO(today) }
  }
  if (preset === 'custom') {
    return { from: customFrom, to: customTo }
  }
  return { from: '', to: '' }
}

export function DateRangeSelect({ preset, customFrom, customTo, onChange }) {
  const [open, setOpen]       = useState(false)
  const [localFrom, setLocalFrom] = useState(customFrom)
  const [localTo,   setLocalTo]   = useState(customTo)
  const ref = useRef(null)

  useEffect(() => {
    const handler = e => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('pointerdown', handler)
    return () => document.removeEventListener('pointerdown', handler)
  }, [])

  function selectPreset(p) {
    if (p === 'custom') {
      onChange({ preset: 'custom', customFrom: localFrom, customTo: localTo })
      // keep open so user can set dates
    } else {
      onChange({ preset: p, customFrom: '', customTo: '' })
      setOpen(false)
    }
  }

  function applyCustom() {
    onChange({ preset: 'custom', customFrom: localFrom, customTo: localTo })
    setOpen(false)
  }

  const current = PRESETS.find(p => p.value === preset)
  const active  = !!preset

  return (
    <div ref={ref} className="relative shrink-0">
      <button
        onClick={() => setOpen(o => !o)}
        className={`flex items-center gap-1.5 h-9 px-3 rounded-lg border text-sm font-medium transition-colors
          ${active
            ? 'bg-primary text-white border-primary'
            : 'bg-white text-slate-500 border-slate-200 hover:border-slate-300'
          }`}
      >
        <span>{current ? current.label : 'Date range'}</span>
        <ChevronDown size={14} className={`transition-transform ${open ? 'rotate-180' : ''} ${active ? 'text-white/80' : 'text-slate-400'}`} />
      </button>

      {open && (
        <div className="absolute top-full right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg z-50 min-w-[180px] py-1 overflow-hidden">
          {/* All time */}
          <button
            onClick={() => { onChange({ preset: '', customFrom: '', customTo: '' }); setOpen(false) }}
            className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-slate-50 text-slate-500"
          >
            <span>All time</span>
            {!preset && <Check size={14} className="text-primary" />}
          </button>
          <div className="h-px bg-slate-100 my-1" />

          {PRESETS.filter(p => p.value !== 'custom').map(p => (
            <button
              key={p.value}
              onClick={() => selectPreset(p.value)}
              className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-slate-50"
            >
              <span className={preset === p.value ? 'text-primary font-medium' : 'text-slate-700'}>{p.label}</span>
              {preset === p.value && <Check size={14} className="text-primary shrink-0" />}
            </button>
          ))}

          <div className="h-px bg-slate-100 my-1" />

          {/* Custom */}
          <button
            onClick={() => selectPreset('custom')}
            className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-slate-50"
          >
            <span className={preset === 'custom' ? 'text-primary font-medium' : 'text-slate-700'}>Custom range</span>
            {preset === 'custom' && <Check size={14} className="text-primary shrink-0" />}
          </button>

          {preset === 'custom' && (
            <div className="px-3 pb-3 space-y-2">
              <div className="flex flex-col gap-1.5">
                <label className="text-[11px] text-slate-400 font-medium">From</label>
                <input type="date" value={localFrom} onChange={e => setLocalFrom(e.target.value)}
                  className="h-8 px-2 rounded-lg border border-slate-200 text-xs text-slate-600 focus:outline-none focus:border-primary transition-colors" />
                <label className="text-[11px] text-slate-400 font-medium">To</label>
                <input type="date" value={localTo} onChange={e => setLocalTo(e.target.value)}
                  className="h-8 px-2 rounded-lg border border-slate-200 text-xs text-slate-600 focus:outline-none focus:border-primary transition-colors" />
              </div>
              <button onClick={applyCustom}
                className="w-full h-8 rounded-lg bg-primary text-white text-xs font-semibold hover:bg-primary/90 transition-colors">
                Apply
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
