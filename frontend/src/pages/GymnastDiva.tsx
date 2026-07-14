import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Sparkles, Calendar, CheckCircle2, Archive, Copy, Check, X, BarChart2, Plus, Trash2 } from 'lucide-react'
import { api, type ContentItem, type ContentGenerateResult, type Meet } from '../lib/api'
import { cn, formatDate } from '../lib/utils'

const PLATFORM_ICONS: Record<string, React.ReactNode> = {
  instagram:      <span className="text-xs font-bold leading-none">IG</span>,
  tiktok:         <span className="text-xs font-bold leading-none">TK</span>,
  youtube_shorts: <span className="text-xs font-bold leading-none">YT</span>,
  facebook:       <span className="text-xs font-bold leading-none">FB</span>,
}

const PLATFORM_COLORS: Record<string, string> = {
  instagram:     'bg-pink-900/30 text-pink-400',
  tiktok:        'bg-stone-700 text-stone-200',
  youtube_shorts: 'bg-red-900/30 text-red-400',
  facebook:      'bg-blue-900/30 text-blue-400',
}

const STATUS_COLORS: Record<string, string> = {
  draft:     'bg-stone-700 text-stone-400',
  review:    'bg-amber-900/40 text-amber-400',
  approved:  'bg-emerald-900/40 text-emerald-400',
  scheduled: 'bg-blue-900/40 text-blue-400',
  published: 'bg-purple-900/40 text-purple-400',
  archived:  'bg-stone-800 text-stone-600',
}

const CONTENT_TYPES = ['highlight', 'skills', 'meet_recap', 'motivation', 'lesson_promo']

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
      className="btn-ghost p-1"
      title="Copy"
    >
      {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
    </button>
  )
}

