import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Home, Users, FileText, CheckCircle2, Clock, AlertCircle, ChevronRight, Copy, Check, X, Share2, Video, Sparkles } from 'lucide-react'
import { api, type Listing, type Transaction, type DraftMemory, type NeighborhoodCaptionResult } from '../lib/api'
import { cn, formatDate, STATUS_COLORS } from '../lib/utils'

const RE_CONTENT_TYPES = [
  { key: 'market_update',    label: 'Market Update' },
  { key: 'buyer_tip',        label: 'Buyer Tip' },
  { key: 'seller_tip',       label: 'Seller Tip' },
  { key: 'personal_brand',   label: 'Personal Brand Story' },
  { key: 'community',        label: 'Community Spotlight' },
  { key: 'testimonial_ask',  label: 'Testimonial Ask' },
  { key: 'call_to_action',   label: 'Call to Action' },
  { key: 'land_education',   label: 'Land Buyer Education' },
]

const PLATFORMS = ['instagram', 'facebook', 'tiktok', 'linkedin'] as const

const PIPELINE_STAGES: { key: string; label: string }[] = [
  { key: 'pending',          label: 'Pending' },
  { key: 'offer_submitted',  label: 'Offer Submitted' },
  { key: 'under_contract',   label: 'Under Contract' },
  { key: 'inspection',       label: 'Inspection' },
  { key: 'closing',          label: 'Closing' },
]

const LISTING_STATUS_COLORS: Record<string, string> = {
  active:           'bg-emerald-900/40 text-emerald-400',
  on_hold:          'bg-amber-900/40 text-amber-400',
  under_contract:   'bg-blue-900/40 text-blue-400',
  pending:          'bg-purple-900/40 text-purple-400',
  sold:             'bg-stone-700 text-stone-400',
  withdrawn:        'bg-red-900/40 text-red-400',
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
      className="btn-ghost p-1"
    >
      {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
    </button>
  )
}

