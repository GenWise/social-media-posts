const APPS_SCRIPT_URL =
  'https://script.google.com/macros/s/AKfycbxCzwF7o0VmVQRu3ItQl4zHasNcsC2ybV7zBqPKrlM9RjbXO03MVGb7Z949WavIUZVSdg/exec'

export async function fetchPosts() {
  const res = await fetch(APPS_SCRIPT_URL)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const json = await res.json()
  return json.posts ?? []
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
