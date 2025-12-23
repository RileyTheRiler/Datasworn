import { useEffect, useMemo, useState } from 'react'
import api from '../utils/api'

const Pill = ({ label, active, onToggle }) => (
  <button
    onClick={onToggle}
    className={`px-3 py-1 rounded-full text-xs font-mono border transition-colors ${
      active ? 'bg-disco-cyan/20 border-disco-cyan text-disco-paper' : 'bg-black/40 border-disco-muted text-disco-muted'
    }`}
  >
    {label}
  </button>
)

const EntryCard = ({ entry }) => (
  <div className="p-3 bg-black/40 border border-disco-cyan/10 rounded-lg space-y-1">
    <div className="flex items-center justify-between text-xs uppercase tracking-wide text-disco-cyan/80 font-mono">
      <span>{entry.category}</span>
      <span>{entry.discovered ? '★ Discovered' : '○ Unconfirmed'}</span>
    </div>
    <h3 className="text-lg font-serif text-disco-paper">{entry.title}</h3>
    <p className="text-sm text-disco-muted leading-relaxed">{entry.summary}</p>
    <div className="flex flex-wrap gap-2 mt-2 text-[11px]">
      {entry.factions?.map(f => <span key={`f-${f}`} className="px-2 py-1 bg-disco-purple/20 text-disco-purple rounded">{f}</span>)}
      {entry.locations?.map(loc => <span key={`l-${loc}`} className="px-2 py-1 bg-disco-green/20 text-disco-green rounded">{loc}</span>)}
      {entry.items?.map(item => <span key={`i-${item}`} className="px-2 py-1 bg-disco-yellow/20 text-disco-yellow rounded">{item}</span>)}
    </div>
    {entry.callbacks?.length > 0 && (
      <div className="mt-2 text-xs text-disco-paper/70">
        <div className="font-mono text-disco-cyan/70 mb-1">Narrative callbacks</div>
        <ul className="list-disc list-inside space-y-1">
          {entry.callbacks.map((cb) => (
            <li key={`${entry.id}-${cb.trigger}`}>[{cb.trigger}] {cb.response}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)

const buildOptions = (entries, key) => {
  const set = new Set()
  entries.forEach((entry) => {
    entry[key]?.forEach((value) => set.add(value))
  })
  return Array.from(set)
}

export default function CodexBrowser({ visible, onClose }) {
  const [entries, setEntries] = useState([])
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({ factions: [], locations: [], items: [] })
  const [loading, setLoading] = useState(false)

  const fetchEntries = async () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (search) params.append('q', search)
    if (filters.factions.length) params.append('factions', filters.factions.join(','))
    if (filters.locations.length) params.append('locations', filters.locations.join(','))
    if (filters.items.length) params.append('items', filters.items.join(','))

    try {
      const data = await api.get(`/lore?${params.toString()}`)
      setEntries(data.entries || [])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (visible) {
      fetchEntries()
    }
  }, [visible])

  useEffect(() => {
    if (visible) {
      fetchEntries()
    }
  }, [search, filters])

  const factionOptions = useMemo(() => buildOptions(entries, 'factions'), [entries])
  const locationOptions = useMemo(() => buildOptions(entries, 'locations'), [entries])
  const itemOptions = useMemo(() => buildOptions(entries, 'items'), [entries])

  const toggleFilter = (key, value) => {
    setFilters((prev) => {
      const exists = prev[key].includes(value)
      const next = exists ? prev[key].filter((v) => v !== value) : [...prev[key], value]
      return { ...prev, [key]: next }
    })
  }

  if (!visible) return null

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 p-6 overflow-y-auto">
      <div className="max-w-5xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs uppercase text-disco-cyan/70 font-mono">Codex</div>
            <h2 className="text-3xl font-serif text-disco-paper">Lore Browser</h2>
          </div>
          <button onClick={onClose} className="px-3 py-1 text-sm font-mono text-disco-paper border border-disco-cyan/50 rounded">
            Close
          </button>
        </div>

        <div className="bg-black/50 border border-disco-cyan/10 p-4 rounded-lg shadow-lg space-y-4">
          <div className="flex flex-col gap-2 md:flex-row md:items-center md:gap-4">
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search entries..."
              className="flex-1 px-3 py-2 bg-black/40 border border-disco-cyan/30 text-disco-paper rounded focus:outline-none"
            />
            <span className="text-xs text-disco-muted font-mono">Filters stack and update automatically.</span>
          </div>

          <div className="grid md:grid-cols-3 gap-3 text-sm">
            <div className="space-y-2">
              <div className="text-xs uppercase text-disco-cyan/70 font-mono">Factions</div>
              <div className="flex gap-2 flex-wrap">
                {factionOptions.map((faction) => (
                  <Pill
                    key={faction}
                    label={faction}
                    active={filters.factions.includes(faction)}
                    onToggle={() => toggleFilter('factions', faction)}
                  />
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-xs uppercase text-disco-cyan/70 font-mono">Locations</div>
              <div className="flex gap-2 flex-wrap">
                {locationOptions.map((location) => (
                  <Pill
                    key={location}
                    label={location}
                    active={filters.locations.includes(location)}
                    onToggle={() => toggleFilter('locations', location)}
                  />
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-xs uppercase text-disco-cyan/70 font-mono">Items</div>
              <div className="flex gap-2 flex-wrap">
                {itemOptions.map((item) => (
                  <Pill
                    key={item}
                    label={item}
                    active={filters.items.includes(item)}
                    onToggle={() => toggleFilter('items', item)}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-disco-cyan font-mono">Loading entries...</div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {entries.map((entry) => (
              <EntryCard key={entry.id} entry={entry} />
            ))}
            {entries.length === 0 && (
              <div className="text-disco-muted text-sm">No entries match the current filters.</div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
