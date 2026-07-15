import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { UserPlus, X, Phone, Mail, MapPin, Calendar, Send, Copy, Check, Bot } from 'lucide-react'
import { api, type Lead } from '../lib/api'
import { cn, formatDate, timeAgo, STATUS_COLORS } from '../lib/utils'

function AddLeadModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({
    first_name: '', last_name: '', phone: '', email: '',
    source: 'referral', referrer: '', lead_type: 'buyer',
    status: 'new', notes: '',
  })

  const mutation = useMutation({
    mutationFn: () => api.leads.create(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] })
      onClose()
    },
  })

  const field = (key: keyof typeof form, label: string, type = 'text', opts?: string[]) => (
    <div>
      <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">{label}</label>
      {opts ? (
        <select
          value={form[key]}
          onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
          className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
        >
          {opts.map(o => <option key={o} value={o}>{o.replace('_', ' ')}</option>)}
        </select>
      ) : (
        <input
          type={type}
          value={form[key]}
          onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
          className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
        />
      )}
    </div>
  )

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
      <div className="bg-stone-900 border border-stone-800 rounded-xl w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-stone-800">
          <h2 className="font-heading font-bold text-stone-100">Add Lead</h2>
          <button onClick={onClose} className="btn-ghost p-1"><X size={16} /></button>
        </div>
        <div className="px-6 py-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            {field('first_name', 'First Name')}
            {field('last_name', 'Last Name')}
          </div>
          <div className="grid grid-cols-2 gap-3">
            {field('phone', 'Phone', 'tel')}
            {field('email', 'Email', 'email')}
          </div>
          <div className="grid grid-cols-2 gap-3">
            {field('lead_type', 'Type', 'text', ['buyer', 'seller', 'land', 'investor', 'renter'])}
            {field('status', 'Status', 'text', ['new', 'contacted', 'qualified', 'active'])}
          </div>
          <div className="grid grid-cols-2 gap-3">
            {field('source', 'Source', 'text', ['referral', 'har_mls', 'kw_command', 'social', 'direct'])}
            {field('referrer', 'Referred By')}
          </div>
          <div>
            <label className="text-stone-500 text-xs uppercase tracking-wide block mb-1">Notes</label>
            <textarea
              value={form.notes}
              onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              rows={3}
              className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600 resize-none"
            />
          </div>
        </div>
        <div className="px-6 py-4 border-t border-stone-800 flex gap-3 justify-end">
          <button onClick={onClose} className="btn-ghost border border-stone-700">Cancel</button>
          <button
            onClick={() => mutation.mutate()}
            disabled={!form.first_name || !form.last_name || mutation.isPending}
            className="btn-primary"
          >
            {mutation.isPending ? 'Saving...' : 'Add Lead'}
          </button>
        </div>
      </div>
    </div>
  )
}

interface AgentMessage {
  role: 'user' | 'assistant'
  content: string
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button onClick={copy} className="btn-ghost p-1 ml-auto" title="Copy">
      {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
    </button>
  )
}

const SEQUENCE_TRACK_LABELS: Record<string, string> = {
  aicc: 'AICC follow-up (default)',
  smartplan: 'KW Command SmartPlan',
  none: 'No automated outreach',
}

