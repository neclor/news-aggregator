import { useState } from 'react'
import type { Feed, FeedIn } from '../api/types'

interface Props {
  initial?: Feed
  onSave: (data: FeedIn) => Promise<void>
  onCancel: () => void
}

export default function FeedForm({ initial, onSave, onCancel }: Props) {
  const [name, setName] = useState(initial?.name ?? '')
  const [sources, setSources] = useState(initial?.sources.join('\n') ?? '')
  const [keywords, setKeywords] = useState(initial?.keywords.join('\n') ?? '')
  const [maxAge, setMaxAge] = useState(initial?.max_age_hours?.toString() ?? '')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    await onSave({
      name: name.trim(),
      sources: sources.split('\n').map(s => s.trim()).filter(Boolean),
      keywords: keywords.split('\n').map(s => s.trim()).filter(Boolean),
      max_age_hours: maxAge ? Number(maxAge) : null,
    })
    setSaving(false)
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      <div className="form-field">
        <label className="form-label">Name</label>
        <input
          type="text"
          className="form-input"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="My Feed"
          required
          autoFocus
        />
      </div>

      <div className="form-field">
        <label className="form-label">
          Sources
          <span className="form-hint"> — one URL per line</span>
        </label>
        <textarea
          className="form-input"
          value={sources}
          onChange={e => setSources(e.target.value)}
          placeholder={'https://example.com/rss.xml\n@telegram_channel'}
          rows={4}
        />
      </div>

      <div className="form-field">
        <label className="form-label">
          Keywords
          <span className="form-hint"> — one per line, empty = all items</span>
        </label>
        <textarea
          className="form-input"
          value={keywords}
          onChange={e => setKeywords(e.target.value)}
          placeholder={'technology\nscience'}
          rows={3}
        />
      </div>

      <div className="form-field">
        <label className="form-label">
          Max age (hours)
          <span className="form-hint"> — leave empty for no limit</span>
        </label>
        <input
          type="number"
          className="form-input form-input-sm"
          value={maxAge}
          onChange={e => setMaxAge(e.target.value)}
          min="0.1"
          step="0.5"
          placeholder="24"
        />
      </div>

      <div className="form-actions">
        <button type="button" className="btn btn-ghost" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>
    </form>
  )
}