// ── Caption Generator ─────────────────────────────────────────────────────────
function CaptionGenerator() {
  const queryClient = useQueryClient()
  const [description, setDescription] = useState('')
  const [contentType, setContentType] = useState('highlight')
  const [title, setTitle] = useState('')
  const [result, setResult] = useState<ContentGenerateResult | null>(null)

  const generateMutation = useMutation({
    mutationFn: () => api.content.generate({ description, content_type: contentType, title, save: false }),
    onSuccess: (data) => setResult(data),
  })

  const saveMutation = useMutation({
    mutationFn: () => api.content.generate({ description, content_type: contentType, title, save: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content-queue'] })
      setResult(null)
      setDescription('')
      setTitle('')
    },
  })

  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-2 mb-1">
        <Sparkles size={15} className="text-emerald-400" />
        <h3 className="font-heading font-semibold text-stone-100 text-sm">Caption Generator</h3>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Content Type</label>
          <select
            value={contentType}
            onChange={e => setContentType(e.target.value)}
            className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
          >
            {CONTENT_TYPES.map(t => (
              <option key={t} value={t}>{t.replace('_', ' ')}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Title (optional)</label>
          <input
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="e.g. Iyah hits her first double"
            className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
          />
        </div>
      </div>

      <div>
        <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Video Description</label>
        <textarea
          value={description}
          onChange={e => setDescription(e.target.value)}
          rows={3}
          placeholder="Describe what's in the video — skills shown, energy, moment, equipment used..."
          className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600 resize-none"
        />
      </div>

      <button
        onClick={() => generateMutation.mutate()}
        disabled={!description.trim() || generateMutation.isPending}
        className="btn-primary flex items-center gap-2"
      >
        <Sparkles size={14} />
        {generateMutation.isPending ? 'Generating...' : 'Generate Captions'}
      </button>

      {result && (
        <div className="border-t border-stone-800 pt-4 space-y-4">
          {/* Instagram */}
          {result.captions.instagram && (
            <PlatformCaption
              platform="instagram"
              label="Instagram Caption"
              text={result.captions.instagram}
              extra={`Hashtags (first comment):\n${result.hashtags.join(' ')}`}
            />
          )}
          {/* TikTok */}
          {result.captions.tiktok && (
            <PlatformCaption platform="tiktok" label="TikTok Caption" text={result.captions.tiktok} />
          )}
          {/* YouTube */}
          {(result.captions.youtube_title || result.captions.youtube_description) && (
            <PlatformCaption
              platform="youtube_shorts"
              label="YouTube Shorts"
              text={`${result.captions.youtube_title ? `Title: ${result.captions.youtube_title}\n\n` : ''}${result.captions.youtube_description ?? ''}`}
            />
          )}
          {/* Facebook */}
          {result.captions.facebook && (
            <PlatformCaption platform="facebook" label="Facebook Caption" text={result.captions.facebook} />
          )}

          <div className="flex gap-3 pt-2">
            <button
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              className="btn-primary flex items-center gap-2"
            >
              <CheckCircle2 size={14} />
              {saveMutation.isPending ? 'Saving...' : 'Save All to Queue'}
            </button>
            <button onClick={() => setResult(null)} className="btn-ghost border border-stone-700 flex items-center gap-2">
              <X size={14} />
              Discard
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function PlatformCaption({ platform, label, text, extra }: { platform: string; label: string; text: string; extra?: string }) {
  return (
    <div className="bg-stone-800/50 rounded-xl p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={cn('inline-flex items-center justify-center w-5 h-5 rounded-full', PLATFORM_COLORS[platform])}>
            {PLATFORM_ICONS[platform]}
          </span>
          <p className="text-stone-300 text-xs font-medium">{label}</p>
        </div>
        <CopyButton text={extra ? `${text}\n\n${extra}` : text} />
      </div>
      <p className="text-stone-200 text-xs leading-relaxed whitespace-pre-wrap">{text}</p>
      {extra && (
        <p className="text-stone-500 text-xs leading-relaxed whitespace-pre-wrap border-t border-stone-700 pt-2">{extra}</p>
      )}
    </div>
  )
}

// ── Content Queue ─────────────────────────────────────────────────────────────
function ContentQueue() {
  const queryClient = useQueryClient()
  const [filter, setFilter] = useState<string>('all')
  const [expanded, setExpanded] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['content-queue', filter],
    queryFn: () => api.content.queue(filter === 'all' ? undefined : filter),
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.content.updateStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['content-queue'] }),
  })

  const items = data?.items ?? []

  return (
    <div>
      {/* Filter tabs */}
      <div className="flex gap-2 mb-4 flex-wrap">
        {['all', 'draft', 'review', 'approved', 'published'].map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={cn(
              'text-xs px-3 py-1.5 rounded-full transition-colors capitalize',
              filter === s
                ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-600/40'
                : 'bg-stone-800 text-stone-400 hover:text-stone-100'
            )}
          >
            {s}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-stone-500 text-sm">Loading queue...</p>
      ) : items.length === 0 ? (
        <div className="card text-center py-10">
          <p className="text-stone-500 text-sm">No content in queue. Generate some captions above.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map(item => (
            <div key={item.id} className="card">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <span className={cn('inline-flex items-center justify-center w-6 h-6 rounded-full shrink-0', PLATFORM_COLORS[item.platform])}>
                    {PLATFORM_ICONS[item.platform]}
                  </span>
                  <div className="min-w-0">
                    <p className="text-stone-100 text-sm font-medium truncate">
                      {item.title || item.content_type.replace('_', ' ')}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className={cn('badge text-xs', STATUS_COLORS[item.status])}>
                        {item.status}
                      </span>
                      <span className="text-stone-600 text-xs capitalize">{item.content_type.replace('_', ' ')}</span>
                      <span className="text-stone-600 text-xs">{formatDate(item.created_at)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  {item.caption && <CopyButton text={item.caption} />}
                  <button
                    onClick={() => setExpanded(expanded === item.id ? null : item.id)}
                    className="text-stone-500 hover:text-stone-100 text-xs px-2"
                  >
                    {expanded === item.id ? 'Hide' : 'View'}
                  </button>
                </div>
              </div>

              {expanded === item.id && (
                <div className="mt-3 pt-3 border-t border-stone-800 space-y-3">
                  {item.caption && (
                    <p className="text-stone-300 text-xs leading-relaxed whitespace-pre-wrap">{item.caption}</p>
                  )}
                  {item.hashtags && item.hashtags.length > 0 && (
                    <p className="text-stone-500 text-xs">{item.hashtags.join(' ')}</p>
                  )}
                  <div className="flex gap-2 flex-wrap">
                    {item.status === 'draft' && (
                      <button onClick={() => statusMutation.mutate({ id: item.id, status: 'approved' })} className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1">
                        <CheckCircle2 size={11} /> Approve
                      </button>
                    )}
                    {item.status === 'approved' && (
                      <button onClick={() => statusMutation.mutate({ id: item.id, status: 'published' })} className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1">
                        <CheckCircle2 size={11} /> Mark Published
                      </button>
                    )}
                    {!['archived', 'published'].includes(item.status) && (
                      <button onClick={() => statusMutation.mutate({ id: item.id, status: 'archived' })} className="btn-ghost border border-stone-700 text-xs px-3 py-1.5 flex items-center gap-1">
                        <Archive size={11} /> Archive
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Add Meet Modal ─────────────────────────────────────────────────────────────
function AddMeetModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({ date: '', name: '', location: '', discipline: 'All' })

  const addMutation = useMutation({
    mutationFn: () => api.content.meets.add(form as Omit<Meet, 'id'>),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meets'] })
      onClose()
    },
  })

  const DISCIPLINES = ['All', 'Floor', 'Trampoline', 'Rod Floor', 'Black Floor']

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-stone-900 border border-stone-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-heading font-semibold text-stone-100">Add Meet</h3>
          <button onClick={onClose} className="btn-ghost p-1"><X size={16} /></button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Date</label>
            <input
              type="date"
              value={form.date}
              onChange={e => setForm(f => ({ ...f, date: e.target.value }))}
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
            />
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Meet Name</label>
            <input
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="e.g. Houston Invitational"
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
            />
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Location</label>
            <input
              value={form.location}
              onChange={e => setForm(f => ({ ...f, location: e.target.value }))}
              placeholder="e.g. Houston, TX"
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
            />
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Discipline</label>
            <select
              value={form.discipline}
              onChange={e => setForm(f => ({ ...f, discipline: e.target.value }))}
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
            >
              {DISCIPLINES.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button
            onClick={() => addMutation.mutate()}
            disabled={!form.date || !form.name || !form.location || addMutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={14} />
            {addMutation.isPending ? 'Adding...' : 'Add Meet'}
          </button>
          <button onClick={onClose} className="btn-ghost border border-stone-700">Cancel</button>
        </div>
      </div>
    </div>
  )
}

// ── Meet Schedule ─────────────────────────────────────────────────────────────
function MeetSchedule() {
  const queryClient = useQueryClient()
  const [showAdd, setShowAdd] = useState(false)
  const now = new Date()

  const { data, isLoading } = useQuery({
    queryKey: ['meets'],
    queryFn: api.content.meets.list,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.content.meets.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['meets'] }),
  })

  const meets = data?.meets ?? []
  const upcoming = meets.filter(m => new Date(m.date) >= now)
  const past = meets.filter(m => new Date(m.date) < now)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-stone-500 text-xs">{upcoming.length} upcoming · {past.length} past</p>
        <button
          onClick={() => setShowAdd(true)}
          className="btn-primary text-xs flex items-center gap-1.5 px-3 py-1.5"
        >
          <Plus size={12} /> Add Meet
        </button>
      </div>

      {showAdd && <AddMeetModal onClose={() => setShowAdd(false)} />}

      {isLoading ? (
        <p className="text-stone-500 text-sm">Loading schedule...</p>
      ) : meets.length === 0 ? (
        <div className="card text-center py-10">
          <Calendar size={20} className="text-stone-600 mx-auto mb-2" />
          <p className="text-stone-500 text-sm">No meets scheduled yet.</p>
          <p className="text-stone-600 text-xs mt-1">Click "Add Meet" to enter Iyah's real meet dates.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {upcoming.map(meet => {
            const daysOut = Math.ceil((new Date(meet.date).getTime() - now.getTime()) / 86400000)
            return (
              <div key={meet.id} className="card flex items-center justify-between group">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-900/30 rounded-lg">
                    <Calendar size={14} className="text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-stone-100 text-sm font-medium">{meet.name}</p>
                    <p className="text-stone-500 text-xs">{meet.location} · {meet.discipline}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <div className="text-right">
                    <p className="text-stone-300 text-sm">{formatDate(meet.date)}</p>
                    <p className="text-emerald-400 text-xs">{daysOut} days out</p>
                  </div>
                  <button
                    onClick={() => deleteMutation.mutate(meet.id)}
                    className="opacity-0 group-hover:opacity-100 btn-ghost p-1 text-stone-600 hover:text-red-400 transition-opacity"
                    title="Remove meet"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            )
          })}
          {past.length > 0 && (
            <>
              <p className="text-stone-600 text-xs pt-2 pb-1">Past Meets</p>
              {past.map(meet => (
                <div key={meet.id} className="card flex items-center justify-between opacity-40 group">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-stone-800 rounded-lg">
                      <Calendar size={14} className="text-stone-500" />
                    </div>
                    <div>
                      <p className="text-stone-400 text-sm">{meet.name}</p>
                      <p className="text-stone-600 text-xs">{meet.location} · {meet.discipline}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <p className="text-stone-600 text-sm">{formatDate(meet.date)}</p>
                    <button
                      onClick={() => deleteMutation.mutate(meet.id)}
                      className="opacity-0 group-hover:opacity-100 btn-ghost p-1 text-stone-600 hover:text-red-400 transition-opacity"
                      title="Remove meet"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function GymnastDiva() {
  const [tab, setTab] = useState<'generate' | 'queue' | 'schedule' | 'plan'>('generate')

  const { data: queueData } = useQuery({ queryKey: ['content-queue', 'all'], queryFn: () => api.content.queue() })
  const { data: meetsData } = useQuery({ queryKey: ['meets'], queryFn: api.content.meets.list })
  const [weeklyPlan, setWeeklyPlan] = useState<string | null>(null)

  const planMutation = useMutation({
    mutationFn: api.content.weeklyPlan,
    onSuccess: (data) => { setWeeklyPlan(data.plan); setTab('plan') },
  })

  const drafts = (queueData?.items ?? []).filter(i => i.status === 'draft').length
  const approved = (queueData?.items ?? []).filter(i => i.status === 'approved').length
  const published = (queueData?.items ?? []).filter(i => i.status === 'published').length
  const now = new Date()
  const nextMeet = (meetsData?.meets ?? []).find(m => new Date(m.date) >= now)

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-heading text-xl font-bold text-stone-100">GymnastDiva</h1>
          <p className="text-stone-500 text-sm">@GymnastDivaIyah · Iyah Gonzales · Content Engine</p>
        </div>
        <button
          onClick={() => planMutation.mutate()}
          disabled={planMutation.isPending}
          className="btn-ghost border border-stone-700 flex items-center gap-2 text-sm"
        >
          <BarChart2 size={14} />
          {planMutation.isPending ? 'Generating...' : 'Weekly Plan'}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3">
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-stone-100">{drafts}</p>
          <p className="text-stone-500 text-xs">Drafts</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-emerald-400">{approved}</p>
          <p className="text-stone-500 text-xs">Approved</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-purple-400">{published}</p>
          <p className="text-stone-500 text-xs">Published</p>
        </div>
        <div className="card text-center">
          <p className="text-lg font-heading font-bold text-stone-100 leading-tight">
            {nextMeet ? nextMeet.name.split(' ')[0] : '—'}
          </p>
          <p className="text-stone-500 text-xs">Next Meet</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-stone-800">
        {([
          { key: 'generate', label: 'Generate' },
          { key: 'queue',    label: `Queue${queueData?.count ? ` (${queueData.count})` : ''}` },
          { key: 'schedule', label: 'Meet Schedule' },
          ...(weeklyPlan ? [{ key: 'plan', label: 'Weekly Plan' }] : []),
        ] as { key: typeof tab; label: string }[]).map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={cn(
              'px-4 py-2.5 text-sm transition-colors border-b-2 -mb-px',
              tab === t.key
                ? 'border-emerald-500 text-emerald-400 font-medium'
                : 'border-transparent text-stone-400 hover:text-stone-100'
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === 'generate' && <CaptionGenerator />}
      {tab === 'queue' && <ContentQueue />}
      {tab === 'schedule' && <MeetSchedule />}
      {tab === 'plan' && weeklyPlan && (
        <div className="card">
          <pre className="text-stone-300 text-sm whitespace-pre-wrap leading-relaxed font-body">{weeklyPlan}</pre>
        </div>
      )}
    </div>
  )
}
