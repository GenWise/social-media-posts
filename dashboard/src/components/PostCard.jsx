import { ExternalLink, Lock, Paperclip, Pencil } from 'lucide-react'
import { PlatformIcon } from './PlatformIcon'
import { StatusBadge } from './StatusBadge'
import { formatDate } from '../lib/data'

export function PostCard({ post, tab, onClick, onEdit }) {
  const preview  = (post.final_post_text || post.hook || '').slice(0, 160)
  const more     = (post.final_post_text || '').length > 160
  const hasMedia = post.media_type && post.media_type !== 'none' && post.media_type !== ''

  const scheduledDate = formatDate(post.scheduled_time, true)
  const postedDate    = formatDate(post.posted_time, true)

  return (
    <article onClick={onClick}
      className="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 cursor-pointer hover:border-slate-200 hover:shadow-md transition-all active:scale-[0.99]">

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
          {tab === 'queue' && onEdit && (
            <button
              onClick={e => { e.stopPropagation(); onEdit(post) }}
              className="w-6 h-6 flex items-center justify-center rounded-md hover:bg-slate-100 text-slate-300 hover:text-primary transition-colors"
              title="Edit post"
            >
              <Pencil size={12} />
            </button>
          )}
        </div>
      </div>

      {/* Person */}
      {post.person_featured && (
        <p className="text-xs font-semibold text-slate-500 mb-1">{post.person_featured}</p>
      )}

      {/* Text */}
      <p className="text-[13.5px] leading-relaxed text-slate-700 line-clamp-3 mb-3">
        {preview}{more ? '…' : ''}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-50 gap-2">
        {/* Left: date */}
        <div className="flex items-center gap-3 text-[11px] text-slate-400">
          {tab === 'queue' && scheduledDate && <span>🗓 {scheduledDate}</span>}
          {tab === 'history' && postedDate   && <span>📅 {postedDate}</span>}
          {post.impressions && <span>👁 {post.impressions}</span>}
          {post.engagements && <span>♥ {post.engagements}</span>}
        </div>
        {/* Right: live link for history */}
        {tab === 'history' && post.post_url && (
          <a href={post.post_url} target="_blank" rel="noopener noreferrer"
            onClick={e => e.stopPropagation()}
            className="flex items-center gap-1 text-primary text-[11px] font-medium hover:underline shrink-0">
            View live <ExternalLink size={11} />
          </a>
        )}
      </div>
    </article>
  )
}
