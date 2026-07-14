import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Film, Edit3, MessageSquare, Calendar, Plus, X, Check, ChevronDown, Send, RefreshCw } from 'lucide-react'
import { api, type VideoTrackerItem } from '../lib/api'
import { cn } from '../lib/utils'

// ── Status badge configs ───────────────────────────────────────────────────────

const FILM_COLORS: Record<string, string> = {
  not_filmed: 'bg-stone-700 text-stone-400',
  filmed:     'bg-emerald-900/40 text-emerald-400',
}

const EDIT_COLORS: Record<string, string> = {
  raw:      'bg-stone-700 text-stone-400',
  edited:   'bg-amber-900/40 text-amber-400',
  approved: 'bg-emerald-900/40 text-emerald-400',
}

const CAPTION_COLORS: Record<string, string> = {
  draft:    'bg-stone-700 text-stone-400',
  approved: 'bg-blue-900/40 text-blue-400',
  posted:   'bg-purple-900/40 text-purple-400',
}

const FILM_NEXT: Record<string, string>    = { not_filmed: 'filmed', filmed: 'not_filmed' }
const EDIT_NEXT: Record<string, string>    = { raw: 'edited', edited: 'approved', approved: 'raw' }
const CAPTION_NEXT: Record<string, string> = { draft: 'approved', approved: 'posted', posted: 'draft' }

function Badge({
  value,
  colors,
  nextMap,
  onAdvance,
}: {
  value: string
  colors: Record<string, string>
  nextMap: Record<string, string>
  onAdvance: (next: string) => void
}) {
  return (
    <button
      onClick={() => onAdvance(nextMap[value])}
      title="Click to advance status"
      className={cn(
        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium transition-opacity hover:opacity-80',
        colors[value] ?? 'bg-stone-700 text-stone-400'
      )}
    >
      {value.replace('_', ' ')}
      <ChevronDown size={10} />
    </button>
  )
}

