import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(iso?: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

export function timeAgo(iso?: string | null): string {
  if (!iso) return 'never'
  const diff = Date.now() - new Date(iso).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return 'today'
  if (days === 1) return 'yesterday'
  return `${days}d ago`
}

export const PRIORITY_COLORS: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-400',
  high:     'bg-orange-500/20 text-orange-400',
  medium:   'bg-yellow-500/20 text-yellow-400',
  low:      'bg-stone-700 text-stone-400',
}

export const STATUS_COLORS: Record<string, string> = {
  new:            'bg-emerald-500/20 text-emerald-400',
  contacted:      'bg-blue-500/20 text-blue-400',
  qualified:      'bg-purple-500/20 text-purple-400',
  active:         'bg-emerald-500/20 text-emerald-400',
  under_contract: 'bg-amber-500/20 text-amber-400',
  closed:         'bg-stone-700 text-stone-400',
  lost:           'bg-red-500/20 text-red-400',
}
