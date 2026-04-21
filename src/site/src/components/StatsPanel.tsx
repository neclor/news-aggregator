import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { FeedStats } from '../api/types'

interface Props {
  feedId: string
  refreshKey: number
}

const DAY_LABELS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

function last7Days(): string[] {
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (6 - i))
    return d.toISOString().slice(0, 10)
  })
}

export default function StatsPanel({ feedId, refreshKey }: Props) {
  const [stats, setStats] = useState<FeedStats | null>(null)

  useEffect(() => {
    api.news.stats(feedId).then(setStats).catch(() => null)
  }, [feedId, refreshKey])

  if (!stats || stats.total === 0) return null

  const days = last7Days()
  const byDay = Object.fromEntries(stats.daily.map(d => [d.date, d.count]))
  const maxDay = Math.max(...days.map(d => byDay[d] || 0), 1)
  const maxSrc = stats.by_source[0]?.count || 1

  return (
    <aside className="stats-panel">
      <div className="stats-section">
        <div className="stats-title">Overview</div>
        <div className="stats-row">
          <span>Total</span>
          <span className="stats-val">{stats.total}</span>
        </div>
        <div className="stats-row">
          <span>Unread</span>
          <span className="stats-val stats-accent">{stats.unread}</span>
        </div>
        <div className="stats-row">
          <span>Read</span>
          <span className="stats-val">{stats.read}</span>
        </div>
      </div>

      {stats.by_source.length > 1 && (
        <div className="stats-section">
          <div className="stats-title">By source</div>
          {stats.by_source.map(({ source, count }) => (
            <div key={source} className="stats-source-row">
              <div className="stats-source-name" title={source}>{source}</div>
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
              <div className="stats-day-label">{DAY_LABELS[new Date(day + 'T12:00:00').getDay()]}</div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}
