import { useState, useEffect, useMemo } from 'react'
import { RefreshCw, Search } from 'lucide-react'
import { fetchPosts, PLATFORMS, OFFERINGS, QUEUE_STATUSES, HISTORY_STATUSES } from './lib/data'
import { Select } from './components/Select'
import { DateRangeSelect, computeDateRange } from './components/DateRangeSelect'
import { PostCard } from './components/PostCard'
import { PostDetail } from './components/PostDetail'
import { PlatformIcon, PLATFORM_LABELS } from './components/PlatformIcon'

const PLATFORM_OPTIONS = PLATFORMS.map(p => ({ value: p, label: PLATFORM_LABELS[p] }))
const OFFERING_OPTIONS  = OFFERINGS.map(o => ({ value: o, label: o }))

export default function App() {
  const [posts, setPosts]         = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)
  const [updatedAt, setUpdatedAt] = useState(null)
  const [tab, setTab]             = useState('queue')
  const [detail, setDetail]       = useState(null)

  // Filters
  const [platform, setPlatform] = useState('')
  const [offering, setOffering] = useState('')
  const [status,   setStatus]   = useState('')
  const [campaign, setCampaign] = useState('')
  const [person,   setPerson]   = useState('')
  const [search,      setSearch]      = useState('')
  const [datePreset,  setDatePreset]  = useState('')
  const [customFrom,  setCustomFrom]  = useState('')
  const [customTo,    setCustomTo]    = useState('')

  async function load() {
    setLoading(true); setError(null)
    try {
      const data = await fetchPosts()
      setPosts(data)
      setUpdatedAt(new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit' }) + ' IST')
    } catch(e) { setError(e.message) }
    finally    { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const campaigns = useMemo(() => [...new Set(posts.map(p => p.campaign).filter(Boolean))].sort(), [posts])
  const persons   = useMemo(() => [...new Set(posts.map(p => p.person_featured).filter(Boolean))].sort(), [posts])
  const statuses  = useMemo(() => (tab === 'queue' ? QUEUE_STATUSES : HISTORY_STATUSES), [tab])

  const visible = useMemo(() => {
    const tabFilter  = tab === 'queue' ? QUEUE_STATUSES : HISTORY_STATUSES
    const q          = search.toLowerCase()
    return posts
      .filter(p => {
        if (!tabFilter.includes(p.status)) return false
        if (platform && p.platform !== platform) return false
        if (offering && p.offering !== offering) return false
        if (status   && p.status   !== status)   return false
        if (campaign && p.campaign !== campaign)  return false
        if (person   && p.person_featured !== person) return false
        if (q) {
          const haystack = [p.final_post_text, p.hook, p.body, p.person_featured, p.campaign, p.offering]
            .join(' ').toLowerCase()
          if (!haystack.includes(q)) return false
        }
        // Date range — compare against the relevant date field
        const { from: dateFrom, to: dateTo } = computeDateRange(datePreset, customFrom, customTo)
        const dateField = tab === 'queue' ? p.scheduled_time : p.posted_time
        if (dateFrom && dateField && dateField.slice(0,10) < dateFrom) return false
        if (dateTo   && dateField && dateField.slice(0,10) > dateTo)   return false
        return true
      })
      .sort((a, b) => {
        const da = (tab === 'queue' ? a.scheduled_time : a.posted_time) || ''
        const db = (tab === 'queue' ? b.scheduled_time : b.posted_time) || ''
        return tab === 'queue' ? da.localeCompare(db) : db.localeCompare(da)
      })
  }, [posts, tab, platform, offering, status, campaign, person, search, datePreset, customFrom, customTo])

  const activeFilters = [platform, offering, status, campaign, person, search, datePreset].filter(Boolean).length

  function clearAll() {
    setPlatform(''); setOffering(''); setStatus(''); setCampaign(''); setPerson('')
    setSearch(''); setDatePreset(''); setCustomFrom(''); setCustomTo('')
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Sticky header */}
      <div className="sticky top-0 z-20 bg-white border-b border-slate-100 px-4 pt-4 pb-3 space-y-3">
        {/* Top bar */}
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">GenWise Social Media Pipeline</h1>
          <div className="flex items-center gap-2">
            {updatedAt && <span className="text-[11px] text-slate-400 hidden sm:block">{updatedAt}</span>}
            <button onClick={load} disabled={loading}
              className="w-8 h-8 flex items-center justify-center rounded-full bg-white border border-slate-200 text-slate-400 hover:text-primary hover:border-primary transition-colors disabled:opacity-40">
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex p-1 bg-slate-100 rounded-full max-w-2xl mx-auto">
          {['queue', 'history'].map(t => (
            <button key={t} onClick={() => { setTab(t); setStatus('') }}
              className={`flex-1 py-2 px-4 rounded-full text-sm font-medium capitalize transition-all ${
                tab === t ? 'bg-white shadow-sm text-primary font-semibold' : 'text-slate-500 hover:text-slate-700'
              }`}>
              {t === 'queue' ? 'Queue' : 'History'}
              <span className={`ml-1.5 text-[11px] font-bold ${tab === t ? 'text-primary' : 'text-slate-400'}`}>
                {tab === t
                  ? visible.length
                  : posts.filter(p => (t === 'queue' ? QUEUE_STATUSES : HISTORY_STATUSES).includes(p.status)).length}
              </span>
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative max-w-2xl mx-auto">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search posts, people, campaigns…"
            className="w-full h-9 pl-8 pr-3 rounded-lg border border-slate-200 text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-colors"
          />
          {search && (
            <button onClick={() => setSearch('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs px-1">
              ✕
            </button>
          )}
        </div>

        {/* Filter row — all on one scrollable line */}
        <div className="flex items-center gap-2 overflow-x-auto hide-scrollbar max-w-2xl mx-auto pb-0.5">
          <Select label="Platform" value={platform} onChange={setPlatform} options={PLATFORM_OPTIONS}
            renderOption={opt => <PlatformIcon platform={opt.value} size={14} />} />
          <Select label="Offering" value={offering} onChange={setOffering} options={OFFERING_OPTIONS} />
          <Select label="Status"   value={status}   onChange={setStatus}   options={statuses.map(s => ({ value: s, label: s }))} />
          {campaigns.length > 0 && (
            <Select label="Campaign" value={campaign} onChange={setCampaign} options={campaigns.map(c => ({ value: c, label: c }))} />
          )}
          {persons.length > 0 && (
            <Select label="Person" value={person} onChange={setPerson} options={persons.map(p => ({ value: p, label: p }))} />
          )}
          <div className="shrink-0 w-px h-5 bg-slate-200 mx-0.5" />
          <DateRangeSelect
            preset={datePreset}
            customFrom={customFrom}
            customTo={customTo}
            onChange={({ preset, customFrom: f, customTo: t }) => {
              setDatePreset(preset); setCustomFrom(f); setCustomTo(t)
            }}
          />
          {activeFilters > 0 && (
            <button onClick={clearAll}
              className="shrink-0 h-9 px-3 rounded-lg text-xs font-medium text-slate-500 hover:text-red-500 hover:bg-red-50 transition-colors border border-transparent hover:border-red-100">
              Clear {activeFilters}
            </button>
          )}
        </div>
      </div>

      {/* Cards */}
      <main className="max-w-2xl mx-auto px-4 pt-3 pb-12 space-y-3">
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400">
            <RefreshCw size={28} className="animate-spin mb-3" />
            <p className="text-sm">Loading pipeline…</p>
          </div>
        )}
        {error && (
          <div className="rounded-2xl bg-red-50 border border-red-100 p-5">
            <p className="text-sm font-semibold text-red-700 mb-1">Failed to load</p>
            <p className="text-xs text-red-500">{error}</p>
          </div>
        )}
        {!loading && !error && visible.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <p className="text-4xl mb-3">📭</p>
            <h3 className="text-base font-semibold text-slate-600 mb-1">Nothing here</h3>
            <p className="text-sm text-slate-400">No posts match your filters.</p>
          </div>
        )}
        {!loading && visible.map(post => (
          <PostCard key={`${post.post_id}-${post.platform}`} post={post} tab={tab} onClick={() => setDetail(post)} />
        ))}
      </main>

      {/* Detail modal */}
      {detail && <PostDetail post={detail} onClose={() => setDetail(null)} />}
    </div>
  )
}
