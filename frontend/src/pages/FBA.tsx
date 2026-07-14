import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Package, CheckCircle2, XCircle, Clock, Plus, Trash2, X, Search, Lightbulb, Copy, Check, FileText } from 'lucide-react'
import { api, type FBABrand, type FBADistributor } from '../lib/api'
import { cn, formatDate } from '../lib/utils'

const STATUS_STYLES = {
  pending:  { bar: 'bg-amber-500',   badge: 'bg-amber-900/40 text-amber-400',   icon: Clock,        label: 'Pending' },
  approved: { bar: 'bg-emerald-500', badge: 'bg-emerald-900/40 text-emerald-400', icon: CheckCircle2, label: 'Approved' },
  denied:   { bar: 'bg-red-500',     badge: 'bg-red-900/40 text-red-400',        icon: XCircle,      label: 'Denied' },
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }}
      className="btn-ghost p-1.5 flex items-center gap-1 text-xs"
      title="Copy"
    >
      {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  )
}

// ── Add Brand Modal ───────────────────────────────────────────────────────────
function AddBrandModal({ distributors, onClose }: { distributors: FBADistributor[]; onClose: () => void }) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({ name: '', distributor: distributors[0]?.name ?? '', notes: '' })

  const addMutation = useMutation({
    mutationFn: () => api.fba.brands.add(form),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['fba-brands'] }); onClose() },
  })

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-stone-900 border border-stone-700 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-heading font-semibold text-stone-100">Add Brand Approval</h3>
          <button onClick={onClose} className="btn-ghost p-1"><X size={16} /></button>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Brand Name</label>
            <input
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="e.g. Energizer, Dove, Clorox"
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
            />
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Distributor</label>
            <select
              value={form.distributor}
              onChange={e => setForm(f => ({ ...f, distributor: e.target.value }))}
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
            >
              {distributors.map(d => <option key={d.id} value={d.name}>{d.name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Notes (optional)</label>
            <input
              value={form.notes}
              onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              placeholder="e.g. Submitted via Seller Central, waiting on invoice"
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-5">
          <button
            onClick={() => addMutation.mutate()}
            disabled={!form.name.trim() || addMutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={14} />
            {addMutation.isPending ? 'Adding...' : 'Add Brand'}
          </button>
          <button onClick={onClose} className="btn-ghost border border-stone-700">Cancel</button>
        </div>
      </div>
    </div>
  )
}

// ── Brand Approvals ───────────────────────────────────────────────────────────
function BrandApprovals() {
  const queryClient = useQueryClient()
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'denied'>('all')
  const [showAdd, setShowAdd] = useState(false)
  const [expanded, setExpanded] = useState<string | null>(null)

  const { data: brandsData, isLoading: brandsLoading } = useQuery({
    queryKey: ['fba-brands'],
    queryFn: api.fba.brands.list,
  })
  const { data: distData } = useQuery({ queryKey: ['fba-distributors'], queryFn: api.fba.distributors.list })

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => api.fba.brands.updateStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['fba-brands'] }),
  })

  const researchMutation = useMutation({
    mutationFn: (id: string) => api.fba.brands.research(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['fba-brands'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.fba.brands.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['fba-brands'] }),
  })

  const brands = brandsData?.brands ?? []
  const distributors = distData?.distributors ?? []
  const filtered = filter === 'all' ? brands : brands.filter(b => b.status === filter)

  return (
    <div className="space-y-4">
      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        {(['pending', 'approved', 'denied'] as const).map(s => {
          const count = brands.filter(b => b.status === s).length
          const style = STATUS_STYLES[s]
          return (
            <button
              key={s}
              onClick={() => setFilter(filter === s ? 'all' : s)}
              className={cn('card text-center transition-all', filter === s ? 'ring-1 ring-emerald-600' : '')}
            >
              <p className={cn('text-2xl font-heading font-bold', style.badge.split(' ')[1])}>{count}</p>
              <p className="text-stone-500 text-xs capitalize">{s}</p>
            </button>
          )
        })}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-stone-500 text-xs">{filtered.length} brand{filtered.length !== 1 ? 's' : ''}</p>
        <button onClick={() => setShowAdd(true)} className="btn-primary text-xs flex items-center gap-1.5 px-3 py-1.5">
          <Plus size={12} /> Add Brand
        </button>
      </div>

      {showAdd && <AddBrandModal distributors={distributors} onClose={() => setShowAdd(false)} />}

      {brandsLoading ? (
        <p className="text-stone-500 text-sm">Loading brands...</p>
      ) : filtered.length === 0 ? (
        <div className="card text-center py-10">
          <Package size={20} className="text-stone-600 mx-auto mb-2" />
          <p className="text-stone-500 text-sm">No brands tracked yet.</p>
          <p className="text-stone-600 text-xs mt-1">Add every brand you are waiting on approval for.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map(brand => {
            const style = STATUS_STYLES[brand.status]
            const Icon = style.icon
            const isExpanded = expanded === brand.id
            const isResearching = researchMutation.isPending && researchMutation.variables === brand.id

            return (
              <div key={brand.id} className="card overflow-hidden">
                <div className={cn('h-0.5 -mx-4 -mt-4 mb-4', style.bar)} />
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className={cn('p-1.5 rounded-lg mt-0.5', style.badge.split(' ')[0])}>
                      <Icon size={13} className={style.badge.split(' ')[1]} />
                    </div>
                    <div className="min-w-0">
                      <p className="text-stone-100 text-sm font-medium">{brand.name}</p>
                      <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                        <span className={cn('badge text-xs', style.badge)}>{style.label}</span>
                        <span className="text-stone-500 text-xs">{brand.distributor}</span>
                        <span className="text-stone-600 text-xs">Added {formatDate(brand.date_submitted)}</span>
                      </div>
                      {brand.notes && <p className="text-stone-500 text-xs mt-1">{brand.notes}</p>}
                    </div>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      onClick={() => setExpanded(isExpanded ? null : brand.id)}
                      className="text-stone-500 hover:text-stone-100 text-xs px-2"
                    >
                      {isExpanded ? 'Hide' : 'Details'}
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(brand.id)}
                      className="btn-ghost p-1 text-stone-600 hover:text-red-400"
                      title="Remove"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="mt-3 pt-3 border-t border-stone-800 space-y-3">
                    {/* Status actions */}
                    <div className="flex gap-2 flex-wrap">
                      {brand.status !== 'approved' && (
                        <button
                          onClick={() => statusMutation.mutate({ id: brand.id, status: 'approved' })}
                          className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1"
                        >
                          <CheckCircle2 size={11} /> Mark Approved
                        </button>
                      )}
                      {brand.status !== 'denied' && (
                        <button
                          onClick={() => statusMutation.mutate({ id: brand.id, status: 'denied' })}
                          className="btn-ghost border border-stone-700 text-xs px-3 py-1.5 flex items-center gap-1 text-red-400 hover:text-red-300"
                        >
                          <XCircle size={11} /> Mark Denied
                        </button>
                      )}
                      {brand.status !== 'pending' && (
                        <button
                          onClick={() => statusMutation.mutate({ id: brand.id, status: 'pending' })}
                          className="btn-ghost border border-stone-700 text-xs px-3 py-1.5 flex items-center gap-1"
                        >
                          <Clock size={11} /> Reset to Pending
                        </button>
                      )}
                      <button
                        onClick={() => researchMutation.mutate(brand.id)}
                        disabled={isResearching}
                        className="btn-ghost border border-emerald-700/50 text-xs px-3 py-1.5 flex items-center gap-1 text-emerald-400 hover:text-emerald-300"
                      >
                        <Search size={11} />
                        {isResearching ? 'Researching...' : brand.research ? 'Re-Research' : 'AI Research'}
                      </button>
                    </div>

                    {/* Research output */}
                    {brand.research && (
                      <div className="bg-stone-800/60 rounded-xl p-3 space-y-2">
                        <div className="flex items-center justify-between">
                          <p className="text-emerald-400 text-xs font-medium flex items-center gap-1">
                            <Search size={11} /> AI Research
                            {brand.researched_at && <span className="text-stone-600 font-normal ml-1">{formatDate(brand.researched_at)}</span>}
                          </p>
                          <CopyButton text={brand.research} />
                        </div>
                        <p className="text-stone-300 text-xs leading-relaxed whitespace-pre-wrap">{brand.research}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

const ACCT_STATUS = {
  no_account: { label: 'No Account',    badge: 'bg-stone-700 text-stone-400' },
  applied:    { label: 'Applied',       badge: 'bg-amber-900/40 text-amber-400' },
  active:     { label: 'Active',        badge: 'bg-emerald-900/40 text-emerald-400' },
}

// ── Distributors ──────────────────────────────────────────────────────────────
function Distributors() {
  const queryClient = useQueryClient()
  const [showAdd, setShowAdd] = useState(false)
  const [emailResult, setEmailResult] = useState<{ id: string; text: string } | null>(null)
  const [form, setForm] = useState({ name: '', contact: '', website: '', notes: '' })

  const { data, isLoading } = useQuery({ queryKey: ['fba-distributors'], queryFn: api.fba.distributors.list })

  const addMutation = useMutation({
    mutationFn: () => api.fba.distributors.add(form),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['fba-distributors'] }); setShowAdd(false); setForm({ name: '', contact: '', website: '', notes: '' }) },
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => api.fba.distributors.updateStatus(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['fba-distributors'] }),
  })

  const emailMutation = useMutation({
    mutationFn: (id: string) => api.fba.distributors.applicationEmail(id),
    onSuccess: (data, id) => setEmailResult({ id, text: data.email }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.fba.distributors.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['fba-distributors'] }),
  })

  const distributors = data?.distributors ?? []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-stone-500 text-xs">{distributors.filter(d => d.account_status === 'active').length} active · {distributors.filter(d => d.account_status === 'applied').length} applied · {distributors.filter(d => d.account_status === 'no_account').length} need account</p>
        <button onClick={() => setShowAdd(!showAdd)} className="btn-ghost border border-stone-700 text-xs flex items-center gap-1.5 px-3 py-1.5">
          <Plus size={12} /> Add Distributor
        </button>
      </div>

      {showAdd && (
        <div className="card space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Name</label>
              <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="Distributor name" className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600" />
            </div>
            <div>
              <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Contact</label>
              <input value={form.contact} onChange={e => setForm(f => ({ ...f, contact: e.target.value }))} placeholder="Email or phone" className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600" />
            </div>
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Notes</label>
            <input value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} placeholder="Best categories, ordering notes..." className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600" />
          </div>
          <div className="flex gap-2">
            <button onClick={() => addMutation.mutate()} disabled={!form.name.trim() || addMutation.isPending} className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1"><Plus size={12} />{addMutation.isPending ? 'Adding...' : 'Add'}</button>
            <button onClick={() => setShowAdd(false)} className="btn-ghost border border-stone-700 text-xs px-3 py-1.5">Cancel</button>
          </div>
        </div>
      )}

      {isLoading ? (
        <p className="text-stone-500 text-sm">Loading...</p>
      ) : (
        <div className="space-y-3">
          {distributors.map(d => {
            const acct = ACCT_STATUS[d.account_status ?? 'no_account']
            const isGeneratingEmail = emailMutation.isPending && emailMutation.variables === d.id
            return (
              <div key={d.id} className="card space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-stone-100 text-sm font-medium">{d.name}</p>
                      <span className={cn('badge text-xs', acct.badge)}>{acct.label}</span>
                    </div>
                    {d.contact && <p className="text-stone-400 text-xs mt-0.5">{d.contact}</p>}
                    {d.notes && <p className="text-stone-500 text-xs mt-0.5">{d.notes}</p>}
                  </div>
                  <button onClick={() => deleteMutation.mutate(d.id)} className="btn-ghost p-1 text-stone-600 hover:text-red-400">
                    <Trash2 size={13} />
                  </button>
                </div>

                {/* Actions */}
                <div className="flex gap-2 flex-wrap">
                  {d.account_status !== 'active' && (
                    <>
                      <button
                        onClick={() => emailMutation.mutate(d.id)}
                        disabled={isGeneratingEmail}
                        className="btn-ghost border border-emerald-700/50 text-xs px-3 py-1.5 flex items-center gap-1 text-emerald-400 hover:text-emerald-300"
                      >
                        {isGeneratingEmail ? 'Writing...' : 'Draft Application Email'}
                      </button>
                      <button
                        onClick={() => statusMutation.mutate({ id: d.id, status: 'active' })}
                        className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1"
                      >
                        <CheckCircle2 size={11} /> I Have an Account
                      </button>
                      {d.account_status === 'no_account' && (
                        <button onClick={() => statusMutation.mutate({ id: d.id, status: 'applied' })} className="btn-ghost border border-stone-700 text-xs px-3 py-1.5 flex items-center gap-1">
                          <Clock size={11} /> Mark Applied
                        </button>
                      )}
                    </>
                  )}
                  {d.account_status === 'active' && (
                    <span className="text-emerald-400 text-xs flex items-center gap-1">
                      <CheckCircle2 size={11} /> Account active
                    </span>
                  )}
                </div>

                {/* Email output */}
                {emailResult?.id === d.id && (
                  <div className="bg-stone-800/60 rounded-xl p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <p className="text-emerald-400 text-xs font-medium">Application Email — {d.name}</p>
                      <CopyButton text={emailResult.text} />
                    </div>
                    <p className="text-stone-300 text-xs leading-relaxed whitespace-pre-wrap">{emailResult.text}</p>
                    <button
                      onClick={() => statusMutation.mutate({ id: d.id, status: 'applied' })}
                      className="btn-ghost border border-stone-700 text-xs px-3 py-1.5 flex items-center gap-1"
                    >
                      <Clock size={11} /> I sent this — mark as Applied
                    </button>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ── Setup Guide ───────────────────────────────────────────────────────────────
function SetupGuide() {
  const [checklist, setChecklist] = useState<string | null>(null)
  const [starters, setStarters] = useState<string | null>(null)

  const checklistMutation = useMutation({
    mutationFn: api.fba.setup.checklist,
    onSuccess: data => setChecklist(data.checklist),
  })

  const startersMutation = useMutation({
    mutationFn: api.fba.setup.starterDistributors,
    onSuccess: data => setStarters(data.suggestions),
  })

  return (
    <div className="space-y-4">
      {/* Document checklist */}
      <div className="card space-y-3">
        <div className="flex items-center gap-2">
          <FileText size={15} className="text-emerald-400" />
          <h3 className="font-heading font-semibold text-stone-100 text-sm">Document Checklist</h3>
        </div>
        <p className="text-stone-500 text-xs">Every document you need to gather before applying to any wholesale distributor — with how to get each one in Texas.</p>
        <button
          onClick={() => checklistMutation.mutate()}
          disabled={checklistMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          {checklistMutation.isPending ? 'Loading...' : 'Get Document Checklist'}
        </button>
        {checklist && (
          <div className="bg-stone-800/60 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-emerald-400 text-xs font-medium">What You Need</p>
              <CopyButton text={checklist} />
            </div>
            <p className="text-stone-300 text-xs leading-relaxed whitespace-pre-wrap">{checklist}</p>
          </div>
        )}
      </div>

      {/* Starter distributors */}
      <div className="card space-y-3">
        <div className="flex items-center gap-2">
          <Package size={15} className="text-amber-400" />
          <h3 className="font-heading font-semibold text-stone-100 text-sm">Easier Distributors for New Sellers</h3>
        </div>
        <p className="text-stone-500 text-xs">Some wholesale distributors and platforms are much easier to get approved with when you are brand new. Here are the best ones to start with.</p>
        <button
          onClick={() => startersMutation.mutate()}
          disabled={startersMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          {startersMutation.isPending ? 'Researching...' : 'Find Beginner-Friendly Distributors'}
        </button>
        {starters && (
          <div className="bg-stone-800/60 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-amber-400 text-xs font-medium">Starter Distributors</p>
              <CopyButton text={starters} />
            </div>
            <p className="text-stone-300 text-xs leading-relaxed whitespace-pre-wrap">{starters}</p>
          </div>
        )}
      </div>
    </div>
  )
}

const CATEGORIES = [
  '', 'Health & Household', 'Beauty & Personal Care', 'Grocery & Gourmet',
  'Sports & Outdoors', 'Tools & Home Improvement', 'Baby', 'Pet Supplies',
  'Office Products', 'Toys & Games',
]

// ── AI Strategy ───────────────────────────────────────────────────────────────
function AIStrategy() {
  const [advice, setAdvice] = useState<string | null>(null)
  const [chat, setChat] = useState('')
  const [chatResponse, setChatResponse] = useState<string | null>(null)
  const [discoverDist, setDiscoverDist] = useState('Infinity Distribution LLC')
  const [discoverCat, setDiscoverCat] = useState('')
  const [discoverResult, setDiscoverResult] = useState<string | null>(null)

  const { data: distData } = useQuery({ queryKey: ['fba-distributors'], queryFn: api.fba.distributors.list })
  const distributors = distData?.distributors ?? []

  const discoverMutation = useMutation({
    mutationFn: () => api.fba.discover(discoverDist, discoverCat),
    onSuccess: data => setDiscoverResult(data.brands),
  })

  const prioritizeMutation = useMutation({
    mutationFn: api.fba.prioritize,
    onSuccess: data => setAdvice(data.advice),
  })

  const chatMutation = useMutation({
    mutationFn: () => api.fba.chat(chat),
    onSuccess: data => { setChatResponse(data.response); setChat('') },
  })

  return (
    <div className="space-y-4">

      {/* Brand Discovery — shown first since she has no brands yet */}
      <div className="card space-y-4 border border-emerald-800/30">
        <div className="flex items-center gap-2">
          <Search size={15} className="text-emerald-400" />
          <h3 className="font-heading font-semibold text-stone-100 text-sm">Brand Discovery</h3>
          <span className="text-xs bg-emerald-900/40 text-emerald-400 px-2 py-0.5 rounded-full">Start here</span>
        </div>
        <p className="text-stone-500 text-xs">Pick a distributor and the AI will suggest specific brands that are easy to get approved for and sell well on Amazon — with exactly what you need to submit for each one.</p>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Distributor</label>
            <select
              value={discoverDist}
              onChange={e => setDiscoverDist(e.target.value)}
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
            >
              {distributors.map(d => <option key={d.id} value={d.name}>{d.name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Category (optional)</label>
            <select
              value={discoverCat}
              onChange={e => setDiscoverCat(e.target.value)}
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
            >
              {CATEGORIES.map(c => <option key={c} value={c}>{c || 'Best opportunities (all categories)'}</option>)}
            </select>
          </div>
        </div>

        <button
          onClick={() => discoverMutation.mutate()}
          disabled={discoverMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          <Search size={14} />
          {discoverMutation.isPending ? 'Finding brands...' : 'Find Brands to Pursue'}
        </button>

        {discoverResult && (
          <div className="bg-stone-800/60 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-emerald-400 text-xs font-medium">Brand Opportunities — {discoverDist}</p>
              <CopyButton text={discoverResult} />
            </div>
            <p className="text-stone-300 text-xs leading-relaxed whitespace-pre-wrap">{discoverResult}</p>
          </div>
        )}
      </div>

      {/* Priority Advice */}
      <div className="card space-y-3">
        <div className="flex items-center gap-2">
          <Lightbulb size={15} className="text-amber-400" />
          <h3 className="font-heading font-semibold text-stone-100 text-sm">Priority Advice</h3>
        </div>
        <p className="text-stone-500 text-xs">Once you have brands added, this reviews your list and tells you what to do this week to get approvals fastest.</p>
        <button
          onClick={() => prioritizeMutation.mutate()}
          disabled={prioritizeMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          <Lightbulb size={14} />
          {prioritizeMutation.isPending ? 'Analyzing...' : 'Get Priority Advice'}
        </button>
        {advice && (
          <div className="bg-stone-800/60 rounded-xl p-3 space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-amber-400 text-xs font-medium">FBA Strategy</p>
              <CopyButton text={advice} />
            </div>
            <p className="text-stone-300 text-xs leading-relaxed whitespace-pre-wrap">{advice}</p>
          </div>
        )}
      </div>

      {/* Free chat */}
      <div className="card space-y-3">
        <h3 className="font-heading font-semibold text-stone-100 text-sm">Ask the FBA Manager</h3>
        <textarea
          value={chat}
          onChange={e => setChat(e.target.value)}
          rows={3}
          placeholder="What documents do I need to submit for ungating? How do I find the BSR on a product? What should I look for in Catalist's catalog?"
          className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600 resize-none"
        />
        <button
          onClick={() => chatMutation.mutate()}
          disabled={!chat.trim() || chatMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          {chatMutation.isPending ? 'Thinking...' : 'Ask'}
        </button>
        {chatResponse && (
          <div className="bg-stone-800/60 rounded-xl p-3 space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-emerald-400 text-xs font-medium">FBA Manager</p>
              <CopyButton text={chatResponse} />
            </div>
            <p className="text-stone-300 text-xs leading-relaxed whitespace-pre-wrap">{chatResponse}</p>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function FBA() {
  const [tab, setTab] = useState<'brands' | 'distributors' | 'setup' | 'strategy'>('setup')

  const { data: brandsData } = useQuery({ queryKey: ['fba-brands'], queryFn: api.fba.brands.list })
  const pending = brandsData?.pending ?? 0
  const approved = brandsData?.approved ?? 0

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-heading text-xl font-bold text-stone-100">Amazon FBA</h1>
        <p className="text-stone-500 text-sm">Brand approvals · Distributors · Strategy</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-amber-400">{pending}</p>
          <p className="text-stone-500 text-xs">Awaiting Approval</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-emerald-400">{approved}</p>
          <p className="text-stone-500 text-xs">Approved to Sell</p>
        </div>
        <div className="card text-center">
          <p className="text-2xl font-heading font-bold text-stone-100">{brandsData?.count ?? 0}</p>
          <p className="text-stone-500 text-xs">Total Tracked</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-stone-800">
        {[
          { key: 'setup',        label: 'Get Started' },
          { key: 'distributors', label: 'Distributors' },
          { key: 'brands',       label: `Brands${pending > 0 ? ` (${pending} pending)` : ''}` },
          { key: 'strategy',     label: 'AI Strategy' },
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

      {tab === 'setup'        && <SetupGuide />}
      {tab === 'distributors' && <Distributors />}
      {tab === 'brands'       && <BrandApprovals />}
      {tab === 'strategy'     && <AIStrategy />}
    </div>
  )
}
