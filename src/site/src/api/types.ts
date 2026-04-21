export interface Feed {
  id: string
  name: string
  sources: string[]
  keywords: string[]
  max_age_hours: number | null
}

export interface FeedIn {
  name: string
  sources: string[]
  keywords: string[]
  max_age_hours: number | null
}

export interface NewsItem {
  url: string
  source: string
  title: string
  text: string
  published_at: string
  author: string | null
  is_read: boolean
}

export interface FeedStats {
  total: number
  read: number
  unread: number
  by_source: { source: string; count: number }[]
  daily: { date: string; count: number }[]
}

export interface Source {
  url: string
  type: 'rss' | 'telegram' | 'site'
}

export interface SiteSelectors {
  articles: string
  title: string
  url: string
  text: string
}

export interface SourceIn {
  url: string
  type: 'rss' | 'telegram' | 'site'
  selectors?: SiteSelectors
}
