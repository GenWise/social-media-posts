import { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { ChevronDown, Check } from 'lucide-react'

export function Select({ label, options, value, onChange, renderOption }) {
  const [open, setOpen]   = useState(false)
  const [pos, setPos]     = useState({ top: 0, left: 0, width: 0 })
  const buttonRef = useRef(null)
  const menuRef   = useRef(null)

  useEffect(() => {
    if (!open) return
    const handler = (e) => {
      if (
        buttonRef.current && !buttonRef.current.contains(e.target) &&
        menuRef.current   && !menuRef.current.contains(e.target)
      ) setOpen(false)
    }
    document.addEventListener('pointerdown', handler)
    return () => document.removeEventListener('pointerdown', handler)
  }, [open])

  function openMenu() {
    if (open) { setOpen(false); return }
    const rect = buttonRef.current.getBoundingClientRect()
    setPos({ top: rect.bottom + 4, left: rect.left, width: rect.width })
    setOpen(true)
  }

  const current = options.find(o => o.value === value)

  return (
    <div className="relative shrink-0">
      <button
        ref={buttonRef}
        onClick={openMenu}
        className={`flex items-center gap-1.5 h-9 px-3 rounded-lg border text-sm font-medium transition-colors
          ${value
            ? 'bg-primary text-white border-primary'
            : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'
          }`}
      >
        {current ? (
          <>
            {renderOption && renderOption(current, true)}
            <span>{current.label}</span>
          </>
        ) : (
          <span className="text-slate-500">{label}</span>
        )}
        <ChevronDown size={14} className={`transition-transform ${open ? 'rotate-180' : ''} ${value ? 'text-white/80' : 'text-slate-400'}`} />
      </button>

      {open && createPortal(
        <div
          ref={menuRef}
          style={{ position: 'fixed', top: pos.top, left: pos.left, minWidth: Math.max(pos.width, 160), zIndex: 9999 }}
          className="bg-white border border-slate-200 rounded-xl shadow-lg py-1 overflow-hidden"
        >
          <button
            onClick={() => { onChange(''); setOpen(false) }}
            className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-slate-50 text-slate-500"
          >
            <span>All</span>
            {!value && <Check size={14} className="text-primary" />}
          </button>
          <div className="h-px bg-slate-100 my-1" />
          {options.map(opt => (
            <button
              key={opt.value}
              onClick={() => { onChange(opt.value); setOpen(false) }}
              className="w-full flex items-center justify-between gap-2 px-3 py-2 text-sm hover:bg-slate-50"
            >
              <span className="flex items-center gap-2">
                {renderOption && renderOption(opt, false)}
                <span className={value === opt.value ? 'text-primary font-medium' : 'text-slate-700'}>{opt.label}</span>
              </span>
              {value === opt.value && <Check size={14} className="text-primary shrink-0" />}
            </button>
          ))}
        </div>,
        document.body
      )}
    </div>
  )
}
