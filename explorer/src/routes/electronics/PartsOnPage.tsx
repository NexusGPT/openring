// The parts that sit on the shown page. A row selects the part: the stage highlights it and its card opens.
import { useRef } from 'react'
import { PartCard } from '../../components/PartCard'
import { testId, type AreaState, type Files, type Parts } from '../../contract'
import { useScrollIn } from './useScrollIn'
import { lineOfId, partLabel, refOf, type Notes } from './model'

interface Props {
  ids: readonly string[]
  selected: string | null
  parts: Parts | null
  notes: Notes | null
  files: Files | null
  areaState: AreaState | null
  onSelect: (id: string | null) => void
}

export function PartsOnPage({ ids, selected, parts, notes, files, areaState, onSelect }: Props) {
  const card = useRef<HTMLDivElement>(null)
  useScrollIn(card, selected)
  return (
    <section className="el-parts" aria-labelledby="el-parts-h" data-testid={testId('electronics', 'parts-list')}>
      <div className="el-sec-row">
        <h3 className="label" id="el-parts-h">{`Parts on this page · ${ids.length}`}</h3>
        {selected && <button type="button" className="el-close" onClick={() => onSelect(null)} data-testid={testId('electronics', 'card-close')}>Close card</button>}
      </div>
      {ids.length === 0 ? (
        <p className="el-none muted">No parts are listed for this page.</p>
      ) : (
        <ul>
          {ids.map((id) => (
            <li key={id}>
              <button
                type="button" aria-pressed={id === selected}
                data-testid={testId('electronics', 'part-row')} data-part={id}
                onClick={() => onSelect(id === selected ? null : id)}
              >
                <span className="el-ref">{refOf(id)}</span>
                <span className="el-part-name">{partLabel(id, parts, notes)}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
      {selected && (
        <div className="el-card" ref={card}>
          <PartCard
            route="electronics" partId={selected} line={lineOfId(parts, selected)} note={notes?.[selected] ?? null}
            legend={parts?.evidence_legend ?? null} files={files} areaState={areaState}
          />
        </div>
      )}
    </section>
  )
}
