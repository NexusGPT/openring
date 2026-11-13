import { Link } from '../../app/router'
import { testId } from '../../contract'
import { WORDS, type CaseBoard } from './model'

/** The parts a case board carries (reference, value, what it is), each opening its part card; and the way to the Board screen. */
export function BoardParts({ board, selected, onSelect }: { board: CaseBoard; selected: string | null; onSelect(id: string): void }) {
  return (
    <section className="cs-sec" data-testid={testId('case', 'board-parts')} data-board={board.key}>
      <h2 className="label">
        {`${WORDS.boardParts}: ${board.title.toLowerCase()}`}
        <span className="cs-count">{` · ${board.parts.length}`}</span>
      </h2>
      {board.picker ? (
        <Link className="cs-board-link" to={`/board?board=${encodeURIComponent(board.picker)}`} data-testid={testId('case', 'open-board')}>
          {WORDS.openBoard}
        </Link>
      ) : null}
      <ul className="cs-parts cs-board-list">
        {board.parts.map((p) => {
          const on = selected !== null && p.part_id === selected
          return (
            <li key={p.ref} data-testid={testId('case', 'board-part')} data-ref={p.ref} data-part-id={p.part_id ?? undefined}>
              {p.part_id ? (
                <button type="button" className="cs-part" aria-pressed={on} onClick={() => onSelect(p.part_id!)}>
                  <span className="cs-part-ref">{p.ref}</span>
                  <span className="cs-part-name">{p.what ?? p.value}</span>
                  <span className="cs-part-qty">{p.value}</span>
                </button>
              ) : (
                <div className="cs-part cs-part-plain">
                  <span className="cs-part-ref">{p.ref}</span>
                  <span className="cs-part-name">{p.value}</span>
                  <span className="cs-part-qty" />
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