// ── Schedule in Metricool Modal ───────────────────────────────────────────────
function ScheduleModal({ video, onClose }: { video: VideoTrackerItem; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [mediaUrl, setMediaUrl] = useState('')
  const [captionOverride, setCaptionOverride] = useState('')
  const [networks, setNetworks] = useState(['instagram', 'tiktok'])
  const [publishDatetime, setPublishDatetime] = useState('')
  const [result, setResult] = useState<{ publish_datetime: string } | null>(null)

  const { data: nextSlot } = useQuery({
    queryKey: ['metricool-next-slot'],
    queryFn: api.metricool.nextSlot,
  })

  const scheduleMutation = useMutation({
    mutationFn: () => api.metricool.schedule({
      video_id: video.id,
      media_url: mediaUrl,
      networks,
      publish_datetime: publishDatetime || undefined,
      caption_override: captionOverride || undefined,
    }),
    onSuccess: (data) => {
      setResult(data)
      queryClient.invalidateQueries({ queryKey: ['video-tracker'] })
    },
  })

  const toggleNetwork = (n: string) =>
    setNetworks(prev => prev.includes(n) ? prev.filter(x => x !== n) : [...prev, n])

  const NETWORK_OPTS = ['instagram', 'tiktok', 'facebook', 'youtube']

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-stone-900 border border-stone-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="font-heading font-semibold text-stone-100">Schedule in Metricool</h3>
            <p className="text-stone-500 text-xs mt-0.5">{video.title}</p>
          </div>
          <button onClick={onClose} className="btn-ghost p-1"><X size={16} /></button>
        </div>

        {result ? (
          <div className="text-center py-6 space-y-3">
            <div className="w-12 h-12 bg-emerald-900/40 rounded-full flex items-center justify-center mx-auto">
              <Check size={20} className="text-emerald-400" />
            </div>
            <p className="text-stone-100 font-medium">Scheduled!</p>
            <p className="text-stone-400 text-sm">{result.publish_datetime.replace('T', ' at ').slice(0, 19)} CT</p>
            <p className="text-stone-500 text-xs">Metricool will post it automatically at that time.</p>
            <button onClick={onClose} className="btn-primary mt-2">Done</button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">
                Google Drive Video URL <span className="text-red-400">*</span>
              </label>
              <input
                value={mediaUrl}
                onChange={e => setMediaUrl(e.target.value)}
                placeholder="https://drive.google.com/file/d/..."
                className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
              />
              <p className="text-stone-600 text-xs mt-1">Make sure it's set to "Anyone with the link can view"</p>
            </div>

            <div>
              <label className="text-stone-500 text-xs uppercase tracking-wide block mb-2">Platforms</label>
              <div className="flex gap-2 flex-wrap">
                {NETWORK_OPTS.map(n => (
                  <button
                    key={n}
                    onClick={() => toggleNetwork(n)}
                    className={cn(
                      'text-xs px-3 py-1.5 rounded-full border capitalize transition-colors',
                      networks.includes(n)
                        ? 'bg-emerald-600/20 text-emerald-400 border-emerald-600/40'
                        : 'bg-stone-800 text-stone-400 border-stone-700 hover:text-stone-100'
                    )}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">
                Schedule Date/Time <span className="text-stone-600 normal-case">(leave blank for next Tue/Thu 9am CT)</span>
              </label>
              <input
                type="datetime-local"
                value={publishDatetime}
                onChange={e => setPublishDatetime(e.target.value.replace('T', 'T').slice(0, 16) + ':00')}
                className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
              />
              {nextSlot && !publishDatetime && (
                <p className="text-stone-500 text-xs mt-1">Auto-slot: {nextSlot.next_slot.replace('T', ' ')} CT</p>
              )}
            </div>

            <div>
              <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">
                Caption <span className="text-stone-600 normal-case">(optional — paste from Real Estate → Video Captions)</span>
              </label>
              <textarea
                value={captionOverride}
                onChange={e => setCaptionOverride(e.target.value)}
                rows={3}
                placeholder="Paste your Instagram or TikTok caption here..."
                className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600 resize-none"
              />
            </div>

            {scheduleMutation.isError && (
              <p className="text-red-400 text-xs">Error: check that METRICOOL_TOKEN, METRICOOL_USER_ID, and METRICOOL_BLOG_ID are set in .env</p>
            )}

            <div className="flex gap-3 pt-1">
              <button
                onClick={() => scheduleMutation.mutate()}
                disabled={!mediaUrl.trim() || networks.length === 0 || scheduleMutation.isPending}
                className="btn-primary flex items-center gap-2"
              >
                <Send size={14} />
                {scheduleMutation.isPending ? 'Scheduling...' : 'Schedule Post'}
              </button>
              <button onClick={onClose} className="btn-ghost border border-stone-700">Cancel</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Add Video Modal ────────────────────────────────────────────────────────────
function AddVideoModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({
    title: '',
    category: 're',
    neighborhood: '',
    topic: '',
    notes: '',
  })

  const addMutation = useMutation({
    mutationFn: () => api.videoTracker.create(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['video-tracker'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-stone-900 border border-stone-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-heading font-semibold text-stone-100">Add Video</h3>
          <button onClick={onClose} className="btn-ghost p-1"><X size={16} /></button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Category</label>
            <select
              value={form.category}
              onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
            >
              <option value="re">Real Estate</option>
              <option value="gymnastics">GymnastDiva</option>
            </select>
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Title</label>
            <input
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              placeholder="e.g. Pearland Community Tour"
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
            />
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Neighborhood / Topic</label>
            <input
              value={form.neighborhood}
              onChange={e => setForm(f => ({ ...f, neighborhood: e.target.value }))}
              placeholder="e.g. Pearland"
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
            />
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Notes</label>
            <textarea
              value={form.notes}
              onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              rows={2}
              placeholder="Key angles, talking points..."
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600 resize-none"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button
            onClick={() => addMutation.mutate()}
            disabled={!form.title.trim() || addMutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={14} />
            {addMutation.isPending ? 'Adding...' : 'Add Video'}
          </button>
          <button onClick={onClose} className="btn-ghost border border-stone-700">Cancel</button>
        </div>
      </div>
    </div>
  )
}

// ── Video Row ──────────────────────────────────────────────────────────────────
function VideoRow({ video }: { video: VideoTrackerItem }) {
  const queryClient = useQueryClient()
  const [expanded, setExpanded] = useState(false)
  const [editDate, setEditDate] = useState(false)
  const [dateVal, setDateVal] = useState(video.scheduled_for?.slice(0, 10) ?? '')
  const [showSchedule, setShowSchedule] = useState(false)

  const updateMutation = useMutation({
    mutationFn: (data: Partial<VideoTrackerItem>) => api.videoTracker.update(video.id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['video-tracker'] }),
  })

  const engagementTotal = video.ig_likes + video.ig_comments + video.ig_saves + video.tiktok_views

  return (
    <div className="card space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={cn(
              'text-xs px-2 py-0.5 rounded-full font-medium',
              video.category === 're' ? 'bg-emerald-900/30 text-emerald-400' : 'bg-pink-900/30 text-pink-400'
            )}>
              {video.category === 're' ? 'Real Estate' : 'GymnastDiva'}
            </span>
            <p className="text-stone-100 text-sm font-medium">{video.title}</p>
          </div>
          {video.neighborhood && (
            <p className="text-stone-500 text-xs mt-0.5">{video.neighborhood}</p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {video.edit_status === 'approved' && (
            <button
              onClick={() => setShowSchedule(true)}
              className="text-xs px-2 py-1 rounded-lg bg-emerald-600/20 text-emerald-400 border border-emerald-600/30 hover:bg-emerald-600/30 flex items-center gap-1 transition-colors"
            >
              <Send size={10} />
              Metricool
            </button>
          )}
          <button
            onClick={() => setExpanded(e => !e)}
            className="text-stone-500 hover:text-stone-100 text-xs"
          >
            {expanded ? 'Hide' : 'Details'}
          </button>
        </div>
        {showSchedule && <ScheduleModal video={video} onClose={() => setShowSchedule(false)} />}
      </div>

      {/* Status badges — click to advance */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="flex items-center gap-1.5">
          <Film size={11} className="text-stone-600" />
          <Badge
            value={video.film_status}
            colors={FILM_COLORS}
            nextMap={FILM_NEXT}
            onAdvance={v => updateMutation.mutate({ film_status: v })}
          />
        </div>
        <div className="flex items-center gap-1.5">
          <Edit3 size={11} className="text-stone-600" />
          <Badge
            value={video.edit_status}
            colors={EDIT_COLORS}
            nextMap={EDIT_NEXT}
            onAdvance={v => updateMutation.mutate({ edit_status: v })}
          />
        </div>
        <div className="flex items-center gap-1.5">
          <MessageSquare size={11} className="text-stone-600" />
          <Badge
            value={video.caption_status}
            colors={CAPTION_COLORS}
            nextMap={CAPTION_NEXT}
            onAdvance={v => updateMutation.mutate({ caption_status: v })}
          />
        </div>

        {/* Schedule date */}
        <div className="flex items-center gap-1.5 ml-auto">
          <Calendar size={11} className="text-stone-600" />
          {editDate ? (
            <div className="flex items-center gap-1">
              <input
                type="date"
                value={dateVal}
                onChange={e => setDateVal(e.target.value)}
                className="bg-stone-800 border border-stone-700 rounded px-2 py-0.5 text-xs text-stone-100 focus:outline-none focus:border-emerald-600"
              />
              <button
                onClick={() => { updateMutation.mutate({ scheduled_for: dateVal || undefined }); setEditDate(false) }}
                className="text-emerald-400 hover:text-emerald-300"
              >
                <Check size={11} />
              </button>
              <button onClick={() => setEditDate(false)} className="text-stone-500 hover:text-stone-300">
                <X size={11} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setEditDate(true)}
              className="text-xs text-stone-500 hover:text-stone-300"
            >
              {video.scheduled_for ? video.scheduled_for.slice(0, 10) : 'Schedule'}
            </button>
          )}
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="pt-3 border-t border-stone-800 space-y-3">
          {video.topic && (
            <p className="text-stone-400 text-xs leading-relaxed">{video.topic}</p>
          )}
          {video.notes && (
            <p className="text-stone-500 text-xs italic">{video.notes}</p>
          )}

          {/* Engagement stats (show when posted) */}
          {video.caption_status === 'posted' && engagementTotal > 0 && (
            <div className="grid grid-cols-4 gap-2 pt-1">
              {[
                { label: 'IG Likes', value: video.ig_likes, field: 'ig_likes' },
                { label: 'IG Saves', value: video.ig_saves, field: 'ig_saves' },
                { label: 'IG Comments', value: video.ig_comments, field: 'ig_comments' },
                { label: 'TikTok Views', value: video.tiktok_views, field: 'tiktok_views' },
              ].map(({ label, value, field }) => (
                <div key={field} className="bg-stone-800/60 rounded-lg p-2 text-center">
                  <p className="text-stone-100 text-sm font-heading font-bold">{value}</p>
                  <p className="text-stone-600 text-xs">{label}</p>
                </div>
              ))}
            </div>
          )}

          {video.caption_status === 'posted' && engagementTotal === 0 && (
            <p className="text-stone-600 text-xs">Add engagement stats to track performance.</p>
          )}
        </div>
      )}
    </div>
  )
}

// ── Main Page ──────────────────────────────────────────────────────────────────
export default function ContentCalendar() {
  const [filter, setFilter] = useState<'all' | 're' | 'gymnastics'>('all')
  const [showAdd, setShowAdd] = useState(false)

  const pullMetricsMutation = useMutation({
    mutationFn: () => api.metricool.pullMetrics(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['video-tracker'] })
      alert(`Synced ${data.updated} videos from Metricool.`)
    },
  })

  const { data, isLoading } = useQuery({
    queryKey: ['video-tracker', filter],
    queryFn: () => api.videoTracker.list(filter === 'all' ? undefined : filter),
  })

  const videos = data?.videos ?? []

  const filmed      = videos.filter(v => v.film_status === 'filmed').length
  const notFilmed   = videos.filter(v => v.film_status === 'not_filmed').length
  const edited      = videos.filter(v => v.edit_status !== 'raw').length
  const posted      = videos.filter(v => v.caption_status === 'posted').length

  const reVideos  = videos.filter(v => v.category === 're')
  const gymVideos = videos.filter(v => v.category === 'gymnastics')

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-heading text-xl font-bold text-stone-100">Content Calendar</h1>
          <p className="text-stone-500 text-sm">Video pipeline — from filming to posted</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => pullMetricsMutation.mutate()}
            disabled={pullMetricsMutation.isPending}
            className="btn-ghost border border-stone-700 flex items-center gap-2 text-sm"
            title="Pull latest engagement stats from Metricool"
          >
            <RefreshCw size={13} className={pullMetricsMutation.isPending ? 'animate-spin' : ''} />
            Sync Metrics
          </button>
          <button
            onClick={() => setShowAdd(true)}
            className="btn-primary flex items-center gap-2 text-sm"
          >
            <Plus size={14} />
            Add Video
          </button>
        </div>
      </div>

      {showAdd && <AddVideoModal onClose={() => setShowAdd(false)} />}

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-emerald-400">{filmed}</p>
          <p className="text-stone-500 text-xs">Filmed</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-stone-400">{notFilmed}</p>
          <p className="text-stone-500 text-xs">Not Filmed</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-amber-400">{edited}</p>
          <p className="text-stone-500 text-xs">In Editing+</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-purple-400">{posted}</p>
          <p className="text-stone-500 text-xs">Posted</p>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1 border-b border-stone-800">
        {([
          { key: 'all',        label: `All (${videos.length})` },
          { key: 're',         label: `Real Estate (${reVideos.length})` },
          { key: 'gymnastics', label: `GymnastDiva (${gymVideos.length})` },
        ] as { key: typeof filter; label: string }[]).map(t => (
          <button
            key={t.key}
            onClick={() => setFilter(t.key)}
            className={cn(
              'px-4 py-2.5 text-sm transition-colors border-b-2 -mb-px',
              filter === t.key
                ? 'border-emerald-500 text-emerald-400 font-medium'
                : 'border-transparent text-stone-400 hover:text-stone-100'
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Hint */}
      <p className="text-stone-600 text-xs">Click any status badge to advance it. Click "Schedule" to set a post date.</p>

      {/* Video list */}
      {isLoading ? (
        <p className="text-stone-500 text-sm">Loading...</p>
      ) : videos.length === 0 ? (
        <div className="card text-center py-10">
          <Film size={20} className="text-stone-600 mx-auto mb-2" />
          <p className="text-stone-500 text-sm">No videos yet. Click "Add Video" to start tracking.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {videos.map(v => <VideoRow key={v.id} video={v} />)}
        </div>
      )}
    </div>
  )
}
