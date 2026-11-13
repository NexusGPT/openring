// The placed parts as words. A board can hold a hundred of them, so the list starts closed behind a find box:
// type a name or reference, or open the whole list. A row selects the object like the plan does.
import { useState } from 'react'
import { testId } from '../../contract'
import { matchesQuery, shows, type Mode, type Placement } from './model'

interface Props {
  placements: readonly Placement[]
  mode: Mode
  selected: string | null
  labelOf: (p: Placement) => string
  refOf: (p: Placement) => string
  onSelect: (p: Placement) => void
}

export function PlacedList({ placements, mode, selected, labelOf, refOf, onSelect }: Props) {
  const [q, setQ] = useState('')
  const onSide = placements.filter((p) => shows(mode, p.side))
  const found = onSide.filter((p) => matchesQuery(q, labelOf(p), refOf(p), p.name))
  const open = true
  const rows = open ? found : []
  return (
    <section className="bd-list" aria-labelledby="bd-list-h" data-testid={testId('board', 'placed-list')}>
      <div className="bd-row">
        <h2 className="label" id="bd-list-h">{`Parts on the board · ${onSide.length}`}</h2>
      </div>
      {onSide.length > 8 && (
        <input
          type="search" className="bd-find" value={q} onChange={(e) => setQ(e.target.value)}
          placeholder="Find a part by name or reference" aria-label="Find a part on the board" data-testid={testId('board', 'find')}
        />
      )}
      {open && rows.length === 0 ? (
        <p className="bd-none muted">{onSide.length === 0 ? 'Nothing is placed on this side.' : 'No part matches.'}</p>
      ) : (
        <ul>
          {rows.map((p) => (
            <li key={p.name}>
              <button
                type="button" aria-pressed={selected === p.name} data-testid={testId('board', 'placed-row')} data-part={p.name} data-side={p.side}
                onClick={() => onSelect(p)}
              >
                <span className="bd-ref">{refOf(p)}</span>
                <span className="bd-name">{labelOf(p)}</span>
                <span className="label">{p.side}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
