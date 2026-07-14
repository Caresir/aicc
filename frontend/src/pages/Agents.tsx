import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Send, Bot, Database, ChevronRight, ChevronDown } from 'lucide-react'
import { api } from '../lib/api'
import { cn } from '../lib/utils'

const AGENTS = [
  { id: 'real_estate',     label: 'Real Estate Assistant', desc: 'Leads, follow-ups, listings' },
  { id: 'ceo',             label: 'CEO Agent',             desc: 'Daily priorities, briefings' },
  { id: 'project_manager', label: 'Project Manager',       desc: 'Tasks, deadlines, blockers' },
]

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function Agents() {
  const [activeAgent, setActiveAgent] = useState(AGENTS[0].id)
  const [messages, setMessages] = useState<Record<string, Message[]>>({})
  const [input, setInput] = useState('')
  const [showMemory, setShowMemory] = useState(false)
  const [memoryKey, setMemoryKey] = useState('')
  const [memoryResult, setMemoryResult] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  const thread = messages[activeAgent] ?? []

  const { data: agentStatuses } = useQuery({
    queryKey: ['agents-status'],
    queryFn: api.agents.status,
    refetchInterval: 30000,
  })

  const statusFor = (id: string) =>
    agentStatuses?.find(a => a.agent === id)?.status ?? 'unknown'

  const chatMutation = useMutation({
    mutationFn: (message: string) => api.agents.chat(activeAgent, message),
    onSuccess: (data) => {
      setMessages(prev => ({
        ...prev,
        [activeAgent]: [...(prev[activeAgent] ?? []), { role: 'assistant', content: data.response }],
      }))
    },
  })

  const memoryMutation = useMutation({
    mutationFn: (key: string) =>
      fetch(`http://localhost:8080/api/agents/${activeAgent}/memory/${encodeURIComponent(key)}`)
        .then(r => r.json()),
    onSuccess: (data) => {
      setMemoryResult(JSON.stringify(data, null, 2))
    },
    onError: () => setMemoryResult('No memory found for that key.'),
  })

  const send = () => {
    const msg = input.trim()
    if (!msg || chatMutation.isPending) return
    setInput('')
    setMessages(prev => ({
      ...prev,
      [activeAgent]: [...(prev[activeAgent] ?? []), { role: 'user', content: msg }],
    }))
    chatMutation.mutate(msg)
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [thread])

  const agent = AGENTS.find(a => a.id === activeAgent)!
  const status = statusFor(activeAgent)

  return (
    <div className="flex h-screen">
      {/* Agent Selector */}
      <div className="w-52 shrink-0 border-r border-stone-800 p-3 space-y-1">
        <p className="text-stone-500 text-xs uppercase tracking-wide px-2 mb-3">AI Employees</p>
        {AGENTS.map(a => {
          const s = statusFor(a.id)
          return (
            <button
              key={a.id}
              onClick={() => { setActiveAgent(a.id); setShowMemory(false); setMemoryResult(null) }}
              className={cn(
                'w-full text-left px-3 py-2 rounded-lg transition-colors',
                activeAgent === a.id
                  ? 'bg-emerald-600/20 text-emerald-400'
                  : 'text-stone-400 hover:text-stone-100 hover:bg-stone-800'
              )}
            >
              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    'w-1.5 h-1.5 rounded-full shrink-0',
                    s === 'active' ? 'bg-emerald-500' : s === 'unknown' ? 'bg-stone-600' : 'bg-red-500'
                  )}
                />
                <p className="text-sm font-medium">{a.label}</p>
              </div>
              <p className="text-xs text-stone-500 mt-0.5 ml-3.5">{a.desc}</p>
            </button>
          )
        })}
      </div>

      {/* Chat + Memory Panel */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="px-6 py-4 border-b border-stone-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-600/20 rounded-lg">
              <Bot size={16} className="text-emerald-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <p className="font-semibold text-stone-100 text-sm">{agent.label}</p>
                <span
                  className={cn(
                    'text-xs px-1.5 py-0.5 rounded-full font-medium',
                    status === 'active'
                      ? 'bg-emerald-900/50 text-emerald-400'
                      : status === 'unknown'
                      ? 'bg-stone-800 text-stone-500'
                      : 'bg-red-900/50 text-red-400'
                  )}
                >
                  {status}
                </span>
              </div>
              <p className="text-stone-500 text-xs">{agent.desc}</p>
            </div>
          </div>
          <button
            onClick={() => { setShowMemory(v => !v); setMemoryResult(null) }}
            className={cn(
              'flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg transition-colors',
              showMemory ? 'bg-stone-700 text-stone-100' : 'btn-ghost text-stone-400'
            )}
          >
            <Database size={13} />
            Memory
            {showMemory ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </button>
        </div>

        {/* Memory Viewer (collapsible) */}
        {showMemory && (
          <div className="border-b border-stone-800 bg-stone-950 px-6 py-4">
            <p className="text-stone-500 text-xs uppercase tracking-wide mb-3">Memory Viewer</p>
            <div className="flex gap-2 mb-3">
              <input
                value={memoryKey}
                onChange={e => setMemoryKey(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && memoryMutation.mutate(memoryKey)}
                placeholder="Enter memory key (e.g. follow_up_draft)"
                className="flex-1 bg-stone-800 border border-stone-700 rounded-lg px-3 py-2 text-xs text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
              />
              <button
                onClick={() => memoryMutation.mutate(memoryKey)}
                disabled={!memoryKey || memoryMutation.isPending}
                className="btn-primary text-xs px-3"
              >
                Fetch
              </button>
            </div>
            {memoryMutation.isPending && (
              <p className="text-stone-500 text-xs">Fetching...</p>
            )}
            {memoryResult && (
              <pre className="bg-stone-900 border border-stone-800 rounded-lg p-3 text-xs text-stone-300 overflow-x-auto max-h-48 leading-relaxed">
                {memoryResult}
              </pre>
            )}
            <p className="text-stone-600 text-xs mt-2">
              Common keys: <span className="text-stone-500">briefing_history · follow_up_draft · lead_research · sequence_draft</span>
            </p>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {thread.length === 0 && (
            <div className="text-center py-16">
              <Bot size={32} className="text-stone-700 mx-auto mb-3" />
              <p className="text-stone-500 text-sm">Start a conversation with {agent.label}</p>
            </div>
          )}
          {thread.map((msg, i) => (
            <div key={i} className={cn('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
              <div
                className={cn(
                  'max-w-lg px-4 py-3 rounded-xl text-sm leading-relaxed whitespace-pre-wrap',
                  msg.role === 'user' ? 'bg-emerald-600 text-white' : 'bg-stone-800 text-stone-200'
                )}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {chatMutation.isPending && (
            <div className="flex justify-start">
              <div className="bg-stone-800 px-4 py-3 rounded-xl">
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

        {/* Input */}
        <div className="px-6 py-4 border-t border-stone-800">
          <div className="flex gap-3">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
              placeholder={`Message ${agent.label}...`}
              className="flex-1 bg-stone-800 border border-stone-700 rounded-lg px-4 py-2.5 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
            />
            <button onClick={send} disabled={chatMutation.isPending} className="btn-primary px-3">
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