function LeadDrawer({ lead, onClose }: { lead: Lead; onClose: () => void }) {
  const [draft, setDraft] = useState<{ type: string; content: string } | null>(null)
  const [chatMessages, setChatMessages] = useState<AgentMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  const trackMutation = useMutation({
    mutationFn: (sequence_track: string) => api.leads.update(lead.id, { sequence_track: sequence_track as Lead['sequence_track'] }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['leads'] }),
  })

  const draftMutation = useMutation({
    mutationFn: (type: 'text' | 'email' | 'agreement') => {
      const name = `${lead.first_name} ${lead.last_name}`
      const prompts: Record<string, string> = {
        text: `Draft a warm, professional follow-up text message for ${name}. Lead type: ${lead.lead_type ?? 'buyer'}. Notes: ${lead.notes ?? 'none'}. Keep it under 160 characters if possible.`,
        email: `Draft a professional follow-up email for ${name}. Lead type: ${lead.lead_type ?? 'buyer'}. Notes: ${lead.notes ?? 'none'}. Include subject line.`,
        agreement: `Draft a buyer representation agreement outline for ${name}. Lead type: ${lead.lead_type ?? 'buyer'}. Budget: ${lead.budget_min ? `$${lead.budget_min.toLocaleString()}` : 'unspecified'}–${lead.budget_max ? `$${lead.budget_max.toLocaleString()}` : 'unspecified'}. Notes: ${lead.notes ?? 'none'}. Remind me: this is a DRAFT ONLY — I will execute it myself in Lone Wolf.`,
      }
      return api.agents.chat('real_estate', prompts[type])
    },
    onSuccess: (data, type) => {
      setDraft({ type, content: data.response })
    },
  })

  const chatMutation = useMutation({
    mutationFn: (message: string) =>
      api.agents.chat('real_estate', `[Context: Lead is ${lead.first_name} ${lead.last_name}, ${lead.lead_type ?? 'buyer'}, status: ${lead.status}. Notes: ${lead.notes ?? 'none'}]\n\n${message}`),
    onSuccess: (data) => {
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    },
  })

  const sendChat = () => {
    const msg = chatInput.trim()
    if (!msg || chatMutation.isPending) return
    setChatInput('')
    setChatMessages(prev => [...prev, { role: 'user', content: msg }])
    chatMutation.mutate(msg)
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  return (
    <div className="w-full md:w-[420px] border-l border-stone-800 bg-stone-900 flex flex-col h-screen overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-stone-800 flex items-center justify-between shrink-0">
        <div>
          <h2 className="font-heading font-bold text-stone-100">
            {lead.first_name} {lead.last_name}
          </h2>
          <div className="flex gap-2 mt-1">
            <span className={cn('badge', STATUS_COLORS[lead.status] ?? '')}>
              {lead.status.replace('_', ' ')}
            </span>
            {lead.lead_type && (
              <span className="badge bg-stone-700 text-stone-300 capitalize">{lead.lead_type}</span>
            )}
          </div>
        </div>
        <button onClick={onClose} className="btn-ghost p-1">
          <X size={16} />
        </button>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-5">
        {/* Contact Info */}
        <div className="space-y-2 text-sm">
          {lead.phone && (
            <div className="flex items-center gap-2 text-stone-300">
              <Phone size={14} className="text-stone-500" />
              {lead.phone}
            </div>
          )}
          {lead.email && (
            <div className="flex items-center gap-2 text-stone-300">
              <Mail size={14} className="text-stone-500" />
              {lead.email}
            </div>
          )}
          {lead.referrer && (
            <div className="flex items-center gap-2 text-stone-300">
              <MapPin size={14} className="text-stone-500" />
              Referred by {lead.referrer}
            </div>
          )}
          <div className="flex items-center gap-2 text-stone-400">
            <Calendar size={14} className="text-stone-500" />
            Added {formatDate(lead.created_at)} · Last contact {timeAgo(lead.last_contact_at)}
          </div>
        </div>

        {/* Notes */}
        {lead.notes && (
          <div>
            <p className="text-stone-500 text-xs uppercase tracking-wide mb-1">Notes</p>
            <p className="text-stone-300 text-sm leading-relaxed">{lead.notes}</p>
          </div>
        )}

        {/* Budget */}
        {(lead.budget_min || lead.budget_max) && (
          <div>
            <p className="text-stone-500 text-xs uppercase tracking-wide mb-1">Budget</p>
            <p className="text-stone-300 text-sm">
              {lead.budget_min ? `$${lead.budget_min.toLocaleString()}` : '—'}
              {' → '}
              {lead.budget_max ? `$${lead.budget_max.toLocaleString()}` : '—'}
            </p>
          </div>
        )}

        {/* Sequence Track (dedup guard) */}
        <div className="border-t border-stone-800 pt-4">
          <p className="text-stone-500 text-xs uppercase tracking-wide mb-1">Follow-Up Owner</p>
          <p className="text-stone-500 text-xs mb-2">
            Only one system should ever message this lead. Set this to "KW Command SmartPlan"
            the moment you enroll them in a SmartPlan in agent.kw.com &mdash; that stops AICC's
            automated follow-up for them.
          </p>
          <select
            value={lead.sequence_track ?? 'aicc'}
            onChange={e => trackMutation.mutate(e.target.value)}
            disabled={trackMutation.isPending}
            className="w-full bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-sm text-stone-100 focus:outline-none focus:border-emerald-600"
          >
            {Object.entries(SEQUENCE_TRACK_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
          {lead.sequence_track === 'smartplan' && (
            <p className="text-amber-500 text-xs mt-2">
              AICC's hourly follow-up reminder is skipping this lead.
            </p>
          )}
        </div>

        {/* Quick Actions */}
        <div className="border-t border-stone-800 pt-4">
          <p className="text-stone-500 text-xs uppercase tracking-wide mb-3">Quick Actions</p>
          <div className="space-y-2">
            <button
              onClick={() => draftMutation.mutate('text')}
              disabled={draftMutation.isPending}
              className="btn-primary w-full text-sm"
            >
              {draftMutation.isPending && draftMutation.variables === 'text' ? 'Drafting...' : 'Draft Follow-Up Text'}
            </button>
            <button
              onClick={() => draftMutation.mutate('email')}
              disabled={draftMutation.isPending}
              className="btn-ghost w-full border border-stone-700 text-sm"
            >
              {draftMutation.isPending && draftMutation.variables === 'email' ? 'Drafting...' : 'Draft Follow-Up Email'}
            </button>
            <button
              onClick={() => draftMutation.mutate('agreement')}
              disabled={draftMutation.isPending}
              className="btn-ghost w-full border border-stone-700 text-sm"
            >
              {draftMutation.isPending && draftMutation.variables === 'agreement' ? 'Drafting...' : 'Draft Agreement'}
            </button>
          </div>
        </div>

        {/* Draft Output */}
        {draftMutation.isPending && !draft && (
          <div className="bg-stone-800 rounded-xl p-4">
            <div className="flex gap-1">
              <span className="w-1.5 h-1.5 bg-stone-500 rounded-full animate-bounce [animation-delay:0ms]" />
              <span className="w-1.5 h-1.5 bg-stone-500 rounded-full animate-bounce [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 bg-stone-500 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        )}
        {draft && (
          <div className="border border-emerald-800/40 bg-emerald-950/20 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-emerald-400 text-xs font-medium uppercase tracking-wide">
                {draft.type === 'text' ? 'Text Draft' : draft.type === 'email' ? 'Email Draft' : 'Agreement Draft (Review Only)'}
              </p>
              <div className="flex gap-1">
                <CopyButton text={draft.content} />
                <button onClick={() => setDraft(null)} className="btn-ghost p-1">
                  <X size={12} />
                </button>
              </div>
            </div>
            <p className="text-stone-300 text-sm whitespace-pre-wrap leading-relaxed">{draft.content}</p>
            {draft.type === 'agreement' && (
              <p className="text-amber-500 text-xs mt-3 flex items-center gap-1">
                ⚠ Draft only — execute in Lone Wolf yourself, not through this system.
              </p>
            )}
          </div>
        )}

        {/* Agent Chat (scoped to this lead) */}
        <div className="border-t border-stone-800 pt-4">
          <div className="flex items-center gap-2 mb-3">
            <Bot size={14} className="text-emerald-400" />
            <p className="text-stone-500 text-xs uppercase tracking-wide">Ask Real Estate Assistant</p>
          </div>
          <div className="space-y-3 min-h-[60px]">
            {chatMessages.map((msg, i) => (
              <div key={i} className={cn('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                <div
                  className={cn(
                    'max-w-[85%] px-3 py-2 rounded-xl text-xs leading-relaxed whitespace-pre-wrap',
                    msg.role === 'user' ? 'bg-emerald-600 text-white' : 'bg-stone-800 text-stone-200'
                  )}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {chatMutation.isPending && (
              <div className="flex justify-start">
                <div className="bg-stone-800 px-3 py-2 rounded-xl">
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-stone-500 rounded-full animate-bounce [animation-delay:0ms]" />
                    <span className="w-1.5 h-1.5 bg-stone-500 rounded-full animate-bounce [animation-delay:150ms]" />
                    <span className="w-1.5 h-1.5 bg-stone-500 rounded-full animate-bounce [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>
      </div>

      {/* Chat Input */}
      <div className="px-4 py-3 border-t border-stone-800 shrink-0">
        <div className="flex gap-2">
          <input
            value={chatInput}
            onChange={e => setChatInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendChat()}
            placeholder={`Ask about ${lead.first_name}...`}
            className="flex-1 bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-xs text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
          />
          <button onClick={sendChat} disabled={chatMutation.isPending} className="btn-primary px-2.5">
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Leads() {
  const [selected, setSelected] = useState<Lead | null>(null)
  const [showAddLead, setShowAddLead] = useState(false)

  const { data: leads = [], isLoading } = useQuery({
    queryKey: ['leads'],
    queryFn: api.leads.list,
  })

  return (
    <div className="flex h-screen">
      {showAddLead && <AddLeadModal onClose={() => setShowAddLead(false)} />}
      {/* Table */}
      <div className={cn('flex-1 p-6 overflow-y-auto', selected && 'hidden md:block')}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="font-heading text-xl font-bold text-stone-100">Leads</h1>
            <p className="text-stone-500 text-sm">{leads.length} total</p>
          </div>
          <button onClick={() => setShowAddLead(true)} className="btn-primary flex items-center gap-2">
            <UserPlus size={14} />
            Add Lead
          </button>
        </div>

        {isLoading ? (
          <p className="text-stone-500 text-sm">Loading leads...</p>
        ) : leads.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-stone-500">No leads yet.</p>
          </div>
        ) : (
          <div className="card p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-stone-800">
                  <th className="text-left px-4 py-3 text-stone-500 font-medium">Name</th>
                  <th className="text-left px-4 py-3 text-stone-500 font-medium">Type</th>
                  <th className="text-left px-4 py-3 text-stone-500 font-medium">Status</th>
                  <th className="text-left px-4 py-3 text-stone-500 font-medium">Source</th>
                  <th className="text-left px-4 py-3 text-stone-500 font-medium">Last Contact</th>
                </tr>
              </thead>
              <tbody>
                {leads.map(lead => (
                  <tr
                    key={lead.id}
                    onClick={() => setSelected(lead)}
                    className={cn(
                      'border-b border-stone-800/50 cursor-pointer transition-colors hover:bg-stone-800/50',
                      selected?.id === lead.id && 'bg-emerald-900/20'
                    )}
                  >
                    <td className="px-4 py-3 font-medium text-stone-100">
                      {lead.first_name} {lead.last_name}
                    </td>
                    <td className="px-4 py-3 text-stone-400 capitalize">
                      {lead.lead_type ?? '—'}
                    </td>
                    <td className="px-4 py-3">
                      <span className={cn('badge', STATUS_COLORS[lead.status] ?? 'bg-stone-700 text-stone-400')}>
                        {lead.status.replace('_', ' ')}
                      </span>
                      {lead.sequence_track === 'smartplan' && (
                        <span className="badge bg-amber-900/40 text-amber-400 ml-1" title="Follow-up owned by a KW Command SmartPlan">
                          SmartPlan
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-stone-400">
                      {lead.referrer ? `Ref: ${lead.referrer}` : (lead.source ?? '—')}
                    </td>
                    <td className="px-4 py-3 text-stone-400">
                      {timeAgo(lead.last_contact_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Drawer */}
      {selected && (
        <LeadDrawer lead={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  )
}
