const BASE = 'http://localhost:8080'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json()
}

// ── Agents ────────────────────────────────────────────────────────────────────
export const api = {
  agents: {
    status: () => request<AgentStatus[]>('/api/agents/status'),
    chat: (name: string, message: string) =>
      request<{ agent: string; response: string }>(`/api/agents/${name}/chat`, {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),
    briefing: () =>
      request<{ status: string; briefing: string }>('/api/agents/ceo/briefing', {
        method: 'POST',
      }),
  },

  leads: {
    list: () => request<Lead[]>('/api/leads'),
    get: (id: string) => request<Lead>(`/api/leads/${id}`),
    create: (data: Partial<Lead>) =>
      request<Lead>('/api/leads', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: Partial<Lead>) =>
      request<Lead>(`/api/leads/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  },

  listings: {
    list: (status?: string) =>
      request<{ count: number; listings: Listing[] }>(
        `/api/listings${status ? `?status=${status}` : ''}`
      ),
    create: (data: Partial<Listing>) =>
      request<Listing>('/api/listings', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: Partial<Listing>) =>
      request<Listing>(`/api/listings/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  },

  transactions: {
    list: () => request<{ count: number; transactions: Transaction[] }>('/api/transactions'),
    pipeline: () => request<Record<string, Transaction[]>>('/api/transactions/pipeline'),
    create: (data: Partial<Transaction>) =>
      request<Transaction>('/api/transactions', { method: 'POST', body: JSON.stringify(data) }),
    updateStatus: (id: string, data: Partial<Transaction>) =>
      request<Transaction>(`/api/transactions/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    drafts: {
      list: () => request<{ count: number; drafts: DraftMemory[] }>('/api/transactions/drafts'),
      save: (data: { draft_type: string; content: string; lead_id?: string; notes?: string }) =>
        request<{ key: string; status: string }>('/api/transactions/drafts', {
          method: 'POST',
          body: JSON.stringify(data),
        }),
      approve: (key: string) =>
        request<{ key: string; status: string; message: string }>(
          `/api/transactions/drafts/${key}/approve`,
          { method: 'PATCH' }
        ),
    },
  },

  content: {
    generate: (data: { description: string; content_type: string; title?: string; save?: boolean }) =>
      request<ContentGenerateResult>('/api/content/generate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    queue: (status?: string) =>
      request<{ count: number; items: ContentItem[] }>(
        `/api/content/queue${status ? `?status=${status}` : ''}`
      ),
    updateStatus: (id: string, status: string) =>
      request<{ id: string; status: string }>(`/api/content/queue/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }),
    weeklyPlan: () => request<{ plan: string }>('/api/content/plan'),
    chat: (message: string) =>
      request<{ response: string }>('/api/content/chat', {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),
    meets: {
      list: () => request<{ count: number; meets: Meet[] }>('/api/content/meets'),
      add: (data: Omit<Meet, 'id'>) =>
        request<Meet>('/api/content/meets', { method: 'POST', body: JSON.stringify(data) }),
      delete: (id: string) =>
        request<{ deleted: string }>(`/api/content/meets/${id}`, { method: 'DELETE' }),
    },
  },

  fba: {
    brands: {
      list: () => request<{ count: number; pending: number; approved: number; denied: number; brands: FBABrand[] }>('/api/fba/brands'),
      add: (data: { name: string; distributor: string; notes?: string }) =>
        request<FBABrand>('/api/fba/brands', { method: 'POST', body: JSON.stringify(data) }),
      updateStatus: (id: string, status: string, notes?: string) =>
        request<{ id: string; status: string }>(`/api/fba/brands/${id}/status`, {
          method: 'PATCH', body: JSON.stringify({ status, notes: notes ?? '' }),
        }),
      research: (id: string) =>
        request<{ id: string; research: string }>(`/api/fba/brands/${id}/research`, { method: 'POST' }),
      delete: (id: string) =>
        request<{ deleted: string }>(`/api/fba/brands/${id}`, { method: 'DELETE' }),
    },
    distributors: {
      list: () => request<{ count: number; distributors: FBADistributor[] }>('/api/fba/distributors'),
      add: (data: { name: string; contact?: string; website?: string; notes?: string }) =>
        request<FBADistributor>('/api/fba/distributors', { method: 'POST', body: JSON.stringify(data) }),
      updateStatus: (id: string, account_status: string) =>
        request<{ id: string; account_status: string }>(`/api/fba/distributors/${id}/status`, {
          method: 'PATCH', body: JSON.stringify({ account_status }),
        }),
      delete: (id: string) =>
        request<{ deleted: string }>(`/api/fba/distributors/${id}`, { method: 'DELETE' }),
      applicationEmail: (id: string) =>
        request<{ distributor: string; email: string }>(`/api/fba/distributors/${id}/email`, { method: 'POST' }),
    },
    setup: {
      checklist: () => request<{ checklist: string }>('/api/fba/setup/checklist'),
      starterDistributors: () => request<{ suggestions: string }>('/api/fba/setup/starter-distributors'),
    },
    discover: (distributor: string, category?: string) =>
      request<{ brands: string }>('/api/fba/discover', {
        method: 'POST', body: JSON.stringify({ distributor, category: category ?? '' }),
      }),
    prioritize: () => request<{ advice: string }>('/api/fba/prioritize', { method: 'POST' }),
    chat: (message: string) =>
      request<{ response: string }>('/api/fba/chat', { method: 'POST', body: JSON.stringify({ message }) }),
  },

  metricool: {
    nextSlot: () => request<{ next_slot: string; timezone: string }>('/api/metricool/next-slot'),
    schedule: (data: {
      video_id: string
      media_url: string
      networks?: string[]
      publish_datetime?: string
      caption_override?: string
    }) => request<{ scheduled: boolean; video_id: string; publish_datetime: string }>(
      '/api/metricool/schedule', { method: 'POST', body: JSON.stringify(data) }
    ),
    pullMetrics: (days_back?: number) =>
      request<{ pulled: number; updated: number; from_date: string; to_date: string }>(
        '/api/metricool/pull-metrics', { method: 'POST', body: JSON.stringify({ days_back: days_back ?? 30 }) }
      ),
  },

  videoTracker: {
    list: (category?: string) =>
      request<{ count: number; videos: VideoTrackerItem[] }>(
        `/api/video-tracker${category ? `?category=${category}` : ''}`
      ),
    create: (data: Partial<VideoTrackerItem>) =>
      request<VideoTrackerItem>('/api/video-tracker', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: Partial<VideoTrackerItem>) =>
      request<VideoTrackerItem>(`/api/video-tracker/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: string) =>
      request<{ deleted: string }>(`/api/video-tracker/${id}`, { method: 'DELETE' }),
  },

  realEstate: {
    social: (data: { content_type: string; platform: string; context?: string }) =>
      request<{ post: string; platform: string; content_type: string }>('/api/real-estate/social', {
        method: 'POST', body: JSON.stringify(data),
      }),
    neighborhoodCaptions: (data: { neighborhood: string; description: string; content_type?: string }) =>
      request<NeighborhoodCaptionResult>('/api/real-estate/neighborhood-captions', {
        method: 'POST', body: JSON.stringify(data),
      }),
  },

  tasks: {
    list: () => request<{ count: number; tasks: Task[] }>('/api/tasks'),
    overdue: () => request<{ count: number; tasks: Task[] }>('/api/tasks/overdue'),
    weekly: () => request<{ report: string }>('/api/tasks/weekly'),
    create: (req: string) =>
      request<Task>('/api/tasks', { method: 'POST', body: JSON.stringify({ request: req }) }),
    complete: (id: string) =>
      request<{ status: string }>(`/api/tasks/${id}/complete`, { method: 'PATCH' }),
    chat: (message: string) =>
      request<{ response: string }>('/api/tasks/chat', {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),
  },
}

// ── Types ─────────────────────────────────────────────────────────────────────
export interface AgentStatus {
  agent: string
  status: string
  memories?: number
  conversations?: number
  error?: string
}

export interface Lead {
  id: string
  first_name: string
  last_name: string
  email?: string
  phone?: string
  source?: string
  referrer?: string
  status: string
  lead_type?: string
  budget_min?: number
  budget_max?: number
  notes?: string
  last_contact_at?: string
  created_at: string
}

export interface Listing {
  id: string
  address: string
  city: string
  state: string
  zip?: string
  status: string
  listing_type?: string
  price?: number
  bedrooms?: number
  bathrooms?: number
  sqft?: number
  mls_number?: string
  notes?: string
  created_at: string
}

export interface Transaction {
  id: string
  lead_id?: string
  listing_id?: string
  status: string
  contract_price?: number
  closing_date?: string
  lone_wolf_id?: string
  notes?: string
  created_at: string
  leads?: { first_name: string; last_name: string }
  listings?: { address: string; city: string }
}

export interface DraftMemory {
  id: string
  key: string
  value: {
    draft_type: string
    content: string
    status: string
    lead_id?: string
    notes?: string
    created_at: string
    approved_at?: string
  }
}

export interface ContentGenerateResult {
  captions: {
    instagram?: string
    tiktok?: string
    youtube_title?: string
    youtube_description?: string
    facebook?: string
  }
  hashtags: string[]
  content_type: string
  generated_at: string
}

export interface ContentItem {
  id: string
  platform: string
  content_type: string
  athlete_name: string
  title?: string
  caption?: string
  hashtags?: string[]
  media_url?: string
  status: string
  scheduled_for?: string
  published_at?: string
  created_at: string
}

export interface FBABrand {
  id: string
  name: string
  distributor: string
  status: 'pending' | 'approved' | 'denied'
  date_submitted: string
  notes?: string
  research?: string
  researched_at?: string
  created_at: string
}

export interface FBADistributor {
  id: string
  name: string
  contact?: string
  website?: string
  notes?: string
  account_status: 'no_account' | 'applied' | 'active'
  created_at: string
}

export interface Meet {
  id: string
  date: string
  name: string
  location: string
  discipline: string
}

export interface NeighborhoodCaptionResult {
  captions: {
    instagram?: string
    tiktok?: string
    youtube_title?: string
    youtube_description?: string
    facebook?: string
    compliance_notes?: string
    kwp_qualifying?: string
  }
  hashtags: string[]
  neighborhood: string
  content_type: string
  funnel_CTA: string
  generated_at: string
}

export interface VideoTrackerItem {
  id: string
  category: 're' | 'gymnastics'
  title: string
  neighborhood?: string
  topic?: string
  film_status: 'not_filmed' | 'filmed'
  edit_status: 'raw' | 'edited' | 'approved'
  platforms: string[]
  caption_status: 'draft' | 'approved' | 'posted'
  scheduled_for?: string
  posted_at?: string
  ig_likes: number
  ig_comments: number
  ig_shares: number
  ig_saves: number
  tiktok_views: number
  tiktok_likes: number
  notes?: string
  created_at: string
}

export interface Task {
  id: string
  title: string
  description?: string
  status: string
  priority: string
  business_unit?: string
  due_date?: string
  created_at: string
}
