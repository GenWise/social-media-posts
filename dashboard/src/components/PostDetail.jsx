import { ArrowLeft, ExternalLink, Lock, LockOpen } from 'lucide-react'
import { PlatformIcon, PLATFORM_LABELS } from './PlatformIcon'
import { StatusBadge } from './StatusBadge'

const GROUPS = {
  Identity:         ['post_id','idea_id','variant_id','platform','status','lock_status'],
  Content:          ['hook','body','cta','final_post_text','hashtags','mentions','render_version'],
  Media:            ['media_type','media_drive_url','media_public_url','duration_sec','aspect_ratio','srt_url'],
  Classification:   ['offering','post_type','content_angle','campaign','person_featured'],
  'Schedule & URLs':['scheduled_time','posted_time','post_url','source_asset_id'],
  Metrics:          ['impressions','engagements'],
  System:           ['platform_constraints_ok','error_message','retry_count','owner','last_updated_by','last_updated_at','notes'],
}

function Field({ col, val }) {
  if (!val && val !== 0) return (
    <div className="py-2.5">
      <dt className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">{col}</dt>
      <dd className="text-xs text-slate-300 italic mt-0.5">—</dd>
    </div>
  )

  let content
  if (col === 'final_post_text' || col === 'body' || col === 'hook') {
    content = <dd className="mt-1 text-[13px] leading-relaxed text-slate-700 whitespace-pre-wrap bg-slate-50 rounded-lg p-3 border border-slate-100">{val}</dd>
  } else if (col === 'post_url') {
    content = <dd><a href={val} target="_blank" rel="noopener noreferrer" className="text-[13px] text-primary hover:underline flex items-center gap-1 break-all">{val.length > 60 ? val.slice(0, 60) + '…' : val}<ExternalLink size={12} className="shrink-0" /></a></dd>
  } else if (col === 'status') {
    content = <dd className="mt-1"><StatusBadge status={val} /></dd>
  } else if (col === 'lock_status') {
    content = (
      <dd className={`flex items-center gap-1 text-[13px] mt-0.5 ${val === 'LOCKED' ? 'text-slate-400' : 'text-emerald-600'}`}>
        {val === 'LOCKED' ? <Lock size={13} /> : <LockOpen size={13} />} {val}
      </dd>
    )
  } else if (col === 'platform_constraints_ok') {
    const color = val === 'VALID' ? 'text-emerald-600' : val === 'INVALID' ? 'text-red-500' : 'text-amber-500'
    content = <dd className={`text-[13px] font-medium mt-0.5 ${color}`}>{val}</dd>
  } else {
    content = <dd className="text-[13px] text-slate-700 break-words mt-0.5">{val}</dd>
  }

  return (
    <div className="py-2.5">
      <dt className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">{col}</dt>
      {content}
    </div>
  )
}

export function PostDetail({ post, onBack }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-30 bg-white border-b border-slate-100 px-4 py-3 flex items-center gap-3 shadow-sm">
        <button onClick={onBack} className="w-9 h-9 flex items-center justify-center rounded-full hover:bg-slate-100 transition-colors">
          <ArrowLeft size={20} />
        </button>
        <div className="flex items-center gap-2">
          <PlatformIcon platform={post.platform} size={16} />
          <span className="text-sm font-semibold text-slate-800 font-mono">{post.post_id}</span>
          <StatusBadge status={post.status} />
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-5 space-y-3 pb-12">
        {Object.entries(GROUPS).map(([group, cols]) => (
          <section key={group} className="bg-white rounded-2xl px-4 py-1 shadow-sm border border-slate-100">
            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pt-3 pb-1.5 border-b border-slate-50">
              {group}
            </h3>
            <dl className="divide-y divide-slate-50">
              {cols.map(col => <Field key={col} col={col} val={post[col]} />)}
            </dl>
          </section>
        ))}
      </main>
    </div>
  )
}
