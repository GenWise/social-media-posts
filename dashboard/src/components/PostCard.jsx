import { ExternalLink, Lock, Paperclip } from 'lucide-react'
import { PlatformIcon } from './PlatformIcon'
import { StatusBadge } from './StatusBadge'

export function PostCard({ post, tab, onClick }) {
  const preview = (post.final_post_text || post.hook || '').slice(0, 160)
  const dateVal  = tab === 'queue' ? post.scheduled_time : post.posted_time
  const date     = (dateVal || '').slice(0, 16) || '—'
  const hasMedia = post.media_type && post.media_type !== 'none' && post.media_type !== ''

  return (
    <article
      onClick={onClick}
      className="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 cursor-pointer hover:border-slate-200 hover:shadow-md transition-all active:scale-[0.99]"
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          <div className="w-7 h-7 rounded-lg bg-slate-50 flex items-center justify-center shrink-0">
            <PlatformIcon platform={post.platform} size={15} />
          </div>
          <StatusBadge status={post.status} />
          {post.lock_status === 'LOCKED' && <Lock size={12} className="text-slate-300" />}
        </div>
        <div className="flex items-center gap-1.5 shrink-0">
          {post.offering && (
            <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 text-[10px] font-semibold">
              {post.offering}
            </span>
          )}
          {hasMedia && <Paperclip size={13} className="text-slate-300" />}
        </div>
      </div>

      {/* Person */}
      {post.person_featured && (
        <p className="text-xs font-semibold text-slate-500 mb-1">{post.person_featured}</p>
      )}

      {/* Text preview */}
      <p className="text-[13.5px] leading-relaxed text-slate-700 line-clamp-3 mb-3">
        {preview}{(post.final_post_text || '').length > 160 ? '…' : ''}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-50">
        {/* Metrics (history) */}
        {tab === 'history' && (post.impressions || post.engagements) ? (
          <div className="flex items-center gap-3 text-slate-400 text-[11px] mr-auto">
            {post.impressions && <span>👁 {post.impressions}</span>}
            {post.engagements && <span>♥ {post.engagements}</span>}
          </div>
        ) : null}

        {/* Date or live link */}
        {tab === 'history' && post.post_url ? (
          <a
            href={post.post_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={e => e.stopPropagation()}
            className="ml-auto flex items-center gap-1 text-primary text-xs font-medium hover:underline"
          >
            View live <ExternalLink size={12} />
          </a>
        ) : (
          <span className="ml-auto text-xs text-slate-400">{date}</span>
        )}
      </div>
    </article>
  )
}
