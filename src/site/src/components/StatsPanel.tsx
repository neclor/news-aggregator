import type { NewsItem } from '../api/types'

interface Props {
  items: NewsItem[]
  read: Set<string>
}

function dayLabel(iso: string): string {
  return ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'][new Date(iso).getDay()]
}

export default function StatsPanel({ items, read }: Props) {
  const total = items.length
  const unread = items.filter(i => !read.has(i.url)).length

  const bySource = items.reduce((acc, i) => {
    acc[i.source] = (acc[i.source] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  const sources = Object.entries(bySource).sort((a, b) => b[1] - a[1]).slice(0, 7)
  const maxSrc = sources[0]?.[1] || 1

  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - i))
    return d.toISOString().slice(0, 10)
  })
  const byDay = items.reduce((acc, i) => {
    const day = i.published_at.slice(0, 10)
    acc[day] = (acc[day] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  const maxDay = Math.max(...days.map(d => byDay[d] || 0), 1)

  if (total === 0) return null

  return (
    <aside className="stats-panel">
      <div className="stats-section">
        <div className="stats-title">Overview</div>
        <div className="stats-row">
          <span>Total</span>
          <span className="stats-val">{total}</span>
        </div>
        <div className="stats-row">
          <span>Unread</span>
          <span className="stats-val stats-accent">{unread}</span>
        </div>
        <div className="stats-row">
          <span>Read</span>
          <span className="stats-val">{total - unread}</span>
        </div>
      </div>

      {sources.length > 1 && (
        <div className="stats-section">
          <div className="stats-title">By source</div>
          {sources.map(([src, count]) => (
            <div key={src} className="stats-source-row">
              <div className="stats-source-name" title={src}>{src}</div>
              <div className="stats-bar-wrap">
                <div className="stats-bar" style={{ width: `${(count / maxSrc) * 100}%` }} />
              </div>
              <span className="stats-val">{count}</span>
            </div>
          ))}
        </div>
      )}

      <div className="stats-section">
        <div className="stats-title">Last 7 days</div>
        <div className="stats-days">
          {days.map(day => (
            <div key={day} className="stats-day">
              <div className="stats-day-bar-wrap">
                <div
                  className="stats-day-bar"
                  style={{ height: `${Math.max((byDay[day] || 0) / maxDay * 100, byDay[day] ? 8 : 0)}%` }}
                  title={`${byDay[day] || 0}`}
                />
              </div>
              <div className="stats-day-label">{dayLabel(day)}</div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}
