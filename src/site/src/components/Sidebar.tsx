import { useState } from 'react'
import type { Feed } from '../api/types'

type View = { kind: 'news'; feedId: string } | { kind: 'sources' }

interface Props {
  feeds: Feed[]
  view: View | null
  dark: boolean
  onSelectFeed: (id: string) => void
  onNewFeed: () => void
  onViewSources: () => void
  onReorder: (feeds: Feed[]) => void
  onToggleTheme: () => void
}

export default function Sidebar({ feeds, view, dark, onSelectFeed, onNewFeed, onViewSources, onReorder, onToggleTheme }: Props) {
  const [dragIdx, setDragIdx] = useState<number | null>(null)
  const [overIdx, setOverIdx] = useState<number | null>(null)

  const handleDrop = (targetIdx: number) => {
    if (dragIdx === null || dragIdx === targetIdx) {
      setDragIdx(null)
      setOverIdx(null)
      return
    }
    const reordered = [...feeds]
    const [moved] = reordered.splice(dragIdx, 1)
    reordered.splice(targetIdx, 0, moved)
    setDragIdx(null)
    setOverIdx(null)
    onReorder(reordered)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">News Aggregator</div>

      <div className="sidebar-feeds-section">
        <div className="sidebar-section-header">
          <span className="sidebar-section-label">Feeds</span>
          <button className="sidebar-add-btn" onClick={onNewFeed} title="New feed">+</button>
        </div>
        <ul className="sidebar-feeds">
          {feeds.map((feed, i) => (
            <li
              key={feed.id}
              draggable
              onDragStart={() => { setDragIdx(i); setOverIdx(i) }}
              onDragOver={e => { e.preventDefault(); setOverIdx(i) }}
              onDragEnd={() => { setDragIdx(null); setOverIdx(null) }}
              onDrop={() => handleDrop(i)}
              className={overIdx === i && dragIdx !== null && dragIdx !== i ? 'drag-over' : ''}
            >
              <button
                className={`sidebar-feed-item${view?.kind === 'news' && view.feedId === feed.id ? ' active' : ''}${dragIdx === i ? ' dragging' : ''}`}
                onClick={() => onSelectFeed(feed.id)}
              >
                {feed.name}
              </button>
            </li>
          ))}
          {feeds.length === 0 && (
            <li className="sidebar-empty">No feeds yet</li>
          )}
        </ul>
      </div>

      <div className="sidebar-bottom">
        <button
          className={`sidebar-nav-item ${view?.kind === 'sources' ? 'active' : ''}`}
          onClick={onViewSources}
        >
          <span className="sidebar-nav-icon">⊕</span>
          Sources
        </button>
        <button className="sidebar-nav-item sidebar-theme-btn" onClick={onToggleTheme}>
          <span className="sidebar-nav-icon">{dark ? '○' : '●'}</span>
          {dark ? 'Light' : 'Dark'}
        </button>
      </div>
    </aside>
  )
}
