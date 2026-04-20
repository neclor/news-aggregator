import { useState } from 'react'
import type { SiteSelectors, SourceIn } from '../api/types'

interface Props {
  onSave: (data: SourceIn) => Promise<void>
  onCancel: () => void
}

const PLACEHOLDERS: Record<string, string> = {
  rss: 'https://example.com/rss.xml',
  telegram: '@channel or https://t.me/channel',
  site: 'https://example.com/news',
}

const EMPTY_SELECTORS: SiteSelectors = { articles: '', title: '', url: '', text: '' }

export default function SourceForm({ onSave, onCancel }: Props) {
  const [url, setUrl] = useState('')
  const [type, setType] = useState<SourceIn['type']>('rss')
  const [selectors, setSelectors] = useState<SiteSelectors>(EMPTY_SELECTORS)
  const [saving, setSaving] = useState(false)

  const setSel = (key: keyof SiteSelectors) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setSelectors(prev => ({ ...prev, [key]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    const data: SourceIn = { url: url.trim(), type }
    if (type === 'site') data.selectors = selectors
    await onSave(data)
    setSaving(false)
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      <div className="form-field">
        <label className="form-label">Type</label>
        <select
          className="form-input"
          value={type}
          onChange={e => { setType(e.target.value as SourceIn['type']); setUrl('') }}
        >
          <option value="rss">RSS</option>
          <option value="telegram">Telegram</option>
          <option value="site">Site</option>
        </select>
      </div>

      <div className="form-field">
        <label className="form-label">URL</label>
        <input
          type="text"
          className="form-input"
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder={PLACEHOLDERS[type]}
          required
          autoFocus
        />
      </div>

      {type === 'site' && (
        <>
          <div className="form-field">
            <label className="form-label">Articles selector</label>
            <input
              type="text"
              className="form-input"
              value={selectors.articles}
              onChange={setSel('articles')}
              placeholder="article.post"
              required
            />
          </div>
          <div className="form-field">
            <label className="form-label">Title selector</label>
            <input
              type="text"
              className="form-input"
              value={selectors.title}
              onChange={setSel('title')}
              placeholder="h2.title"
              required
            />
          </div>
          <div className="form-field">
            <label className="form-label">URL selector</label>
            <input
              type="text"
              className="form-input"
              value={selectors.url}
              onChange={setSel('url')}
              placeholder="a.title"
              required
            />
          </div>
          <div className="form-field">
            <label className="form-label">Text selector (optional)</label>
            <input
              type="text"
              className="form-input"
              value={selectors.text}
              onChange={setSel('text')}
              placeholder="p.excerpt"
            />
          </div>
        </>
      )}

      <div className="form-actions">
        <button type="button" className="btn btn-ghost" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Adding…' : 'Add Source'}
        </button>
      </div>
    </form>
  )
}
