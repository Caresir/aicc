import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Zap, Users, CheckSquare, Home, RefreshCw } from 'lucide-react'
import { api } from '../lib/api'
import { cn } from '../lib/utils'

export default function Dashboard() {
  const [briefing, setBriefing] = useState<string | null>(null)

  const { data: agents } = useQuery({
    queryKey: ['agents-status'],
    queryFn: api.agents.status,
    refetchInterval: 30000,
  })

  const { data: leads } = useQuery({
    queryKey: ['leads'],
    queryFn: api.leads.list,
  })

  const { data: tasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: api.tasks.list,
  })

  const briefingMutation = useMutation({
    mutationFn: api.agents.briefing,
    onSuccess: (data) => setBriefing(data.briefing),
  })

  const activeAgents = agents?.filter(a => a.status === 'active').length ?? 0
  const activeLeads = leads?.filter(l => !['closed','lost'].includes(l.status)).length ?? 0
  const openTasks = tasks?.count ?? 0

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-heading text-2xl font-bold text-stone-100">
          Good morning, Kareesa ☀️
        </h1>
        <p className="text-stone-400 text-sm mt-1">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard icon={<Users size={18} className="text-emerald-400" />} label="Active Leads" value={activeLeads} />
        <StatCard icon={<CheckSquare size={18} className="text-amber-400" />} label="Open Tasks" value={openTasks} />
        <StatCard icon={<Zap size={18} className="text-blue-400" />} label="Active Agents" value={activeAgents} />
      </div>

      {/* CEO Briefing */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading font-semibold text-stone-100">CEO Briefing</h2>
          <button
            onClick={() => briefingMutation.mutate()}
            disabled={briefingMutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <RefreshCw size={14} className={briefingMutation.isPending ? 'animate-spin' : ''} />
            {briefingMutation.isPending ? 'Generating...' : 'Run Briefing'}
          </button>
        </div>
        {briefing ? (
          <pre className="text-stone-300 text-sm whitespace-pre-wrap font-body leading-relaxed">
            {briefing}
          </pre>
        ) : (
          <p className="text-stone-500 text-sm">
            Click "Run Briefing" to generate today's priorities from live data.
          </p>
        )}
      </div>

      {/* Agent Status */}
      <div className="card">
        <h2 className="font-heading font-semibold text-stone-100 mb-4">Agent Status</h2>
        <div className="space-y-2">
          {agents?.map(agent => (
            <div key={agent.agent} className="flex items-center justify-between py-2 border-b border-stone-800 last:border-0">
              <div className="flex items-center gap-3">
                <div className={cn('w-2 h-2 rounded-full', agent.status === 'active' ? 'bg-emerald-500' : 'bg-red-500')} />
                <span className="text-stone-300 text-sm capitalize">{agent.agent.replace('_', ' ')}</span>
              </div>
              <div className="flex gap-4 text-xs text-stone-500">
                <span>{agent.memories ?? 0} memories</span>
                <span>{agent.conversations ?? 0} conversations</span>
              </div>
            </div>
          )) ?? (
            <p className="text-stone-500 text-sm">Loading agents...</p>
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="card flex items-center gap-4">
      <div className="p-2 bg-stone-800 rounded-lg">{icon}</div>
      <div>
        <p className="text-2xl font-heading font-bold text-stone-100">{value}</p>
        <p className="text-stone-500 text-xs">{label}</p>
      </div>
    </div>
  )
}
