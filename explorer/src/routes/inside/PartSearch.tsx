import { useId, useMemo, useState } from 'react'
import { testId } from '../../contract'
import type { PartsLine } from '../../contract'
import { searchParts, type Notes } from './model'

/** Search a part by words. Enter (or a click) selects; at most 8 results; the text is never a pattern. */
export function PartSearch({ lines, notes, onSelect, disabled }: {
  lines: readonly PartsLine[]
  notes: Notes | null
  onSelect(id: string): void
  disabled?: boolean
}) {
  const [text, setText] = useState('')
  const [active, setActive] = useState(0)
  const listId = useId()
  const hits = useMemo(() => searchParts(lines, notes, text), [lines, notes, text])
  const typed = text.trim().length > 0
  const choose = (i: number) => {
    const h = hits[i]
    if (!h) return
    onSelect(h.id)
    setText('')
    setActive(0)
  }
  return (
    <div className="in-search">
      <input
        type="search"
        value={text}
        disabled={disabled}
        placeholder="Search a part"
        aria-label="Search a part"
        role="combobox"
        aria-expanded={typed}
        aria-controls={listId}
        autoComplete="off"
        data-testid={testId('inside', 'search')}
        onChange={(e) => {
          setText(e.target.value)
          setActive(0)
        }}
        onKeyDown={(e) => {
          if (e.key === 'ArrowDown') {
            e.preventDefault()
            setActive((a) => Math.min(a + 1, Math.max(hits.length - 1, 0)))
          } else if (e.key === 'ArrowUp') {
            e.preventDefault()
            setActive((a) => Math.max(a - 1, 0))
          } else if (e.key === 'Enter') {
            e.preventDefault()
            choose(active)
          } else if (e.key === 'Escape') setText('')
        }}
      />
      {typed && (
        <ul id={listId} role="listbox" className="in-hits" data-testid={testId('inside', 'search-results')}>
          {hits.map((h, i) => (
            <li key={h.id} role="option" aria-selected={i === active}>
              <button
                type="button"
                data-testid={testId('inside', 'search-result')}
                data-part-id={h.id}
                data-active={i === active || undefined}
                onClick={() => choose(i)}
              >
                <span className="in-hit-item">{h.line.item}</span>
                <span className="label">{h.line.refs.join(', ')}</span>
              </button>
            </li>
          ))}
          {hits.length === 0 && (
            <li className="in-nothing" data-testid={testId('inside', 'search-empty')}>Nothing found. Try a part name, a reference or a maker.</li>
          )}
        </ul>
      )}
    </div>
  )
}
