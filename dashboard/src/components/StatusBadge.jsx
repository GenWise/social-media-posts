import { STATUS_STYLES } from '../lib/data'

export function StatusBadge({ status }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase ${STATUS_STYLES[status] ?? 'bg-slate-100 text-slate-400'}`}>
      {status || '—'}
    </span>
  )
}
