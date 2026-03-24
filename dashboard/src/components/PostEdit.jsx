import { useState } from 'react'
import { X, CheckCircle, Save, AlertCircle } from 'lucide-react'
import { PlatformIcon, PLATFORM_LABELS } from './PlatformIcon'
import { updatePost, markReady } from '../lib/data'

export function PostEdit({ post, onClose, onSaved }) {
  const [text, setText]           = useState(post.final_post_text || '')
  const [schedTime, setSchedTime] = useState(
    post.scheduled_time ? post.scheduled_time.slice(0, 16).replace(' ', 'T') : ''
  )
  const [saving, setSaving]   = useState(false)
  const [error, setError]     = useState(null)
  const [success, setSuccess] = useState(null)

  async function handleSave() {
    setSaving(true); setError(null); setSuccess(null)
    try {
      await updatePost(post.post_id, post.platform, {
        final_post_text: text,
        scheduled_time: schedTime ? schedTime.replace('T', ' ') : '',
      })
      setSuccess('Saved')
      onSaved({ ...post, final_post_text: text, scheduled_time: schedTime ? schedTime.replace('T', ' ') : post.scheduled_time })
    } catch (e) { setError(e.message) }
    finally { setSaving(false) }
  }

  async function handleMarkReady() {
    setSaving(true); setError(null); setSuccess(null)
    try {
      await markReady(
        post.post_id, post.platform,
        text,
        schedTime ? schedTime.replace('T', ' ') : ''
      )
      setSuccess('Marked as Ready')
      onSaved({ ...post, final_post_text: text, status: 'READY', scheduled_time: schedTime ? schedTime.replace('T', ' ') : post.scheduled_time })
      setTimeout(onClose, 800)
    } catch (e) { setError(e.message) }
    finally { setSaving(false) }
  }

  const charCount = text.length
  const charLimit = post.platform === 'TW' ? 25000 : null
  const overLimit = charLimit && charCount > charLimit

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white w-full sm:max-w-lg sm:rounded-2xl rounded-t-2xl shadow-2xl flex flex-col max-h-[92vh]">

        {/* Header */}
        <div className="flex items-center justify-between px-4 pt-4 pb-3 border-b border-slate-100 shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-slate-50 flex items-center justify-center">
              <PlatformIcon platform={post.platform} size={15} />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800 leading-tight">{post.post_id}</p>
              <p className="text-[11px] text-slate-400">{PLATFORM_LABELS[post.platform]} · {post.status}</p>
            </div>
          </div>
          <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-100 text-slate-400">
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
          {/* Post text */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">Post text</label>
              <span className={`text-[11px] ${overLimit ? 'text-red-500 font-semibold' : 'text-slate-400'}`}>
                {charCount}{charLimit ? ` / ${charLimit.toLocaleString()}` : ''}
              </span>
            </div>
            <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              rows={12}
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-700 leading-relaxed resize-none focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-colors font-mono"
            />
          </div>

          {/* Scheduled time */}
          <div>
            <label className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">Scheduled time</label>
            <input
              type="datetime-local"
              value={schedTime}
              onChange={e => setSchedTime(e.target.value)}
              className="h-9 px-3 rounded-xl border border-slate-200 text-sm text-slate-600 focus:outline-none focus:border-primary transition-colors"
            />
          </div>

          {/* Status/feedback */}
          {error && (
            <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 rounded-xl px-3 py-2">
              <AlertCircle size={14} /> {error}
            </div>
          )}
          {success && (
            <div className="flex items-center gap-2 text-emerald-600 text-sm bg-emerald-50 rounded-xl px-3 py-2">
              <CheckCircle size={14} /> {success}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex gap-2 px-4 py-3 border-t border-slate-100 shrink-0">
          <button onClick={onClose} disabled={saving}
            className="flex-1 h-10 rounded-xl border border-slate-200 text-sm font-medium text-slate-500 hover:bg-slate-50 transition-colors disabled:opacity-40">
            Cancel
          </button>
          <button onClick={handleSave} disabled={saving || overLimit}
            className="flex items-center justify-center gap-1.5 h-10 px-4 rounded-xl border border-slate-300 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-40">
            <Save size={13} />
            {saving ? 'Saving…' : 'Save draft'}
          </button>
          <button onClick={handleMarkReady} disabled={saving || overLimit}
            className="flex items-center justify-center gap-1.5 flex-1 h-10 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors disabled:opacity-40">
            <CheckCircle size={13} />
            {saving ? 'Saving…' : 'Mark Ready'}
          </button>
        </div>
      </div>
    </div>
  )
}
