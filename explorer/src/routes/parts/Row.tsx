// One line of the list: part, maker, order code, price, evidence, open action. Click opens its card in place.
import { testId, type Files, type Parts, type PartsLine } from '../../contract'
import { PartCard } from '../../components/PartCard'
import type { AreaState, BannerSpec, PartNotes } from '../../contract'
import { hasCode, makerFiles } from './model'
import { fileUrl } from '../../data'

export interface RowProps {
  line: PartsLine
  group: 'ring' | 'case'
  selected: string | null
  onSelect: (id: string | null) => void
  legend: Parts['evidence_legend'] | null
  notes: PartNotes['notes'] | null
  files: Files | null
  areaState: AreaState | null
  banner: BannerSpec | null
}

/** First three refs, then "+N": a line of fourteen test pads must not squeeze its own name. */
const refsText = (l: PartsLine): string => {
  const shown = l.refs.slice(0, 3).join(' ')
  const more = l.refs.length > 3 ? ` +${l.refs.length - 3}` : ''
  return `${shown}${more}${l.quantity > 1 ? ` × ${l.quantity}` : ''}`
}

const base = (p: string): string => p.split('/').pop() ?? p

function DrawingFiles({ line, files }: { line: PartsLine; files: Files | null }) {
  const found = makerFiles(files, line)
  return (
    <p className="pt-drawing" data-testid={testId('parts', 'drawing-files')}>
      {found.length ? (
        <>
          <span className="label">Made to drawing</span>{' '}
          {found.map((f) => (
            <a key={f} href={fileUrl(f)} target="_blank" rel="noreferrer">{base(f)}</a>
          ))}
        </>
      ) : (
        <>
          <span className="label">Made to drawing</span> The maker file for this part is not made yet.
        </>
      )}
    </p>
  )
}

export function Row(p: RowProps) {
  const { line, group, selected } = p
  const open = selected !== null && line.part_ids.includes(selected)
  const first = line.part_ids[0] ?? ''
  const cardId = open && selected ? selected : first
  const evidence = line.evidence
  const meaning = evidence ? p.legend?.find((l) => l.code === evidence)?.meaning ?? evidence : null
  const body = `parts-card-${first.replace(/[^A-Za-z0-9]+/g, '-')}`
  return (
    <li className="pt-item" data-open={open || undefined}>
      <button
        type="button"
        className="pt-row"
        data-testid={testId('parts', group === 'case' ? 'case-row' : 'row')}
        data-part-id={first}
        data-group={group}
        aria-expanded={open}
        aria-controls={open ? body : undefined}
        onClick={() => p.onSelect(open ? null : first)}
      >
        <span className="pt-part">
          <span className="pt-name">{line.item}</span>
          <span className="pt-refs label">{refsText(line)}</span>
        </span>
        <span className="pt-maker">{line.maker ?? <span className="pt-none">no maker named</span>}</span>
        <span className="pt-code" data-testid={testId('parts', 'order-code')}>
          {hasCode(line) ? line.maker_part_number : <span className="pt-none">made to drawing</span>}
        </span>
        <span className="pt-price">{line.price ? line.price.raw : <span className="pt-none">no price yet</span>}</span>
        <span className="pt-ev label" title={meaning ?? undefined} data-evidence={evidence ?? undefined}>{evidence ?? 'none'}</span>
        <span className="pt-action" data-testid={testId('parts', 'open-action')}>
          {line.open_action ? (
            <>
              <span className="pt-open label">Open</span> {line.open_action}
            </>
          ) : null}
        </span>
      </button>
      {open ? (
        <div className="pt-card" id={body} data-testid={testId('parts', 'card-slot')}>
          {line.part_ids.length > 1 ? (
            <div className="pt-refpick" role="group" aria-label="Parts of this line">
              {line.part_ids.map((id, i) => (
                <button key={id} type="button" className="pt-ref" aria-pressed={id === cardId} data-testid={testId('parts', 'ref-chip')} onClick={() => p.onSelect(id)}>
                  {line.refs[i] ?? id}
                </button>
              ))}
            </div>
          ) : null}
          <PartCard route="parts" partId={cardId} line={line} note={p.notes?.[cardId] ?? null} legend={p.legend} files={p.files} areaState={p.areaState} banner={p.banner} />
          {madeToDrawingNote(line) ? <DrawingFiles line={line} files={p.files} /> : null}
        </div>
      ) : null}
    </li>
  )
}

const madeToDrawingNote = (l: PartsLine): boolean => !hasCode(l)
