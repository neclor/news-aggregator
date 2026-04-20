import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { Source, SourceIn } from '../api/types'
import Modal from '../components/Modal'
import SourceForm from '../components/SourceForm'

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([])
  const [adding, setAdding] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const load = async () => {
    try {
      setSources(await api.sources.list())
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => { load() }, [])

  const handleAdd = async (data: SourceIn) => {
    setFormError(null)
    try {
      await api.sources.create(data)
      setAdding(false)
      load()
    } catch (e) {
      setFormError(e instanceof Error ? e.message : 'Failed to add source')
    }
  }

  const handleDelete = async (source: Source) => {
    if (!confirm(`Delete source "${source.url}"?`)) return
    try {
      await api.sources.delete(source.url)
      load()
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to delete')
    }
  }

  const byType = (type: Source['type']) => sources.filter(s => s.type === type)

  return (
    <div className="page">
      <div className="page-header">
        <h2 className="page-title">Sources</h2>
        <button className="btn btn-primary" onClick={() => setAdding(true)}>
          + Add Source
        </button>
      </div>

      {sources.length === 0 ? (
        <div className="empty-state">No sources yet. Add one to start fetching news.</div>
      ) : (
        <div className="source-groups">
          {(['rss', 'telegram', 'site'] as const).map(type => {
            const group = byType(type)
            if (group.length === 0) return null
            return (
              <div key={type} className="source-group">
                <h3 className="source-group-title">{type.toUpperCase()}</h3>
                {group.map(source => (
                  <div key={source.url} className="source-row">
                    <span className="source-url">{source.url}</span>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(source)}
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )
          })}
        </div>
      )}

      {adding && (
        <Modal title="Add Source" onClose={() => { setAdding(false); setFormError(null) }}>
          {formError && <div className="alert alert-error">{formError}</div>}
          <SourceForm
            onSave={handleAdd}
            onCancel={() => { setAdding(false); setFormError(null) }}
          />
        </Modal>
      )}
    </div>
  )
}
