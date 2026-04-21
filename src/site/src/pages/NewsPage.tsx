import { useState, useEffect, useCallback, useRef } from 'react'
import { api } from '../api/client'
import type { Feed, FeedIn, NewsItem } from '../api/types'
import Modal from '../components/Modal'
import FeedForm from '../components/FeedForm'
import StatsPanel from '../components/StatsPanel'

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60_000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

interface Props {
  feed: Feed
  onChanged: () => void
  onDeleted: () => void
}

export default function NewsPage({ feed, onChanged, onDeleted }: Props) {
  const [items, setItems] = useState<NewsItem[]>([])
  const [unreadOnly, setUnreadOnly] = useState(true)
  const [allTime, setAllTime] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [read, setRead] = useState<Set<string>>(new Set())
  const [fetching, setFetching] = useState(false)
  const [editing, setEditing] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [showSettings, setShowSettings] = useState(false)
  const [statsKey, setStatsKey] = useState(0)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!showSettings) return
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node))
        setShowSettings(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [showSettings])

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const loaded = await api.news.list(feed.id, unreadOnly, allTime, allTime ? 1000 : 200)
      setItems(loaded)
      setRead(new Set(loaded.filter(i => i.is_read).map(i => i.url)))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load')
    } finally {
      setLoading(false)
    }
  }, [feed.id, unreadOnly, allTime])

  useEffect(() => { load() }, [load])

  const markRead = async (url: string) => {
    try {
      await api.news.markRead(feed.id, url)
      setRead(prev => new Set(prev).add(url))
      setStatsKey(k => k + 1)
    } catch (e) {
      console.error(e)
    }
  }

  const markUnread = async (url: string) => {
    try {
      await api.news.markUnread(feed.id, url)
      setRead(prev => { const s = new Set(prev); s.delete(url); return s })
      setStatsKey(k => k + 1)
    } catch (e) {
      console.error(e)
    }
  }

  const markAllRead = async () => {
    try {
      await api.news.markAllRead(feed.id)
      setRead(new Set(items.map(i => i.url)))
      setStatsKey(k => k + 1)
    } catch (e) {
      console.error(e)
    }
  }

  const refresh = async () => {
    setFetching(true)
    try { await api.fetch() } catch (e) { console.error(e) } finally { setFetching(false) }
    await load()
  }

  const handleEdit = async (data: FeedIn) => {
    setFormError(null)
    try {
      await api.feeds.update(feed.id, data)
      setEditing(false)
      onChanged()
    } catch (e) {
      setFormError(e instanceof Error ? e.message : 'Failed to save')
    }
  }

  const handleDelete = async () => {
    if (!confirm(`Delete feed "${feed.name}"?`)) return
    try {
      await api.feeds.delete(feed.id)
      onDeleted()
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to delete')
    }
  }

  const visible = unreadOnly ? items.filter(i => !read.has(i.url)) : items
  const allRead = items.length > 0 && items.every(i => read.has(i.url))

  return (
    <div className="page">
      <div className="page-body">
        <div className="news-feed-col">

          <div className="page-header">
            <div className="page-header-info">
              <h2 className="page-title">{feed.name}</h2>
              {feed.keywords.length > 0 && (
                <p className="page-subtitle" title={feed.keywords.join(', ')}>
                  {feed.keywords.join(' · ')}
                </p>
              )}
            </div>
            <div className="page-actions">
              <label className="toggle-label">
                <input type="checkbox" checked={unreadOnly} onChange={e => setUnreadOnly(e.target.checked)} />
                Unread only
              </label>
              {feed.max_age_hours && (
                <label className="toggle-label">
                  <input type="checkbox" checked={allTime} onChange={e => setAllTime(e.target.checked)} />
                  All time
                </label>
              )}
              <button className="btn btn-secondary btn-sm" onClick={markAllRead} disabled={allRead || items.length === 0}>
                Mark all read
              </button>
              <button className="btn btn-ghost btn-sm" onClick={refresh} disabled={fetching}>
                {fetching ? '…' : '↻'}
              </button>
              <div className="dropdown" ref={dropdownRef}>
                <button className="btn btn-ghost btn-sm" onClick={() => setShowSettings(s => !s)}>⋯</button>
                {showSettings && (
                  <div className="dropdown-menu">
                    <button onClick={() => { setFormError(null); setEditing(true); setShowSettings(false) }}>Edit</button>
                    <button className="danger" onClick={handleDelete}>Delete</button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {error && <div className="alert alert-error">{error}</div>}
          {loading && <div className="loading">Loading…</div>}
          {!loading && visible.length === 0 && !error && (
            <div className="empty-state">
              {unreadOnly ? 'No unread items.' : 'No news yet — sources will be fetched soon.'}
            </div>
          )}

          <div className="news-feed">
            {visible.map(item => {
              const isRead = read.has(item.url)
              return (
                <article key={item.url} className={`news-card${isRead ? ' news-card--read' : ''}`}>
                  <div className="news-card-meta">
                    <span className="news-source">{item.source}</span>
                    <span className="news-sep">·</span>
                    <span className="news-time">{timeAgo(item.published_at)}</span>
                    {item.author && (
                      <>
                        <span className="news-sep">·</span>
                        <span className="news-author">{item.author}</span>
                      </>
                    )}
                  </div>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="news-title"
                    onClick={() => { if (!isRead) markRead(item.url) }}
                  >
                    {item.title || item.url}
                  </a>
                  {item.text && (
                    <p className="news-excerpt">
                      {item.text.length > 220 ? item.text.slice(0, 220) + '…' : item.text}
                    </p>
                  )}
                  <div className="news-card-actions">
                    {!isRead
                      ? <button className="news-mark-read" onClick={() => markRead(item.url)}>Mark as read</button>
                      : <button className="news-mark-unread" onClick={() => markUnread(item.url)}>Mark as unread</button>
                    }
                  </div>
                </article>
              )
            })}
          </div>

        </div>
        <StatsPanel feedId={feed.id} refreshKey={statsKey} />
      </div>

      {editing && (
        <Modal title={`Edit "${feed.name}"`} onClose={() => setEditing(false)}>
          {formError && <div className="alert alert-error">{formError}</div>}
          <FeedForm initial={feed} onSave={handleEdit} onCancel={() => setEditing(false)} />
        </Modal>
      )}
    </div>
  )
}
