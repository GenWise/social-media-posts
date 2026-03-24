import { X, ExternalLink, Lock } from 'lucide-react'
import { PlatformIcon, PLATFORM_LABELS } from './PlatformIcon'
import { StatusBadge } from './StatusBadge'
import { formatDate } from '../lib/data'

export function PostDetail({ post, onClose }) {
  const date = post.posted_time || post.scheduled_time || ''
  const dateLabel = formatDate(date, true)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg flex flex-col max-h-[90vh]">

        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-4 pb-3 border-b border-slate-100 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-slate-50 flex items-center justify-center">
              <PlatformIcon platform={post.platform} size={15} />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-slate-800 leading-tight">
                {post.person_featured || PLATFORM_LABELS[post.platform] || post.platform}
              </p>
              {post.person_featured && (
                <p className="text-[11px] text-slate-400">{PLATFORM_LABELS[post.platform]}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge status={post.status} />
            {post.lock_status === 'LOCKED' && <Lock size={12} className="text-slate-300" />}
            <button onClick={onClose}
              className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-slate-100 transition-colors text-slate-400 hover:text-slate-600">
              <X size={15} />
            </button>
          </div>
        </div>

        {/* Post text — scrolls if long */}
        <div className="flex-1 overflow-y-auto px-5 py-4 min-h-0">
          {post.hook && post.hook !== post.final_post_text && (
            <p className="text-[13px] font-semibold text-slate-800 mb-2 leading-snug">{post.hook}</p>
          )}
          <p className="text-[13.5px] leading-relaxed text-slate-700 whitespace-pre-wrap">
            {post.final_post_text || post.body || post.hook || '—'}
          </p>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-slate-100 shrink-0 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            {post.offering && (
              <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 text-[11px] font-semibold">
                {post.offering}
              </span>
            )}
            {post.campaign && (
              <span className="text-[11px] text-slate-400">{post.campaign}</span>
            )}
            {dateLabel && (
              <span className="text-[11px] text-slate-400">{dateLabel}</span>
            )}
            {(post.impressions || post.engagements) && (
              <span className="text-[11px] text-slate-400">
                {post.impressions ? `👁 ${post.impressions}` : ''}
                {post.impressions && post.engagements ? ' · ' : ''}
                {post.engagements ? `♥ ${post.engagements}` : ''}
              </span>
            )}
          </div>
          {post.post_url && (
            <a href={post.post_url} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1 text-primary text-xs font-medium hover:underline shrink-0">
              View live <ExternalLink size={12} />
            </a>
          )}
        </div>

      </div>
    </div>
  )
}
