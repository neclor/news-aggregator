import type { Feed, FeedIn, FeedStats, NewsItem, Source, SourceIn } from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `${res.status} ${res.statusText}`)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

const body = (data: unknown) => JSON.stringify(data)

export const api = {
  feeds: {
    list: () =>
      request<Feed[]>('/feeds'),
    create: (data: FeedIn) =>
      request<Feed>('/feeds', { method: 'POST', body: body(data) }),
    update: (id: string, data: FeedIn) =>
      request<Feed>(`/feeds/${id}`, { method: 'PUT', body: body(data) }),
    delete: (id: string) =>
      request<void>(`/feeds/${id}`, { method: 'DELETE' }),
  },

  news: {
    list: (feedId: string, unreadOnly: boolean, allTime: boolean, limit: number) => {
      const params = new URLSearchParams({ limit: String(limit) })
      if (unreadOnly) params.set('unread_only', 'true')
      if (allTime) params.set('all_time', 'true')
      return request<NewsItem[]>(`/feeds/${feedId}/news?${params}`)
    },
    markRead: (feedId: string, newsUrl: string) =>
      request<void>(`/feeds/${feedId}/news/mark-read`, { method: 'POST', body: body({ url: newsUrl }) }),
    markUnread: (feedId: string, newsUrl: string) =>
      request<void>(`/feeds/${feedId}/news/mark-unread`, { method: 'POST', body: body({ url: newsUrl }) }),
    stats: (feedId: string) =>
      request<FeedStats>(`/feeds/${feedId}/news/stats`),
    markAllRead: (feedId: string) =>
      request<void>(`/feeds/${feedId}/news/read`, { method: 'POST' }),
  },

  fetch: () =>
    request<void>('/fetch', { method: 'POST' }),

  sources: {
    list: () =>
      request<Source[]>('/sources'),
    create: (data: SourceIn) =>
      request<Source>('/sources', { method: 'POST', body: body(data) }),
    delete: (url: string) =>
      request<void>(`/sources/${encodeURIComponent(url)}`, { method: 'DELETE' }),
  },
}
