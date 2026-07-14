import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, CheckCircle2, AlertCircle, BarChart2, X } from 'lucide-react'
import { api, type Task } from '../lib/api'
import { cn, formatDate, PRIORITY_COLORS } from '../lib/utils'

export default function Tasks() {
  const [input, setInput] = useState('')
  const [weeklyReport, setWeeklyReport] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: api.tasks.list,
  })

  const { data: overdue } = useQuery({
    queryKey: ['tasks-overdue'],
    queryFn: api.tasks.overdue,
  })

  const weeklyMutation = useMutation({
    mutationFn: api.tasks.weekly,
    onSuccess: (data) => setWeeklyReport(data.report),
  })

  const createMutation = useMutation({
    mutationFn: (req: string) => api.tasks.create(req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      setInput('')
    },
  })

  const completeMutation = useMutation({
    mutationFn: (id: string) => api.tasks.complete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  })

  const tasks = data?.tasks ?? []
  const overdueList = overdue?.tasks ?? []

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-xl font-bold text-stone-100">Tasks</h1>
          <p className="text-stone-500 text-sm">{tasks.length} open</p>
        </div>
        <button
          onClick={() => weeklyMutation.mutate()}
          disabled={weeklyMutation.isPending}
          className="btn-ghost border border-stone-700 flex items-center gap-2 text-sm"
        >
          <BarChart2 size={14} />
          {weeklyMutation.isPending ? 'Generating...' : 'Weekly Report'}
        </button>
      </div>

      {/* Weekly Report */}
      {weeklyReport && (
        <div className="card mb-6 border border-emerald-800/40 bg-emerald-950/10">
          <div className="flex items-center justify-between mb-3">
            <p className="text-emerald-400 text-xs font-medium uppercase tracking-wide">Weekly Status Report</p>
            <button onClick={() => setWeeklyReport(null)} className="btn-ghost p-1">
              <X size={14} />
            </button>
          </div>
          <pre className="text-stone-300 text-sm whitespace-pre-wrap leading-relaxed font-body">{weeklyReport}</pre>
        </div>
      )}

      {/* Add task */}
      <div className="card mb-6">
        <p className="text-stone-400 text-xs mb-2">Add a task in plain English</p>
        <div className="flex gap-3">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && input.trim() && createMutation.mutate(input)}
            placeholder='e.g. "Call Nadine about Cairnvillage title — high priority, due Friday"'
            className="flex-1 bg-stone-800 border border-stone-700 rounded-lg px-4 py-2.5 text-sm text-stone-100 placeholder-stone-500 focus:outline-none focus:border-emerald-600"
          />
          <button
            onClick={() => input.trim() && createMutation.mutate(input)}
            disabled={createMutation.isPending}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={14} />
            {createMutation.isPending ? 'Adding...' : 'Add'}
          </button>
        </div>
      </div>

      {/* Overdue */}
      {overdueList.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle size={14} className="text-red-400" />
            <p className="text-red-400 text-sm font-semibold">Overdue</p>
          </div>
          <div className="space-y-2">
            {overdueList.map(task => <TaskRow key={task.id} task={task} onComplete={completeMutation.mutate} />)}
          </div>
        </div>
      )}

      {/* Open tasks */}
      {isLoading ? (
        <p className="text-stone-500 text-sm">Loading tasks...</p>
      ) : tasks.length === 0 ? (
        <div className="card text-center py-12">
          <CheckCircle2 size={32} className="text-stone-700 mx-auto mb-3" />
          <p className="text-stone-500 text-sm">No open tasks. Clean slate.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {tasks.map(task => <TaskRow key={task.id} task={task} onComplete={completeMutation.mutate} />)}
        </div>
      )}
    </div>
  )
}

function TaskRow({ task, onComplete }: { task: Task; onComplete: (id: string) => void }) {
  return (
    <div className="card flex items-start gap-3 py-3">
      <button
        onClick={() => onComplete(task.id)}
        className="mt-0.5 text-stone-600 hover:text-emerald-500 transition-colors shrink-0"
      >
        <CheckCircle2 size={16} />
      </button>
      <div className="flex-1 min-w-0">
        <p className="text-stone-100 text-sm font-medium">{task.title}</p>
        {task.description && (
          <p className="text-stone-500 text-xs mt-0.5 truncate">{task.description}</p>
        )}
        <div className="flex items-center gap-2 mt-1">
          <span className={cn('badge text-xs', PRIORITY_COLORS[task.priority] ?? '')}>
            {task.priority}
          </span>
          {task.business_unit && (
            <span className="text-stone-600 text-xs capitalize">
              {task.business_unit.replace('_', ' ')}
            </span>
          )}
          {task.due_date && (
            <span className="text-stone-600 text-xs">
              Due {formatDate(task.due_date)}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
