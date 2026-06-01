import { useState } from 'react'
import { X, ExternalLink, Lock, Copy, Check, Image, Film, MessageSquare, Link2 } from 'lucide-react'
import { PlatformIcon, PLATFORM_LABELS } from './PlatformIcon'
import { StatusBadge } from './StatusBadge'
import { formatDate } from '../lib/data'

function CopyBlock({ label, icon: Icon, text, isUrl }) {
  const [copied, setCopied] = useState(false)
  if (!text) return null
  const lines = text.split(',').map(s => s.trim()).filter(Boolean)
  return (
    <div className="mb-2.5">
      <div className="flex items-center gap-1.5 mb-1">
        {Icon && <Icon size={12} className="text-slate-400" />}
        <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">{label}</span>
      </div>
      {lines.map((line, i) => (
        <div key={i} className="flex items-center gap-1.5 group">
          {isUrl ? (
            <a href={line.startsWith('http') ? line : `https://${line}`} target="_blank" rel="noopener noreferrer"
              className="text-[12px] text-primary hover:underline break-all leading-relaxed">
              {line}
            </a>
          ) : (
            <p className="text-[12px] text-slate-600 whitespace-pre-wrap break-all leading-relaxed flex-1">{line}</p>
          )}
        </div>
      ))}
      <button
        onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500) }}
        className="mt-1 flex items-center gap-1 text-[11px] text-slate-400 hover:text-primary transition-colors">
        {copied ? <><Check size={10} /> Copied</> : <><Copy size={10} /> Copy</>}
      </button>
    </div>
  )
}

function extractComment(notes) {
  if (!notes) return ''
  const patterns = [
    /FIRST COMMENT:\s*(.+?)(?:\.|$)/i,
    /COMMENT AFTER POSTING:\s*(.+?)(?:\.|$)/i,
    /First comment:\s*(.+?)(?:\.|$)/i,
  ]
  for (const p of patterns) {
    const m = notes.match(p)
    if (m) return m[1].trim()
  }
  return ''
}

export function PostDetail({ post, onClose }) {
  const [textCopied, setTextCopied] = useState(false)
  const date = post.posted_time || post.scheduled_time || ''
  const dateLabel = formatDate(date, true)
  const hasMedia = post.media_drive_url || post.media_public_url
  const comment = extractComment(post.notes)
  const isQueue = !post.posted_time

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

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto px-5 py-4 min-h-0 space-y-4">

          {/* Post text with copy button */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">Post text</span>
              <button
                onClick={() => { navigator.clipboard.writeText(post.final_post_text || post.body || post.hook || ''); setTextCopied(true); setTimeout(() => setTextCopied(false), 1500) }}
                className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-primary transition-colors">
                {textCopied ? <><Check size={10} /> Copied</> : <><Copy size={10} /> Copy text</>}
              </button>
            </div>
            <p className="text-[13.5px] leading-relaxed text-slate-700 whitespace-pre-wrap">
              {post.final_post_text || post.body || post.hook || '—'}
            </p>
          </div>

          {/* Posting checklist — only for queue posts */}
          {isQueue && (hasMedia || comment) && (
            <div className="bg-slate-50 rounded-xl p-3.5 space-y-0.5">
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-2">Posting checklist</p>

              <CopyBlock
                label={post.media_type === 'video' ? 'Video' : 'Images'}
                icon={post.media_type === 'video' ? Film : Image}
                text={post.media_drive_url}
                isUrl={true}
              />

              {post.media_public_url && post.media_public_url !== post.media_drive_url && (
                <CopyBlock label="Local path" icon={Link2} text={post.media_public_url} isUrl={false} />
              )}

              {comment && (
                <CopyBlock label="First comment / reply" icon={MessageSquare} text={comment} isUrl={false} />
              )}

              {post.mentions && (
                <CopyBlock label="Mentions" icon={null} text={post.mentions} isUrl={false} />
              )}
            </div>
          )}
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
