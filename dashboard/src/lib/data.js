const APPS_SCRIPT_URL =
  'https://script.google.com/macros/s/AKfycbxCzwF7o0VmVQRu3ItQl4zHasNcsC2ybV7zBqPKrlM9RjbXO03MVGb7Z949WavIUZVSdg/exec'

export async function fetchPosts() {
  const res = await fetch(APPS_SCRIPT_URL)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const json = await res.json()
  return json.posts ?? []
}

// Format a date string like "2026-03-21 09:00" → "Sat Mar 21, 2026"
// or "Sat Mar 21, 2026 09:00" when includeTime is true
export function formatDate(str, includeTime = false) {
  if (!str) return null
  const iso = str.slice(0, 16).replace(' ', 'T')
  const d = new Date(iso)
  if (isNaN(d)) return str.slice(0, 16)
  const wd  = d.toLocaleDateString('en-US', { weekday: 'short' })  // Sat
  const mon = d.toLocaleDateString('en-US', { month: 'short' })    // Mar
  const day = d.getDate()                                           // 21
  const yr  = d.getFullYear()                                       // 2026
  const formatted = `${wd} ${mon} ${day}, ${yr}`
  if (!includeTime || str.length < 16) return formatted
  return `${formatted} ${str.slice(11, 16)}`
}

export const QUEUE_STATUSES  = ['DRAFT', 'READY', 'SCHEDULED']
export const HISTORY_STATUSES = ['POSTED']

export const PLATFORMS = ['TW', 'LI', 'YT']
export const OFFERINGS = ['M3', 'GSP', 'TNP365', 'GenAI']

export const STATUS_STYLES = {
  DRAFT:     'bg-amber-100 text-amber-700',
  READY:     'bg-blue-100 text-blue-700',
  SCHEDULED: 'bg-emerald-100 text-emerald-700',
  POSTED:    'bg-slate-100 text-slate-500',
}
