import { useState, useEffect, useMemo } from 'react'
import { RefreshCw } from 'lucide-react'
import { fetchPosts, PLATFORMS, OFFERINGS, QUEUE_STATUSES, HISTORY_STATUSES } from './lib/data'
import { Select } from './components/Select'
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

  const [platform, setPlatform] = useState('')
  const [offering, setOffering] = useState('')
  const [status, setStatus]     = useState('')
  const [campaign, setCampaign] = useState('')
  const [person, setPerson]     = useState('')

  async function load() {
    setLoading(true); setError(null)
    try {
      const data = await fetchPosts()
      setPosts(data)
      setUpdatedAt(new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit' }) + ' IST')
    } catch(e) { setError(e.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const campaigns = useMemo(() => [...new Set(posts.map(p => p.campaign).filter(Boolean))].sort(), [posts])
  const persons   = useMemo(() => [...new Set(posts.map(p => p.person_featured).filter(Boolean))].sort(), [posts])
  const statuses  = useMemo(() => (tab === 'queue' ? QUEUE_STATUSES : HISTORY_STATUSES), [tab])

  const visible = useMemo(() => {
    const tabFilter = tab === 'queue' ? QUEUE_STATUSES : HISTORY_STATUSES
    return posts
      .filter(p =>
        tabFilter.includes(p.status) &&
        (!platform || p.platform === platform) &&
        (!offering || p.offering === offering) &&
        (!status   || p.status   === status)   &&
        (!campaign || p.campaign === campaign)  &&
        (!person   || p.person_featured === person)
      )
      .sort((a, b) => {
        const da = (tab === 'queue' ? a.scheduled_time : a.posted_time) || ''
        const db = (tab === 'queue' ? b.scheduled_time : b.posted_time) || ''
        return tab === 'queue' ? da.localeCompare(db) : db.localeCompare(da)
      })
  }, [posts, tab, platform, offering, status, campaign, person])

  const activeFilters = [platform, offering, status, campaign, person].filter(Boolean).length

  if (detail) return <PostDetail post={detail} onBack={() => setDetail(null)} />

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="sticky top-0 z-20 bg-white border-b border-slate-100 px-4 pt-4 pb-3 space-y-3">
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">GW Pipeline</h1>
          <div className="flex items-center gap-2">
            {updatedAt && <span className="text-[11px] text-slate-400 hidden sm:block">{updatedAt}</span>}
            <button onClick={load} disabled={loading}
              className="w-8 h-8 flex items-center justify-center rounded-full bg-white border border-slate-200 text-slate-400 hover:text-primary hover:border-primary transition-colors disabled:opacity-40">
              <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

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

        <div className="flex items-center gap-2 flex-wrap max-w-2xl mx-auto">
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
          {activeFilters > 0 && (
            <button onClick={() => { setPlatform(''); setOffering(''); setStatus(''); setCampaign(''); setPerson('') }}
              className="h-9 px-3 rounded-lg text-xs font-medium text-slate-500 hover:text-red-500 hover:bg-red-50 transition-colors border border-transparent hover:border-red-100">
              Clear {activeFilters} filter{activeFilters > 1 ? 's' : ''}
            </button>
          )}
        </div>
      </div>

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
    </div>
  )
}
