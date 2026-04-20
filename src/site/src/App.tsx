import { useState, useEffect, useCallback } from 'react'
import { api } from './api/client'
import type { Feed, FeedIn } from './api/types'
import Sidebar from './components/Sidebar'
import Modal from './components/Modal'
import FeedForm from './components/FeedForm'
import NewsPage from './pages/NewsPage'
import SourcesPage from './pages/SourcesPage'

type View = { kind: 'news'; feedId: string } | { kind: 'sources' }

const ORDER_KEY = 'feed-order'

function applyOrder(feeds: Feed[]): Feed[] {
  const ids: string[] = JSON.parse(localStorage.getItem(ORDER_KEY) ?? '[]')
  if (!ids.length) return feeds
  const map = new Map(feeds.map(f => [f.id, f]))
  const ordered = ids.flatMap(id => map.has(id) ? [map.get(id)!] : [])
  const rest = feeds.filter(f => !ids.includes(f.id))
  return [...ordered, ...rest]
}

export default function App() {
  const [feeds, setFeeds] = useState<Feed[]>([])
  const [view, setView] = useState<View | null>(null)
  const [creating, setCreating] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [dark, setDark] = useState(() => {
    const stored = localStorage.getItem('theme')
    return stored ? stored === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light'
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  const loadFeeds = useCallback(async () => {
    try {
      setFeeds(applyOrder(await api.feeds.list()))
    } catch (e) {
      console.error(e)
    }
  }, [])

  useEffect(() => { loadFeeds() }, [loadFeeds])

  const activeFeed = view?.kind === 'news'
    ? feeds.find(f => f.id === view.feedId)
    : undefined

  const handleCreate = async (data: FeedIn) => {
    setFormError(null)
    try {
      const feed = await api.feeds.create(data)
      setCreating(false)
      await loadFeeds()
      setView({ kind: 'news', feedId: feed.id })
    } catch (e) {
      setFormError(e instanceof Error ? e.message : 'Failed to create feed')
    }
  }

  const handleFeedDeleted = async () => {
    await loadFeeds()
    setView(null)
  }

  const handleReorder = (reordered: Feed[]) => {
    setFeeds(reordered)
    localStorage.setItem(ORDER_KEY, JSON.stringify(reordered.map(f => f.id)))
  }

  return (
    <div className="layout">
      <Sidebar
        feeds={feeds}
        view={view}
        dark={dark}
        onSelectFeed={id => setView({ kind: 'news', feedId: id })}
        onNewFeed={() => { setFormError(null); setCreating(true) }}
        onViewSources={() => setView({ kind: 'sources' })}
        onReorder={handleReorder}
        onToggleTheme={() => setDark(d => !d)}
      />

      <main className="main">
        {view?.kind === 'news' && activeFeed && (
          <NewsPage
            feed={activeFeed}
            onChanged={loadFeeds}
            onDeleted={handleFeedDeleted}
          />
        )}
        {view?.kind === 'sources' && <SourcesPage />}
        {!view && (
          <div className="empty-state">Select a feed or create one</div>
        )}
      </main>

      {creating && (
        <Modal title="New Feed" onClose={() => setCreating(false)}>
          {formError && <div className="alert alert-error">{formError}</div>}
          <FeedForm
            onSave={handleCreate}
            onCancel={() => setCreating(false)}
          />
        </Modal>
      )}
    </div>
  )
}
