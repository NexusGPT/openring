import { testId, type PartsLine } from '../../contract'

/** One row per parts-list line of the case. A click selects the line's first part: the stage outlines it and its card opens. */
export function PartsList({ lines, selected, onSelect, classOf }: { lines: readonly PartsLine[]; selected: string | null; onSelect(id: string): void; classOf?(l: PartsLine): string | null }) {
  return (
    <ul className="cs-parts" data-testid={testId('case', 'parts-list')}>
      {lines.map((l) => {
        const id = l.part_ids[0]!
        const on = selected !== null && l.part_ids.includes(selected)
        const cls = classOf?.(l) ?? null
        return (
          <li key={`${l.bom}-${l.row}`} data-testid={testId('case', 'part-row')} data-part-id={id} data-class={cls ?? undefined} data-selected={on ? 'true' : undefined}>
            <button type="button" className="cs-part" aria-pressed={on} onClick={() => onSelect(id)}>
              <span className="cs-part-ref">{l.refs.join(' ')}</span>
              <span className="cs-part-name">{l.function ?? l.item}</span>
              {cls ? <span className="cs-part-class label">{cls}</span> : null}
              <span className="cs-part-qty">{l.quantity > 1 ? `×${l.quantity}` : ''}</span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}
