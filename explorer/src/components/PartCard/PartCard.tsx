import './PartCard.css'
import { AREA_PILL, StateBanner, testId, type AreaState, type BannerSpec, type Files, type PartNotes, type PartsLine, type TestScope } from '../../contract'
import { ExactData } from './ExactData'
import { NO_LINE, evidenceMeaning, needsAttention, type Legend } from './model'

export interface PartCardProps {
  /** the route that hosts the card: it sets the test id ('<route>.part-card') */
  route: TestScope
  /** '<bom>:<ref>' */
  partId: string
  /** the parts line the id belongs to, or null when the object has no parts-list line */
  line: PartsLine | null
  /** the part-notes entry for the id, if any */
  note?: PartNotes['notes'][string] | null
  legend?: Legend | null
  files?: Files | null
  /** the state of the area this part belongs to; 'waiting on a supplier' lights the accent pill */
  areaState?: AreaState | null
  /** honest state of the record behind the card; a 'stale' banner dims the content, it stays on screen */
  banner?: BannerSpec | null
}

function Kv({ k, children }: { k: string; children: React.ReactNode }) {
  return (
    <>
      <dt>{k}</dt>
      <dd>{children}</dd>
    </>
  )
}

/** The card that explains one part in plain words first, exact data one click below. Text only, no HTML. */
export function PartCard({ route, partId, line, note, legend = null, files = null, areaState = null, banner = null }: PartCardProps) {
  const id = testId(route, 'part-card')
  const ref = partId.slice(partId.indexOf(':') + 1)
  const bom = partId.slice(0, partId.indexOf(':'))
  const heading = note?.what ?? line?.item ?? ref
  const attention = needsAttention(line, areaState)
  const meaning = line ? evidenceMeaning(line.evidence, legend) : null
  const dim = banner?.kind === 'stale'
  return (
    <article className="pc" data-testid={id} data-part-id={partId} data-attention={attention || undefined} data-stale={dim || undefined}>
      {banner && (
        <div className="pc-banner">
          <StateBanner route={route} spec={banner} />
        </div>
      )}
      <div className="pc-body">
        <div className="pc-lab">{`Part · ${ref}${bom ? ` · ${bom}` : ''}`}</div>
        <h3 className="pc-h">{heading}</h3>
        {note?.why && <p className="pc-plain">{note.why}</p>}
        {!line ? (
          <p className="pc-none" data-testid={testId(route, 'part-card-no-line')}>{NO_LINE}</p>
        ) : (
          <>
            <dl className="pc-kv">
              {line.size_mm && <Kv k="Size">{`${line.size_mm} mm`}</Kv>}
              {line.key_figures && <Kv k="Key figure">{line.key_figures}</Kv>}
              {line.quantity === 0 && <Kv k="How many">Not fitted (history only)</Kv>}
              {line.quantity > 1 && <Kv k="How many">{`${line.quantity} in the ring`}</Kv>}
              <Kv k="Order">
                {line.open_action ? <span>{`Open: ${line.open_action}`}</span> : line.maker_part_number ? <span>Order code is under Exact data</span> : <span>No order code yet</span>}
              </Kv>
              {attention && (
                <Kv k="Status">
                  <span className="pc-pill pc-pill-attn" data-testid={testId(route, 'part-card-status')}>{AREA_PILL['waiting on a supplier']}</span>
                </Kv>
              )}
              {meaning && (
                <Kv k="Evidence">
                  <span className="pc-pill" data-testid={testId(route, 'part-card-evidence')} data-evidence={line.evidence ?? undefined}>{meaning}</span>
                </Kv>
              )}
            </dl>
            <ExactData line={line} files={files} testid={id} />
          </>
        )}
      </div>
    </article>
  )
}