// ── Listings Grid ─────────────────────────────────────────────────────────────
function ListingsGrid() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({ queryKey: ['listings'], queryFn: () => api.listings.list() })
  const listings = data?.listings ?? []

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.listings.update(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['listings'] }),
  })

  if (isLoading) return <p className="text-stone-500 text-sm">Loading listings...</p>

  return (
    <div className="space-y-3">
      {listings.length === 0 && (
        <p className="text-stone-500 text-sm">No listings yet.</p>
      )}
      {listings.map(listing => (
        <div key={listing.id} className="card">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-stone-800 rounded-lg mt-0.5">
                <Home size={14} className="text-emerald-400" />
              </div>
              <div>
                <p className="font-medium text-stone-100 text-sm">{listing.address}</p>
                <p className="text-stone-500 text-xs">{listing.city}, {listing.state} {listing.zip}</p>
                {listing.price && (
                  <p className="text-emerald-400 text-xs font-medium mt-0.5">
                    ${listing.price.toLocaleString()}
                  </p>
                )}
                {listing.notes && (
                  <p className="text-stone-500 text-xs mt-1 leading-relaxed">{listing.notes}</p>
                )}
              </div>
            </div>
            <div className="flex flex-col items-end gap-2 shrink-0">
              <span className={cn('badge text-xs', LISTING_STATUS_COLORS[listing.status] ?? 'bg-stone-700 text-stone-400')}>
                {listing.status.replace('_', ' ')}
              </span>
              {listing.mls_number && (
                <p className="text-stone-600 text-xs">MLS# {listing.mls_number}</p>
              )}
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-stone-800 flex gap-2">
            {['active', 'on_hold', 'under_contract', 'sold'].map(s => (
              <button
                key={s}
                onClick={() => updateMutation.mutate({ id: listing.id, status: s })}
                disabled={listing.status === s || updateMutation.isPending}
                className={cn(
                  'text-xs px-2 py-1 rounded-md transition-colors',
                  listing.status === s
                    ? 'bg-stone-700 text-stone-300 cursor-default'
                    : 'bg-stone-800 text-stone-400 hover:text-stone-100 hover:bg-stone-700'
                )}
              >
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Transaction Pipeline ──────────────────────────────────────────────────────
function TransactionPipeline() {
  const queryClient = useQueryClient()
  const { data: pipeline, isLoading } = useQuery({
    queryKey: ['pipeline'],
    queryFn: api.transactions.pipeline,
  })

  const advanceMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.transactions.updateStatus(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pipeline'] }),
  })

  if (isLoading) return <p className="text-stone-500 text-sm">Loading pipeline...</p>

  const total = pipeline ? Object.values(pipeline).flat().length : 0

  if (total === 0) {
    return (
      <div className="card text-center py-8">
        <p className="text-stone-500 text-sm">No active transactions.</p>
      </div>
    )
  }

  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {PIPELINE_STAGES.map(stage => {
        const cards = pipeline?.[stage.key] ?? []
        return (
          <div key={stage.key} className="shrink-0 w-52">
            <div className="flex items-center justify-between mb-2">
              <p className="text-stone-400 text-xs font-medium uppercase tracking-wide">{stage.label}</p>
              {cards.length > 0 && (
                <span className="text-xs bg-stone-800 text-stone-400 px-1.5 py-0.5 rounded-full">
                  {cards.length}
                </span>
              )}
            </div>
            <div className="space-y-2 min-h-[80px]">
              {cards.map(tx => {
                const leadName = tx.leads
                  ? `${tx.leads.first_name} ${tx.leads.last_name}`
                  : null
                const address = tx.listings?.address ?? 'No address'
                const currentIdx = PIPELINE_STAGES.findIndex(s => s.key === stage.key)
                const nextStage = PIPELINE_STAGES[currentIdx + 1]

                return (
                  <div key={tx.id} className="bg-stone-800 rounded-lg p-3 text-xs">
                    <p className="text-stone-100 font-medium leading-snug">{address}</p>
                    {leadName && <p className="text-stone-500 mt-0.5">{leadName}</p>}
                    {tx.contract_price && (
                      <p className="text-emerald-400 mt-1">${tx.contract_price.toLocaleString()}</p>
                    )}
                    {tx.closing_date && (
                      <p className="text-stone-500 mt-0.5 flex items-center gap-1">
                        <Clock size={10} />
                        Closes {formatDate(tx.closing_date)}
                      </p>
                    )}
                    {nextStage && (
                      <button
                        onClick={() => advanceMutation.mutate({ id: tx.id, status: nextStage.key })}
                        disabled={advanceMutation.isPending}
                        className="mt-2 flex items-center gap-1 text-emerald-400 hover:text-emerald-300 transition-colors"
                      >
                        Move to {nextStage.label}
                        <ChevronRight size={10} />
                      </button>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ── Draft Review Queue ────────────────────────────────────────────────────────
function DraftQueue() {
  const queryClient = useQueryClient()
  const [expanded, setExpanded] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['drafts'],
    queryFn: api.transactions.drafts.list,
  })

  const approveMutation = useMutation({
    mutationFn: (key: string) => api.transactions.drafts.approve(key),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['drafts'] }),
  })

  const drafts = (data?.drafts ?? []).filter(d => d.value.status === 'pending_review')
  const approved = (data?.drafts ?? []).filter(d => d.value.status === 'approved')

  if (isLoading) return <p className="text-stone-500 text-sm">Loading drafts...</p>

  if (drafts.length === 0 && approved.length === 0) {
    return (
      <div className="card text-center py-8">
        <p className="text-stone-500 text-sm">No agreement drafts yet. Use the Leads page to draft agreements.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {drafts.length > 0 && (
        <div className="flex items-center gap-2 mb-1">
          <AlertCircle size={13} className="text-amber-400" />
          <p className="text-amber-400 text-xs font-medium">{drafts.length} pending Jennifer's review</p>
        </div>
      )}
      {[...drafts, ...approved].map(draft => (
        <div
          key={draft.key}
          className={cn(
            'card border',
            draft.value.status === 'approved'
              ? 'border-emerald-800/40 bg-emerald-950/10'
              : 'border-amber-800/30 bg-amber-950/10'
          )}
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <FileText size={13} className={draft.value.status === 'approved' ? 'text-emerald-400' : 'text-amber-400'} />
                <p className="text-stone-100 text-sm font-medium capitalize">
                  {draft.value.draft_type.replace(/_/g, ' ')}
                </p>
                <span className={cn(
                  'text-xs px-1.5 py-0.5 rounded-full',
                  draft.value.status === 'approved'
                    ? 'bg-emerald-900/50 text-emerald-400'
                    : 'bg-amber-900/30 text-amber-400'
                )}>
                  {draft.value.status === 'approved' ? 'Approved' : 'Pending Review'}
                </span>
              </div>
              <p className="text-stone-500 text-xs mt-1">{formatDate(draft.value.created_at)}</p>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              <CopyButton text={draft.value.content} />
              <button
                onClick={() => setExpanded(expanded === draft.key ? null : draft.key)}
                className="btn-ghost p-1 text-xs text-stone-400"
              >
                {expanded === draft.key ? 'Hide' : 'View'}
              </button>
              {draft.value.status === 'pending_review' && (
                <button
                  onClick={() => approveMutation.mutate(draft.key)}
                  disabled={approveMutation.isPending}
                  className="btn-primary text-xs px-2 py-1 flex items-center gap-1"
                >
                  <CheckCircle2 size={12} />
                  Approve
                </button>
              )}
            </div>
          </div>

          {expanded === draft.key && (
            <div className="mt-3 pt-3 border-t border-stone-800">
              <pre className="text-stone-300 text-xs whitespace-pre-wrap leading-relaxed font-body">
                {draft.value.content}
              </pre>
              {draft.value.status === 'approved' && (
                <p className="text-emerald-400 text-xs mt-3 flex items-center gap-1">
                  <CheckCircle2 size={11} />
                  Approved {draft.value.approved_at ? formatDate(draft.value.approved_at) : ''} — execute in Lone Wolf Transactions
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

// ── Social Content Generator ──────────────────────────────────────────────────
function SocialContent() {
  const [contentType, setContentType] = useState('market_update')
  const [platform, setPlatform] = useState<typeof PLATFORMS[number]>('instagram')
  const [context, setContext] = useState('')
  const [result, setResult] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const generateMutation = useMutation({
    mutationFn: () => api.realEstate.social({ content_type: contentType, platform, context }),
    onSuccess: data => { setResult(data.post); setCopied(false) },
  })

  const copyPost = () => {
    if (result) { navigator.clipboard.writeText(result); setCopied(true); setTimeout(() => setCopied(false), 2000) }
  }

  const PLATFORM_COLORS: Record<string, string> = {
    instagram: 'bg-pink-900/30 text-pink-400 border-pink-800/40',
    facebook:  'bg-blue-900/30 text-blue-400 border-blue-800/40',
    tiktok:    'bg-stone-700 text-stone-200 border-stone-600',
    linkedin:  'bg-sky-900/30 text-sky-400 border-sky-800/40',
  }

  return (
    <div className="space-y-5">
      <div className="card space-y-4">
        <div className="flex items-center gap-2">
          <Share2 size={15} className="text-emerald-400" />
          <h3 className="font-heading font-semibold text-stone-100 text-sm">Real Estate Post Generator</h3>
        </div>
        <p className="text-stone-500 text-xs">Generate branded posts to grow your pipeline on social media. All posts follow your brand voice — warm, authentic, no AI-sounding phrases.</p>

        {/* Platform selector */}
        <div>
          <label className="text-stone-500 text-xs uppercase tracking-wide block mb-2">Platform</label>
          <div className="flex gap-2 flex-wrap">
            {PLATFORMS.map(p => (
              <button
                key={p}
                onClick={() => setPlatform(p)}
                className={cn(
                  'text-xs px-3 py-1.5 rounded-full border capitalize transition-colors',
                  platform === p
                    ? PLATFORM_COLORS[p]
                    : 'bg-stone-800 text-stone-400 border-stone-700 hover:text-stone-100'
                )}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Content type */}
        <div>
          <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Content Type</label>
          <select
            value={contentType}
            onChange={e => setContentType(e.target.value)}
            className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
          >
            {RE_CONTENT_TYPES.map(t => (
              <option key={t.key} value={t.key}>{t.label}</option>
            ))}
          </select>
        </div>

        {/* Optional context */}
        <div>
          <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">
            Add Context <span className="text-stone-600 normal-case">(optional — specific details, local area, recent experience)</span>
          </label>
          <textarea
            value={context}
            onChange={e => setContext(e.target.value)}
            rows={2}
            placeholder="e.g. Pearland home values up 4% this quarter · first-time buyer just closed in Katy · teaching analogy about reading the fine print..."
            className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600 resize-none"
          />
        </div>

        <button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          <Share2 size={14} />
          {generateMutation.isPending ? 'Writing your post...' : 'Generate Post'}
        </button>
      </div>

      {result && (
        <div className="card space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={cn('text-xs px-2 py-0.5 rounded-full border capitalize', PLATFORM_COLORS[platform])}>
                {platform}
              </span>
              <span className="text-stone-500 text-xs capitalize">{RE_CONTENT_TYPES.find(t => t.key === contentType)?.label}</span>
            </div>
            <button
              onClick={copyPost}
              className="btn-ghost text-xs flex items-center gap-1.5 px-3 py-1.5"
            >
              {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
              {copied ? 'Copied!' : 'Copy Post'}
            </button>
          </div>
          <div className="bg-stone-800/60 rounded-xl p-4">
            <p className="text-stone-200 text-sm leading-relaxed whitespace-pre-wrap">{result}</p>
          </div>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="btn-ghost border border-stone-700 text-xs"
          >
            {generateMutation.isPending ? 'Regenerating...' : 'Generate Another'}
          </button>
        </div>
      )}
    </div>
  )
}

// ── Neighborhood Caption Generator ───────────────────────────────────────────
const NEIGHBORHOODS = [
  { key: 'Meridian',             label: 'Meridian (Manvel)' },
  { key: 'Pomona',               label: 'Pomona (Manvel)' },
  { key: 'Rosharon - Sierra Vista', label: 'Rosharon — Sierra Vista (you live here)' },
  { key: 'Iowa Colony',          label: 'Iowa Colony' },
]

const PLATFORM_LABELS: Record<string, string> = {
  instagram:           'Instagram Caption',
  tiktok:              'TikTok Caption',
  youtube_title:       'YouTube Title',
  youtube_description: 'YouTube Description',
  facebook:            'Facebook Caption',
}

const PLATFORM_COLORS: Record<string, string> = {
  instagram:           'bg-pink-900/30 text-pink-400',
  tiktok:              'bg-stone-700 text-stone-200',
  youtube_title:       'bg-red-900/30 text-red-400',
  youtube_description: 'bg-red-900/30 text-red-400',
  facebook:            'bg-blue-900/30 text-blue-400',
}

function PlatformCaption({ platform, text }: { platform: string; text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <div className="bg-stone-800/50 rounded-xl p-3 space-y-2">
      <div className="flex items-center justify-between">
        <span className={cn('text-xs font-medium px-2 py-0.5 rounded-full', PLATFORM_COLORS[platform] ?? 'bg-stone-700 text-stone-400')}>
          {PLATFORM_LABELS[platform] ?? platform}
        </span>
        <button
          onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
          className="btn-ghost p-1 flex items-center gap-1 text-xs text-stone-400"
        >
          {copied ? <Check size={11} className="text-emerald-400" /> : <Copy size={11} />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <p className="text-stone-200 text-xs leading-relaxed whitespace-pre-wrap">{text}</p>
    </div>
  )
}

function NeighborhoodCaptions() {
  const [neighborhood, setNeighborhood] = useState('Meridian')
  const [description, setDescription] = useState('')
  const [result, setResult] = useState<NeighborhoodCaptionResult | null>(null)

  const generateMutation = useMutation({
    mutationFn: () => api.realEstate.neighborhoodCaptions({ neighborhood, description }),
    onSuccess: data => setResult(data),
  })

  const caps = result?.captions ?? {}
  const platformKeys = ['instagram', 'tiktok', 'youtube_title', 'youtube_description', 'facebook'] as const

  return (
    <div className="space-y-5">
      <div className="card space-y-4">
        <div className="flex items-center gap-2">
          <Video size={15} className="text-emerald-400" />
          <h3 className="font-heading font-semibold text-stone-100 text-sm">Neighborhood Video Captions</h3>
        </div>
        <p className="text-stone-500 text-xs">Describe your video and get ready-to-post captions for all 4 platforms — compliant, on-brand, with the HOUSTON CTA baked in.</p>

        <div>
          <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Neighborhood</label>
          <select
            value={neighborhood}
            onChange={e => setNeighborhood(e.target.value)}
            className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
          >
            {NEIGHBORHOODS.map(n => (
              <option key={n.key} value={n.key}>{n.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">
            What's in the video?
          </label>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            rows={3}
            placeholder="e.g. Walking through Meridian's amenity village, showing the resort pool, Adventure Cove water park, and talking about price ranges and Alvin ISD..."
            className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600 resize-none"
          />
        </div>

        <button
          onClick={() => generateMutation.mutate()}
          disabled={!description.trim() || generateMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          <Sparkles size={14} />
          {generateMutation.isPending ? 'Writing captions...' : 'Generate All Platforms'}
        </button>
      </div>

      {result && (
        <div className="space-y-4">
          {/* Platform captions */}
          <div className="space-y-3">
            {platformKeys.map(key => caps[key] ? (
              <PlatformCaption key={key} platform={key} text={caps[key]!} />
            ) : null)}
          </div>

          {/* Hashtags */}
          {result.hashtags.length > 0 && (
            <div className="card space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-stone-400 text-xs font-medium">Hashtags — paste in first comment on Instagram</p>
                <button
                  onClick={() => navigator.clipboard.writeText(result.hashtags.join(' '))}
                  className="btn-ghost p-1 text-xs flex items-center gap-1 text-stone-400"
                >
                  <Copy size={11} /> Copy
                </button>
              </div>
              <p className="text-stone-500 text-xs leading-relaxed">{result.hashtags.join(' ')}</p>
            </div>
          )}

          {/* Compliance notes */}
          {caps.compliance_notes && caps.compliance_notes !== 'CLEAN' && (
            <div className="bg-amber-950/20 border border-amber-800/30 rounded-xl p-3">
              <p className="text-amber-400 text-xs font-medium mb-1">Compliance Notes</p>
              <p className="text-amber-300/70 text-xs leading-relaxed">{caps.compliance_notes}</p>
            </div>
          )}

          {/* KWP */}
          {caps.kwp_qualifying && (
            <p className="text-stone-500 text-xs">KWP Score: {caps.kwp_qualifying}</p>
          )}

          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="btn-ghost border border-stone-700 text-xs"
          >
            {generateMutation.isPending ? 'Regenerating...' : 'Generate Again'}
          </button>
        </div>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function RealEstate() {
  const [tab, setTab] = useState<'pipeline' | 'social' | 'captions'>('pipeline')

  const { data: leadsData } = useQuery({ queryKey: ['leads'], queryFn: api.leads.list })
  const { data: listingsData } = useQuery({ queryKey: ['listings'], queryFn: () => api.listings.list() })
  const { data: txData } = useQuery({ queryKey: ['transactions'], queryFn: api.transactions.list })
  const { data: draftsData } = useQuery({ queryKey: ['drafts'], queryFn: api.transactions.drafts.list })

  const activeLeads = (leadsData ?? []).filter(l => !['closed', 'lost'].includes(l.status)).length
  const activeListings = (listingsData?.listings ?? []).filter(l => l.status !== 'sold').length
  const openTx = txData?.count ?? 0
  const pendingDrafts = (draftsData?.drafts ?? []).filter(d => d.value.status === 'pending_review').length

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-heading text-xl font-bold text-stone-100">Real Estate</h1>
        <p className="text-stone-500 text-sm">Locked In with Kareesa · KW Preferred Pearland TX</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard icon={<Users size={16} className="text-emerald-400" />} label="Active Leads" value={activeLeads} />
        <StatCard icon={<Home size={16} className="text-blue-400" />} label="Listings" value={activeListings} />
        <StatCard icon={<ChevronRight size={16} className="text-purple-400" />} label="Transactions" value={openTx} />
        <StatCard
          icon={<FileText size={16} className="text-amber-400" />}
          label="Drafts to Review"
          value={pendingDrafts}
          highlight={pendingDrafts > 0}
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-stone-800">
        {[
          { key: 'pipeline', label: 'Pipeline' },
          { key: 'captions', label: 'Video Captions' },
          { key: 'social',   label: 'Social Posts' },
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key as typeof tab)}
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

      {tab === 'pipeline' && (
        <div className="space-y-8">
          <section>
            <h2 className="font-heading font-semibold text-stone-100 mb-4">Listings</h2>
            <ListingsGrid />
          </section>

          <section>
            <h2 className="font-heading font-semibold text-stone-100 mb-4">Transaction Pipeline</h2>
            <TransactionPipeline />
          </section>

          <section>
            <div className="flex items-center gap-3 mb-4">
              <h2 className="font-heading font-semibold text-stone-100">Agreement Drafts</h2>
              {pendingDrafts > 0 && (
                <span className="text-xs bg-amber-900/40 text-amber-400 px-2 py-0.5 rounded-full">
                  {pendingDrafts} pending review
                </span>
              )}
            </div>
            <DraftQueue />
          </section>
        </div>
      )}

      {tab === 'captions' && <NeighborhoodCaptions />}
      {tab === 'social' && <SocialContent />}
    </div>
  )
}

function StatCard({
  icon, label, value, highlight = false,
}: {
  icon: React.ReactNode
  label: string
  value: number
  highlight?: boolean
}) {
  return (
    <div className={cn('card flex items-center gap-3', highlight && 'border border-amber-800/40')}>
      <div className="p-2 bg-stone-800 rounded-lg shrink-0">{icon}</div>
      <div>
        <p className="text-2xl font-heading font-bold text-stone-100">{value}</p>
        <p className="text-stone-500 text-xs">{label}</p>
      </div>
    </div>
  )
}
